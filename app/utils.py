import hmac
import hashlib
import time
import logging
from fastapi import HTTPException, Request

# Configure logger
logger = logging.getLogger("trinity")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# In-memory nonce store - replace with Redis or DB in production for persistence and TTL
_used_nonces = set()

def verify_hmac_signature(secret_key: str, message: bytes, signature: str):
    """
    Verify HMAC SHA256 signature of the message using the secret key.
    Raise HTTPException if verification fails.
    """
    computed_hmac = hmac.new(secret_key.encode(), message, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed_hmac, signature):
        logger.warning(f"HMAC verification failed. Provided: {signature}, Computed: {computed_hmac}")
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")
    logger.info("HMAC signature verification succeeded")

def verify_hmac(
    secret_key: str,
    data: str,
    provided_signature: str,
    timestamp: int,
    nonce: str,
    tolerance_seconds: int = 300,  # 5 minutes
):
    """
    Verify request freshness and replay attack prevention using timestamp and nonce,
    then verify HMAC signature over (data + timestamp + nonce).
    """
    now = int(time.time())

    # Check timestamp freshness
    if abs(now - timestamp) > tolerance_seconds:
        logger.warning(f"Request timestamp {timestamp} outside allowed range. Current time: {now}")
        raise HTTPException(status_code=400, detail="Request timestamp outside allowed range")

    # Check nonce uniqueness (replay attack protection)
    if nonce in _used_nonces:
        logger.warning(f"Replay attack detected: nonce {nonce} already used")
        raise HTTPException(status_code=400, detail="Replay attack detected: nonce already used")
    _used_nonces.add(nonce)
    # Optional: implement TTL for _used_nonces to prevent memory bloat

    # Construct message to sign
    message = f"{data}{timestamp}{nonce}".encode()

    # Verify signature
    verify_hmac_signature(secret_key, message, provided_signature)

async def verify_request_hmac(request: Request, secret_key: str):
    """
    Extract headers and body from the request, then perform HMAC verification,
    timestamp freshness, and nonce replay protection.
    Expects headers:
      - X-Signature: HMAC signature
      - X-Timestamp: request timestamp (int)
      - X-Nonce: unique nonce string
    """
    signature = request.headers.get("X-Signature")
    if not signature:
        logger.warning("Missing X-Signature header")
        raise HTTPException(status_code=401, detail="Missing X-Signature header")

    timestamp_header = request.headers.get("X-Timestamp")
    nonce = request.headers.get("X-Nonce")

    if not timestamp_header or not nonce:
        logger.warning("Missing X-Timestamp or X-Nonce header")
        raise HTTPException(status_code=400, detail="Missing required headers")

    try:
        timestamp = int(timestamp_header)
    except ValueError:
        logger.warning(f"Invalid X-Timestamp header value: {timestamp_header}")
        raise HTTPException(status_code=400, detail="Invalid timestamp format")

    body_bytes = await request.body()
    data_str = body_bytes.decode()  # assuming UTF-8; adjust if needed

    # Perform full HMAC verification with replay and timestamp checks
    verify_hmac(secret_key, data_str, signature, timestamp, nonce)
