from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class OrderStatus(str, Enum):
    payment_pending = "payment_pending"
    pending_delivery_confirmation = "pending_delivery_confirmation"
    delivered = "delivered"
    refunded = "refunded"
    failed = "failed"

class PaymentInitiate(BaseModel):
    order_id: str
    buyer_id: str
    seller_id: str
    amount: float = Field(gt=0)
    payment_reference: str

class PaymentResponse(BaseModel):
    order_id: str
    status: OrderStatus

class DeliveryConfirmSchema(BaseModel):
    order_id: str
    delivery_reference: str
