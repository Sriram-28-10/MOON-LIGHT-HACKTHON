import unittest
from datetime import datetime
from database import SessionLocal, Base, engine
import models
from whatsapp_service import send_whatsapp_message
from main import (
    health_check,
    get_users,
    get_food_posts,
    create_food_post,
    get_ai_demand_forecast,
    get_animal_feed_alerts,
    get_analytics
)

class TestZeroWasteExpansion(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_whatsapp_message_dispatch(self):
        res = send_whatsapp_message("+19876543210", "Test Partner", "pickup_alert", "💬 Unit Test WhatsApp Message")
        self.assertIn(res["status"], ["sent", "delivered_whatsapp_simulated"])
        self.assertEqual(res["recipient_phone"], "+19876543210")

    def test_slot_booking_model(self):
        booking = models.SlotBooking(
            partner_id=1,
            booking_date="2026-09-18",
            time_slot="01:00 PM - 04:00 PM",
            food_category_preference="Cooked Meals",
            estimated_capacity_kg=60.0,
            status="confirmed"
        )
        self.db.add(booking)
        self.db.commit()
        self.assertIsNotNone(booking.id)
        self.assertEqual(booking.booking_date, "2026-09-18")

    def test_health(self):
        res = health_check()
        self.assertEqual(res["status"], "ok")

if __name__ == "__main__":
    unittest.main()
