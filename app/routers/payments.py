from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import PaymentInitiate, PaymentResponse
from app.dependencies import get_api_key, verify_hmac
from app.database import get_db
from app import crud

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/initiate", dependencies=[Depends(get_api_key), Depends(verify_hmac)])
async def initiate_payment(data: PaymentInitiate, db: AsyncSession = Depends(get_db)):
    # Debit buyer's account
    success = await crud.debit_buyer_account(data.buyer_id, data.amount)
    if not success:
        raise HTTPException(status_code=400, detail="Insufficient funds or payment failed")

    # Create order with pending delivery confirmation status
    order = await crud.create_order(
        db=db,
        order_id=data.order_id,
        buyer_id=data.buyer_id,
        seller_id=data.seller_id,
        amount=data.amount,
        payment_reference=data.payment_reference,
        status="pending_delivery_confirmation"
    )
    return PaymentResponse(order_id=order.order_id, status=order.status)
