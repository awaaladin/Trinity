import pytest
from httpx import AsyncClient
from app.main import app
import hmac
import hashlib
import json

API_KEY = "your-secure-api-key"
HMAC_SECRET = "your-hmac-secret"

def generate_hmac_signature(secret_key: str, message: bytes) -> str:
    return hmac.new(secret_key.encode(), message, hashlib.sha256).hexdigest()

@pytest.mark.asyncio
async def test_initiate_payment_success():
    payload = {
        "order_id": "order123",
        "buyer_id": "buyer1",
        "seller_id": "seller1",
        "amount": 100.0,
        "payment_reference": "payref123"
    }
    body = json.dumps(payload).encode()
    signature = generate_hmac_signature(HMAC_SECRET, body)

    headers = {
        "x-api-key": API_KEY,
        "X-Signature": signature,
        "Content-Type": "application/json"
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/payments/initiate", headers=headers, json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == payload["order_id"]
    assert data["status"] == "pending_delivery_confirmation"

@pytest.mark.asyncio
async def test_initiate_payment_invalid_api_key():
    payload = {
        "order_id": "order123",
        "buyer_id": "buyer1",
        "seller_id": "seller1",
        "amount": 100.0,
        "payment_reference": "payref123"
    }
    body = json.dumps(payload).encode()
    signature = generate_hmac_signature(HMAC_SECRET, body)

    headers = {
        "x-api-key": "wrong-api-key",
        "X-Signature": signature,
        "Content-Type": "application/json"
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/payments/initiate", headers=headers, json=payload)
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_initiate_payment_invalid_hmac():
    payload = {
        "order_id": "order123",
        "buyer_id": "buyer1",
        "seller_id": "seller1",
        "amount": 100.0,
        "payment_reference": "payref123"
    }
    headers = {
        "x-api-key": API_KEY,
        "X-Signature": "invalidsignature",
        "Content-Type": "application/json"
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/payments/initiate", headers=headers, json=payload)
    
    assert response.status_code == 401
