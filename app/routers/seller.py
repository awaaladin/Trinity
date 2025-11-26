from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import schemas, crud
from app.dependencies import get_api_key, verify_hmac
from app.database import get_db

router = APIRouter(prefix="/seller", tags=["seller"])

@router.get("/orders/{seller_id}", response_model=List[schemas.OrderOut], dependencies=[Depends(get_api_key), Depends(verify_hmac)])
async def seller_orders(seller_id: str, db: AsyncSession = Depends(get_db)):
    orders = await crud.get_orders_by_seller(db, seller_id)
    return orders
