from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_api_key
import os
import sendgrid
from sendgrid.helpers.mail import Mail

router = APIRouter(prefix="/notifications", tags=["notifications"])

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL") or "no-reply@trinityapp.com"

@router.post("/notify_seller")
async def notify_seller(order_id: str, message: str, api_key: str = Depends(get_api_key)):
    if not SENDGRID_API_KEY:
        raise HTTPException(status_code=500, detail="Email service not configured")

    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    mail = Mail(
        from_email=FROM_EMAIL,
        to_emails="seller@example.com",  # Replace with real seller email lookup
        subject=f"Order {order_id} Notification",
        plain_text_content=message,
    )
    try:
        response = sg.send(mail)
        if response.status_code >= 400:
            raise HTTPException(status_code=500, detail="Failed to send email")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email error: {str(e)}")

    return {"message": f"Notification sent to seller for order {order_id}"}
