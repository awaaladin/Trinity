from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import DeliveryConfirmSchema
from app.dependencies import get_api_key, verify_hmac
from app.database import get_db
from app import crud

router = APIRouter(prefix="/delivery", tags=["delivery"])

@router.post("/confirm", dependencies=[Depends(get_api_key), Depends(verify_hmac)])
async def confirm_delivery(delivery_info: DeliveryConfirmSchema, db: AsyncSession = Depends(get_db)):
    order = await crud.get_order_by_id(db, delivery_info.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "pending_delivery_confirmation":
        raise HTTPException(status_code=400, detail="Order not pending delivery confirmation")

    # Transfer funds to seller
    success = await crud.transfer_to_seller(order.seller_id, order.amount)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to transfer funds to seller")

    updated_order = await crud.update_order_status(db, order.order_id, "delivered")
    return {"message": "Delivery confirmed and funds released", "order_id": updated_order.order_id}
