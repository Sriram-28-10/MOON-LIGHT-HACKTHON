from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base

class UserRole(str, enum.Enum):
    PROVIDER = "provider"
    RECIPIENT = "recipient"
    ANIMAL_PARTNER = "animal_partner"
    ADMIN = "admin"

class FoodCondition(str, enum.Enum):
    FRESH_EDIBLE = "fresh_edible"
    PACKAGED = "packaged"
    NEAR_EXPIRY = "near_expiry"
    NON_RECYCLABLE_ANIMAL_FEED = "non_recyclable_animal_feed"

class PostStatus(str, enum.Enum):
    AVAILABLE = "available"
    CLAIMED = "claimed"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    EXPIRED = "expired"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    role = Column(String(50), default=UserRole.PROVIDER.value)
    organization_type = Column(String(100))  # Canteen, Restaurant, Hostel, NGO, Shelter, Goat/Cow Hut
    address = Column(String(255))
    latitude = Column(Float, default=12.9716)
    longitude = Column(Float, default=77.5946)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    posts = relationship("FoodPost", back_populates="provider")
    claims = relationship("ClaimRequest", back_populates="recipient")

class FoodPost(Base):
    __tablename__ = "food_posts"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(150), nullable=False)
    food_type = Column(String(100), nullable=False)  # Cooked Meals, Bakery, Raw Veggies, Organic Scrap
    quantity_kg = Column(Float, nullable=False)
    servings_count = Column(Integer, default=0)
    condition = Column(String(50), default=FoodCondition.FRESH_EDIBLE.value)
    is_animal_feed = Column(Boolean, default=False)  # Redirected to goat/cow huts if True
    pickup_window_start = Column(DateTime, nullable=False)
    pickup_window_end = Column(DateTime, nullable=False)
    location_address = Column(String(255), nullable=False)
    delivery_address = Column(String(255), nullable=True)  # Set by Admin/Provider
    latitude = Column(Float, default=12.9716)
    longitude = Column(Float, default=77.5946)
    status = Column(String(50), default=PostStatus.AVAILABLE.value)
    urgency_score = Column(Float, default=0.5)  # AI calculated 0.0 - 1.0
    expiry_time = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    provider = relationship("User", back_populates="posts")
    claims = relationship("ClaimRequest", back_populates="post")

class ClaimRequest(Base):
    __tablename__ = "claim_requests"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("food_posts.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(50), default="pending")  # pending, approved, completed, cancelled
    pickup_otp = Column(String(6), nullable=False)
    notes = Column(Text, nullable=True)
    claimed_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    post = relationship("FoodPost", back_populates="claims")
    recipient = relationship("User", back_populates="claims")

class SlotBooking(Base):
    __tablename__ = "slot_bookings"

    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("users.id"))
    booking_date = Column(String(20), nullable=False)  # YYYY-MM-DD
    time_slot = Column(String(50), nullable=False)  # e.g., "09:00 AM - 12:00 PM"
    food_category_preference = Column(String(100), default="Cooked Meals")
    estimated_capacity_kg = Column(Float, default=50.0)
    status = Column(String(50), default="confirmed")  # confirmed, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

class SMSLog(Base):
    __tablename__ = "sms_logs"

    id = Column(Integer, primary_key=True, index=True)
    recipient_phone = Column(String(20), nullable=False)
    recipient_name = Column(String(100), nullable=False)
    message_type = Column(String(50), nullable=False)  # animal_feed_alert, claim_otp, provider_reminder
    content = Column(Text, nullable=False)
    status = Column(String(50), default="sent")
    sent_at = Column(DateTime, default=datetime.utcnow)

class WhatsAppLog(Base):
    __tablename__ = "whatsapp_logs"

    id = Column(Integer, primary_key=True, index=True)
    recipient_phone = Column(String(20), nullable=False)
    recipient_name = Column(String(100), nullable=False)
    message_type = Column(String(50), nullable=False)  # pickup_dispatch, delivery_alert, slot_confirmation
    content = Column(Text, nullable=False)
    status = Column(String(50), default="delivered_whatsapp_simulated")
    sent_at = Column(DateTime, default=datetime.utcnow)
