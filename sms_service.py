import os
import logging
from datetime import datetime

logger = logging.getLogger("sms_service")

# Optional Twilio config
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+18005550199")

def send_sms_alert(to_phone: str, recipient_name: str, message_type: str, body_text: str) -> dict:
    """
    Sends SMS alert via Twilio if configured, or simulates delivery for local dev environment.
    Supports Animal Feed alerts, Claim OTPs, and Provider Reminders.
    """
    timestamp = datetime.utcnow().isoformat()
    
    # Try Twilio if credentials are valid
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and len(TWILIO_ACCOUNT_SID) > 10:
        try:
            from twilio.rest import Client
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=body_text,
                from_=TWILIO_PHONE_NUMBER,
                to=to_phone
            )
            return {
                "status": "sent",
                "provider": "Twilio",
                "sid": message.sid,
                "recipient_phone": to_phone,
                "recipient_name": recipient_name,
                "message_type": message_type,
                "content": body_text,
                "timestamp": timestamp
            }
        except Exception as e:
            logger.warning(f"Twilio SMS delivery failed, falling back to simulator: {str(e)}")

    # Dev Simulator Fallback
    logger.info(f"[SMS SIMULATOR] To: {recipient_name} ({to_phone}) | Type: {message_type} | Body: {body_text}")
    return {
        "status": "delivered_simulated",
        "provider": "ZeroWaste SMS Engine (Dev Simulator)",
        "recipient_phone": to_phone,
        "recipient_name": recipient_name,
        "message_type": message_type,
        "content": body_text,
        "timestamp": timestamp
    }
