import os
import logging
from datetime import datetime

logger = logging.getLogger("whatsapp_service")

# Optional WhatsApp Config (via Twilio or Meta WhatsApp Cloud API)
WHATSAPP_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
WHATSAPP_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
WHATSAPP_SENDER_NUMBER = os.getenv("WHATSAPP_SENDER_NUMBER", "whatsapp:+14155238886")

def send_whatsapp_message(to_phone: str, recipient_name: str, message_type: str, body_text: str) -> dict:
    """
    Sends WhatsApp message via WhatsApp Cloud API / Twilio WhatsApp if configured,
    or generates an interactive dev simulated message.
    """
    timestamp = datetime.utcnow().isoformat()
    formatted_to = to_phone if to_phone.startswith("whatsapp:") else f"whatsapp:{to_phone}"

    if WHATSAPP_ACCOUNT_SID and WHATSAPP_AUTH_TOKEN and len(WHATSAPP_ACCOUNT_SID) > 10:
        try:
            from twilio.rest import Client
            client = Client(WHATSAPP_ACCOUNT_SID, WHATSAPP_AUTH_TOKEN)
            message = client.messages.create(
                body=body_text,
                from_=WHATSAPP_SENDER_NUMBER,
                to=formatted_to
            )
            return {
                "status": "sent",
                "provider": "WhatsApp Cloud API",
                "sid": message.sid,
                "recipient_phone": to_phone,
                "recipient_name": recipient_name,
                "message_type": message_type,
                "content": body_text,
                "timestamp": timestamp
            }
        except Exception as e:
            logger.warning(f"WhatsApp Cloud API delivery failed, falling back to simulator: {str(e)}")

    logger.info(f"[WHATSAPP SIMULATOR] To: {recipient_name} ({to_phone}) | Body: {body_text}")
    return {
        "status": "delivered_whatsapp_simulated",
        "provider": "ZeroWaste WhatsApp Business Engine",
        "recipient_phone": to_phone,
        "recipient_name": recipient_name,
        "message_type": message_type,
        "content": body_text,
        "timestamp": timestamp
    }
