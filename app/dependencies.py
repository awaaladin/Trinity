import os
from fastapi import Security, Header, HTTPException, Request, Depends
from fastapi.security.api_key import APIKeyHeader
from app.utils import verify_request_hmac as verify_request_hmac_util  # ensure this is implemented
from app.config import settings

# Load from environment (recommended for production)
TRINITY_API_KEY = settings.API_KEY
HMAC_SECRET = os.getenv("HMAC_SECRET", "your-hmac-secret")

# API Key Header definition
api_key_header = APIKeyHeader(name="X-API-Key")

# Security dependency: API Key validation via fastapi.security
async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != TRINITY_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# Alternative Header-based API Key validation
async def get_api_key_header(x_api_key: str = Header(...)):
    if x_api_key != TRINITY_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

# HMAC verification dependency
async def verify_hmac(request: Request):
    await verify_request_hmac_util(request, HMAC_SECRET)
