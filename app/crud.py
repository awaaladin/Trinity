import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app import models

logger = logging.getLogger("trinity")

async def debit_buyer_and_create_order(db: AsyncSession, buyer_id: str, order_data: dict):
    """
    Debit buyer's balance and create a new order with 'pending_delivery_confirmation' status.
    Returns the created order or False if insufficient balance.
    """
    try:
        async with db.begin():  # start transaction block
            # Fetch buyer account
            buyer_account = await db.get(models.UserAccount, buyer_id)
            if buyer_account is None:
                logger.warning(f"Buyer account {buyer_id} not found")
                return False

            if buyer_account.balance < order_data['amount']:
                logger.warning(f"Buyer {buyer_id} has insufficient balance for amount {order_data['amount']}")
                return False

            # Debit buyer's balance
            buyer_account.balance -= order_data['amount']
            db.add(buyer_account)

            # Create order
            new_order = models.Order(
                **order_data,
                status="pending_delivery_confirmation"
            )
            db.add(new_order)

        # Transaction committed automatically here
        logger.info(f"Order created with ID {new_order.order_id} and buyer {buyer_id} debited {order_data['amount']}")
        return new_order

    except SQLAlchemyError as e:
        logger.error(f"Error in debit_buyer_and_create_order: {str(e)}")
        await db.rollback()
        raise

async def debit_buyer_account(buyer_id: str, amount: float) -> bool:
    logger.info(f"Debiting buyer {buyer_id} amount {amount}")
    # TODO: Real payment gateway integration
    return True

async def transfer_to_seller(seller_id: str, amount: float) -> bool:
    logger.info(f"Transferring amount {amount} to seller {seller_id}")
    # TODO: Real payment gateway integration
    return True

async def create_order(db: AsyncSession, order_id: str, buyer_id: str, seller_id: str, amount: float, payment_reference: str, status: str):
    try:
        order = models.Order(
            order_id=order_id,
            buyer_id=buyer_id,
            seller_id=seller_id,
            amount=amount,
            payment_reference=payment_reference,
            status=status
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        logger.info(f"Order created: {order_id} with status {status}")
        return order
    except SQLAlchemyError as e:
        logger.error(f"Failed to create order {order_id}: {str(e)}")
        await db.rollback()
        raise

async def get_order_by_id(db: AsyncSession, order_id: str):
    result = await db.execute(select(models.Order).where(models.Order.order_id == order_id))
    return result.scalars().first()

async def update_order_status(db: AsyncSession, order_id: str, status: str):
    try:
        order = await get_order_by_id(db, order_id)
        if order:
            order.status = status
            await db.commit()
            await db.refresh(order)
            logger.info(f"Order {order_id} status updated to {status}")
            return order
        else:
            logger.warning(f"Order {order_id} not found for status update")
            return None
    except SQLAlchemyError as e:
        logger.error(f"Failed to update order {order_id} status: {str(e)}")
        await db.rollback()
        raise
