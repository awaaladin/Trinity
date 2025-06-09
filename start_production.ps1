# Set production environment variables
$env:ENV = "production"
$env:DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/trinitydb"  # Change this to your production DB URL
$env:API_KEY = "your-production-api-key"  # Change this
$env:HMAC_SECRET = "your-production-hmac-secret"  # Change this

# Run migrations
Write-Host "Running database migrations..."
alembic upgrade head

# Start the server with production settings
# 4 workers (2x CPU cores + 1 is recommended)
# Only accept connections from localhost if behind a reverse proxy
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4 --proxy-headers --forwarded-allow-ips='*' --no-access-log
