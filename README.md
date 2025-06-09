# Trinity Payment Escrow API

Trinity is a secure payment escrow backend built with FastAPI where buyer funds are deducted immediately and released to seller only upon delivery confirmation.

---

## Features

- Secure payment initiation with HMAC request verification
- Atomic order and transaction management
- Delivery confirmation triggers fund release
- API key protection on all endpoints
- Logging of all critical operations

---

## Setup

1. Clone repo and create venv

   ```bash
   python -m venv venv
   source venv/bin/activate   # or `venv\Scripts\activate` on Windows
## Security & Deployment Notes

- Always deploy behind HTTPS to protect API keys and HMAC secrets in transit.
- Use environment variables or a secret manager for all sensitive keys.
- Implement replay attack protections by validating timestamps and nonces.
- Use rate limiting middleware to prevent abuse.
- Log all critical transactions and monitor logs regularly.
- Rotate API keys periodically and revoke compromised keys immediately.
- Store notification service API keys (e.g., SendGrid) securely.

---

## Production Deployment

- Always run behind a secure HTTPS reverse proxy (e.g., Nginx, Caddy).
- Use a production server:

  ```powershell
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers
  ```
- Set all secrets (API_KEY, HMAC_SECRET, DATABASE_URL, etc.) as environment variables, not in code.
- Use a distributed cache (e.g., Redis) for rate limiting and nonce storage if running multiple instances.
- Set `allow_origins` in CORS middleware to your real frontend domain(s).
- Monitor logs and rotate them regularly.
- Run Alembic migrations before starting the app:

  ```powershell
  alembic upgrade head
  ```

- For best security, review all dependencies for vulnerabilities and keep them up to date.
