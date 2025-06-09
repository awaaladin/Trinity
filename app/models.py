from sqlalchemy import Column, String, Float, DateTime, Enum, func
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class OrderStatus(str, enum.Enum):
    payment_pending = "payment_pending"
    pending_delivery_confirmation = "pending_delivery_confirmation"
    delivered = "delivered"
    refunded = "refunded"
    failed = "failed"

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(String, primary_key=True, index=True)
    buyer_id = Column(String, index=True, nullable=False)
    seller_id = Column(String, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.payment_pending, nullable=False)
    payment_reference = Column(String, unique=True, nullable=False)
    delivery_reference = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
