import logging
import time
import os
from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Configure logging: file + console with timestamp, level, message
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests=100, window_seconds=60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        window_start = now - self.window_seconds

        # Cleanup old timestamps to keep only those inside current window
        timestamps = self.clients.get(client_ip, [])
        timestamps = [ts for ts in timestamps if ts > window_start]

        if len(timestamps) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for IP {client_ip}")
            raise HTTPException(status_code=429, detail="Too many requests")

        timestamps.append(now)
        self.clients[client_ip] = timestamps

        response = await call_next(request)
        return response

# Determine if docs should be enabled
ENV = os.getenv("ENV", "development")
if ENV == "production":
    docs_url = None
    redoc_url = None
    openapi_url = None
else:
    docs_url = "/docs"
    redoc_url = "/redoc"
    openapi_url = "/openapi.json"

# Initialize FastAPI app
app = FastAPI(
    title="Trinity Payment Escrow API",
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url
)

# CORS: allow only trusted origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # TODO: set real frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware: max 60 requests per 60 seconds per IP
app.add_middleware(RateLimiterMiddleware, max_requests=60, window_seconds=60)

@app.on_event("startup")
async def startup():
    logger.info("Trinity Escrow API starting up...")
    # Skip DB table creation on serverless - use migrations instead
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    logger.info("API ready")


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500, 
        content={"detail": "Internal server error"}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    logger.warning(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code, 
        content={"detail": exc.detail}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Trinity Escrow API"}


# Include routers with lazy import to avoid startup issues
try:
    from app.routers import payments, delivery, notifications
    app.include_router(payments.router)
    app.include_router(delivery.router)
    app.include_router(notifications.router)
except ImportError as e:
    logger.warning(f"Router import failed: {e}")
except Exception as e:
    logger.error(f"Failed to include routers: {e}")
