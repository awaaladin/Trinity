import os
import secrets
from datetime import datetime

API_KEY = secrets.token_urlsafe(32)  # 256-bit key
created = datetime.utcnow().isoformat()

print(f"API Key: {API_KEY}")
print(f"Store this securely. Created at {created}")
