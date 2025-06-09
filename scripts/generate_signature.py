import hmac
import hashlib
import time
import json
import os

# Replace with the same data you're sending in Postman
data = {
    "order_id": "order123",
    "buyer_id": "buyer1",
    "seller_id": "seller1",
    "amount": 100.0,
    "payment_reference": "ref001"
}

body = json.dumps(data)
timestamp = str(int(time.time()))
nonce = "abc123"  # You can make this random if you want

# This must match your .env HMAC secret
HMAC_SECRET = "your-hmac-secret"  # Replace with your real secret

message = body + timestamp + nonce
signature = hmac.new(HMAC_SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()

print("Timestamp:", timestamp)
print("Nonce:", nonce)
print("Signature:", signature)
