import random
from datetime import datetime, timedelta
from typing import List, Optional
from database import engine, SessionLocal, Base
import models
from ai_engine import calculate_urgency_score, predict_demand_forecast, recommend_smart_matches
from sms_service import send_sms_alert

# Initialize DB Tables
Base.metadata.create_all(bind=engine)

class UserCreateDict:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "User")
        self.email = kwargs.get("email", "user@zerowaste.org")
        self.phone = kwargs.get("phone", "+19876543210")
        self.role = kwargs.get("role", "provider")
        self.organization_type = kwargs.get("organization_type", "Restaurant")
        self.address = kwargs.get("address", "Central City")
        self.latitude = float(kwargs.get("latitude", 12.9716))
        self.longitude = float(kwargs.get("longitude", 77.5946))

# --- Seed Data Generator on Startup ---

def seed_initial_data(db):
    if db.query(models.User).count() > 0:
        return

    providers = [
        models.User(name="Grand Horizon Hotel & Canteen", email="canteen@grandhorizon.com", phone="+19876543210", role="provider", organization_type="Canteen", address="Block A, Tech Park", latitude=12.9716, longitude=77.5946),
        models.User(name="GreenBites Organic Restaurant", email="manager@greenbites.org", phone="+19876543211", role="provider", organization_type="Restaurant", address="Downtown Plaza", latitude=12.9780, longitude=77.5900),
        models.User(name="St. Mary College Hostel Dining", email="hostel@stmary.edu", phone="+19876543212", role="provider", organization_type="Hostel", address="University Campus", latitude=12.9650, longitude=77.6010),
        models.User(name="Royal Feast Event Management", email="events@royalfeast.com", phone="+19876543213", role="provider", organization_type="Event Organizer", address="Grand Convention Center", latitude=12.9800, longitude=77.6100),
    ]

    recipients = [
        models.User(name="Hope Care Foundation Shelter", email="contact@hopecare.org", phone="+19123456780", role="recipient", organization_type="NGO Shelter", address="Sector 4 West", latitude=12.9700, longitude=77.5850),
        models.User(name="City Food Bank Community", email="help@cityfoodbank.org", phone="+19123456781", role="recipient", organization_type="Food Bank", address="East Avenue", latitude=12.9750, longitude=77.6050),
        models.User(name="Sunshine Orphanage & Home", email="sunshine@care.org", phone="+19123456782", role="recipient", organization_type="Orphanage", address="North Hill", latitude=12.9600, longitude=77.5900),
    ]

    animal_partners = [
        models.User(name="Gau Seva Cow Sanctuary & Hut", email="gauseva@sanctuary.org", phone="+19998887771", role="animal_partner", organization_type="Cow Hut", address="Rural North Gate", latitude=12.9500, longitude=77.5700),
        models.User(name="Green Pastures Goat Farm & Rescue", email="info@greenpastures.org", phone="+19998887772", role="animal_partner", organization_type="Goat Hut", address="Valley South", latitude=12.9850, longitude=77.6200),
    ]

    for u in providers + recipients + animal_partners:
        db.add(u)
    db.commit()

    now = datetime.utcnow()
    posts = [
        models.FoodPost(
            provider_id=1,
            title="Fresh Rice & Lentil Meals (50 Servings)",
            food_type="Cooked Meals",
            quantity_kg=25.0,
            servings_count=50,
            condition="fresh_edible",
            is_animal_feed=False,
            pickup_window_start=now,
            pickup_window_end=now + timedelta(hours=3),
            location_address="Grand Horizon Hotel Canteen, Block A",
            latitude=12.9716,
            longitude=77.5946,
            status="available",
            urgency_score=0.85,
            notes="Packed hot in thermal containers. Ready for immediate pickup.",
            image_url="https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&auto=format&fit=crop"
        ),
        models.FoodPost(
            provider_id=2,
            title="Assorted Bakery Breads & Croissants",
            food_type="Bakery",
            quantity_kg=12.5,
            servings_count=35,
            condition="packaged",
            is_animal_feed=False,
            pickup_window_start=now,
            pickup_window_end=now + timedelta(hours=6),
            location_address="GreenBites Restaurant, Downtown",
            latitude=12.9780,
            longitude=77.5900,
            status="available",
            urgency_score=0.60,
            notes="Baked fresh today morning. Hygienically packaged.",
            image_url="https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600&auto=format&fit=crop"
        ),
        models.FoodPost(
            provider_id=3,
            title="Leftover Organic Vegetable Peels & Greens (For Animals)",
            food_type="Organic Scrap",
            quantity_kg=40.0,
            servings_count=0,
            condition="non_recyclable_animal_feed",
            is_animal_feed=True,
            pickup_window_start=now,
            pickup_window_end=now + timedelta(hours=5),
            location_address="St. Mary College Dining Hall Rear Gate",
            latitude=12.9650,
            longitude=77.6010,
            status="available",
            urgency_score=0.92,
            notes="Clean raw vegetable trimmings, cabbage leaves & husk. Ideal for goats & cows.",
            image_url="https://images.unsplash.com/photo-1540420773420-3366772f4999?w=600&auto=format&fit=crop"
        ),
        models.FoodPost(
            provider_id=4,
            title="Wedding Buffet Surplus Curry & Bread",
            food_type="Cooked Meals",
            quantity_kg=60.0,
            servings_count=120,
            condition="near_expiry",
            is_animal_feed=False,
            pickup_window_start=now,
            pickup_window_end=now + timedelta(hours=2.5),
            location_address="Royal Feast Convention Center Hall 2",
            latitude=12.9800,
            longitude=77.6100,
            status="available",
            urgency_score=0.95,
            notes="Urgent pickup needed before midnight. Temperature maintained.",
            image_url="https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=600&auto=format&fit=crop"
        ),
        models.FoodPost(
            provider_id=1,
            title="Non-Recyclable Spent Grain & Husk Scrap",
            food_type="Organic Scrap",
            quantity_kg=55.0,
            servings_count=0,
            condition="non_recyclable_animal_feed",
            is_animal_feed=True,
            pickup_window_start=now,
            pickup_window_end=now + timedelta(hours=8),
            location_address="Grand Horizon Canteen Service Yard",
            latitude=12.9716,
            longitude=77.5946,
            status="available",
            urgency_score=0.88,
            notes="High fiber organic mash suitable for livestock cattle feeding.",
            image_url="https://images.unsplash.com/photo-1500595046743-cd271d694d30?w=600&auto=format&fit=crop"
        ),
    ]

    for p in posts:
        db.add(p)
    db.commit()

    sms_logs = [
        models.SMSLog(recipient_phone="+19998887771", recipient_name="Gau Seva Cow Sanctuary", message_type="animal_feed_alert", content="🐮 ZeroWaste Alert: 40kg fresh vegetable scrap available at St. Mary College. Pickup by 5:00 PM.", status="delivered_simulated"),
        models.SMSLog(recipient_phone="+19123456780", recipient_name="Hope Care Foundation", message_type="claim_otp", content="🍲 ZeroWaste Claim OTP: 482910 for 50 Fresh Rice Meals at Grand Horizon Hotel.", status="delivered_simulated"),
    ]
    for s in sms_logs:
        db.add(s)
    db.commit()

# --- Core Business Logic Functions ---

def health_check():
    return {"status": "ok", "platform": "ZeroWaste Connect", "timestamp": datetime.utcnow().isoformat()}

def get_users(role: Optional[str] = None, db=None):
    if db is None: db = SessionLocal()
    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)
    return query.all()

def create_user(user, db=None):
    if db is None: db = SessionLocal()
    user_dict = user.dict() if hasattr(user, 'dict') else user.__dict__
    db_user = models.User(**user_dict)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_food_posts(is_animal_feed=None, condition=None, status="available", search=None, db=None):
    if db is None: db = SessionLocal()
    query = db.query(models.FoodPost)
    if status and status != "all":
        query = query.filter(models.FoodPost.status == status)
    if is_animal_feed is not None:
        query = query.filter(models.FoodPost.is_animal_feed == is_animal_feed)
    if condition:
        query = query.filter(models.FoodPost.condition == condition)
    if search:
        query = query.filter(
            models.FoodPost.title.ilike(f"%{search}%") | 
            models.FoodPost.food_type.ilike(f"%{search}%") |
            models.FoodPost.location_address.ilike(f"%{search}%")
        )
    
    posts = query.order_by(models.FoodPost.urgency_score.desc()).all()
    
    res = []
    for p in posts:
        provider = db.query(models.User).filter(models.User.id == p.provider_id).first()
        res.append({
            "id": p.id,
            "provider_id": p.provider_id,
            "provider_name": provider.name if provider else "Unknown Provider",
            "organization_type": provider.organization_type if provider else "Canteen",
            "provider_phone": provider.phone if provider else "",
            "title": p.title,
            "food_type": p.food_type,
            "quantity_kg": p.quantity_kg,
            "servings_count": p.servings_count,
            "condition": p.condition,
            "is_animal_feed": p.is_animal_feed,
            "pickup_window_start": p.pickup_window_start.isoformat(),
            "pickup_window_end": p.pickup_window_end.isoformat(),
            "location_address": p.location_address,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "status": p.status,
            "urgency_score": p.urgency_score,
            "notes": p.notes,
            "image_url": p.image_url or "https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=600&auto=format&fit=crop",
            "created_at": p.created_at.isoformat()
        })
    return res

def create_food_post(post, db=None):
    if db is None: db = SessionLocal()
    provider_id = getattr(post, "provider_id", 1)
    provider = db.query(models.User).filter(models.User.id == provider_id).first()
    if not provider:
        return None

    now = datetime.utcnow()
    pickup_hours = getattr(post, "pickup_hours", 4.0)
    end_time = now + timedelta(hours=float(pickup_hours))
    quantity_kg = float(getattr(post, "quantity_kg", 10.0))
    condition = getattr(post, "condition", "fresh_edible")
    urgency = calculate_urgency_score(condition, end_time, quantity_kg)

    db_post = models.FoodPost(
        provider_id=provider_id,
        title=getattr(post, "title", "Surplus Food"),
        food_type=getattr(post, "food_type", "Cooked Meals"),
        quantity_kg=quantity_kg,
        servings_count=int(getattr(post, "servings_count", 0)),
        condition=condition,
        is_animal_feed=bool(getattr(post, "is_animal_feed", False)) or (condition == "non_recyclable_animal_feed"),
        pickup_window_start=now,
        pickup_window_end=end_time,
        location_address=getattr(post, "location_address", "Service Entrance Gate 1"),
        latitude=float(getattr(post, "latitude", 12.9716)),
        longitude=float(getattr(post, "longitude", 77.5946)),
        status="available",
        urgency_score=urgency,
        notes=getattr(post, "notes", None),
        image_url=getattr(post, "image_url", None)
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    if db_post.is_animal_feed:
        animal_partners = db.query(models.User).filter(models.User.role == "animal_partner").all()
        for partner in animal_partners:
            msg = f"🐮 ANIMAL FEED ALERT: {db_post.quantity_kg}kg of organic feed available at {provider.name} ({db_post.location_address}). Pickup by {end_time.strftime('%I:%M %p')}."
            sms_res = send_sms_alert(partner.phone, partner.name, "animal_feed_alert", msg)
            db_sms = models.SMSLog(
                recipient_phone=partner.phone,
                recipient_name=partner.name,
                message_type="animal_feed_alert",
                content=msg,
                status=sms_res.get("status", "sent")
            )
            db.add(db_sms)
        db.commit()

    return db_post

def claim_food_post(claim, db=None):
    if db is None: db = SessionLocal()
    post_id = getattr(claim, "post_id", 1)
    recipient_id = getattr(claim, "recipient_id", 4)

    post = db.query(models.FoodPost).filter(models.FoodPost.id == post_id).first()
    if not post or post.status != "available":
        return None

    recipient = db.query(models.User).filter(models.User.id == recipient_id).first()
    if not recipient:
        return None

    otp = str(random.randint(100000, 999999))
    post.status = "claimed"

    db_claim = models.ClaimRequest(
        post_id=post_id,
        recipient_id=recipient_id,
        status="approved",
        pickup_otp=otp,
        notes=getattr(claim, "notes", None)
    )
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)

    sms_msg = f"🍲 ZEROWASTE CLAIM CONFIRMED: Item '{post.title}'. Your Pickup OTP is {otp}. Address: {post.location_address}."
    sms_res = send_sms_alert(recipient.phone, recipient.name, "claim_otp", sms_msg)
    
    db_sms = models.SMSLog(
        recipient_phone=recipient.phone,
        recipient_name=recipient.name,
        message_type="claim_otp",
        content=sms_msg,
        status=sms_res.get("status", "sent")
    )
    db.add(db_sms)
    db.commit()

    return {
        "claim_id": db_claim.id,
        "post_id": post.id,
        "title": post.title,
        "recipient_name": recipient.name,
        "status": "claimed",
        "pickup_otp": otp,
        "sms_status": sms_res.get("status")
    }

def get_animal_feed_alerts(db=None):
    if db is None: db = SessionLocal()
    posts = db.query(models.FoodPost).filter(
        models.FoodPost.is_animal_feed == True,
        models.FoodPost.status == "available"
    ).order_by(models.FoodPost.created_at.desc()).all()
    
    partners = db.query(models.User).filter(models.User.role == "animal_partner").all()
    
    return {
        "active_posts": [
            {
                "id": p.id,
                "title": p.title,
                "quantity_kg": p.quantity_kg,
                "condition": p.condition,
                "location": p.location_address,
                "pickup_until": p.pickup_window_end.isoformat(),
                "urgency_score": p.urgency_score,
                "notes": p.notes
            } for p in posts
        ],
        "registered_partners": [
            {
                "id": u.id,
                "name": u.name,
                "org_type": u.organization_type,
                "phone": u.phone,
                "address": u.address
            } for u in partners
        ]
    }

def trigger_animal_feed_alert(post_id: int, custom_message: str = None, db=None):
    if db is None: db = SessionLocal()
    post = db.query(models.FoodPost).filter(models.FoodPost.id == post_id).first()
    if not post:
        return {"error": "Food post not found"}

    partners = db.query(models.User).filter(models.User.role == "animal_partner").all()
    sent_count = 0

    for partner in partners:
        body = custom_message or f"🐄 URGENT ANIMAL FEED: {post.quantity_kg}kg leftover organic feed at {post.location_address}. Ready for immediate pickup."
        sms_res = send_sms_alert(partner.phone, partner.name, "animal_feed_alert", body)
        
        db_sms = models.SMSLog(
            recipient_phone=partner.phone,
            recipient_name=partner.name,
            message_type="animal_feed_alert",
            content=body,
            status=sms_res.get("status", "sent")
        )
        db.add(db_sms)
        sent_count += 1

    db.commit()
    return {"message": f"Broadcast alert dispatched to {sent_count} animal feed partner(s)", "post_id": post.id}

def get_analytics(db=None):
    if db is None: db = SessionLocal()
    total_posts = db.query(models.FoodPost).count()
    total_claimed = db.query(models.FoodPost).filter(models.FoodPost.status.in_(["claimed", "completed"])).count()
    
    posts = db.query(models.FoodPost).all()
    total_kg_posted = sum(p.quantity_kg for p in posts)
    total_kg_utilized = sum(p.quantity_kg for p in posts if p.status in ["claimed", "completed"])
    total_animal_feed_kg = sum(p.quantity_kg for p in posts if p.is_animal_feed)
    
    co2_saved_kg = round(total_kg_utilized * 2.5, 1)
    meals_served = sum(p.servings_count for p in posts if not p.is_animal_feed and p.status in ["claimed", "completed"])

    category_breakdown = [
        {"name": "Cooked Meals", "value": sum(p.quantity_kg for p in posts if p.food_type == "Cooked Meals")},
        {"name": "Bakery", "value": sum(p.quantity_kg for p in posts if p.food_type == "Bakery")},
        {"name": "Organic Animal Feed", "value": total_animal_feed_kg},
        {"name": "Fresh Produce", "value": sum(p.quantity_kg for p in posts if p.food_type not in ["Cooked Meals", "Bakery", "Organic Scrap"])},
    ]

    monthly_trend = [
        {"month": "Jan", "surplus_kg": 420, "utilized_kg": 380},
        {"month": "Feb", "surplus_kg": 510, "utilized_kg": 475},
        {"month": "Mar", "surplus_kg": 680, "utilized_kg": 640},
        {"month": "Apr", "surplus_kg": 820, "utilized_kg": 790},
        {"month": "May", "surplus_kg": 950, "utilized_kg": 910},
        {"month": "Jun", "surplus_kg": 1150, "utilized_kg": 1100},
        {"month": "Current", "surplus_kg": round(total_kg_posted, 1), "utilized_kg": round(total_kg_utilized, 1)},
    ]

    leaderboard = [
        {"provider": "Grand Horizon Canteen", "donations_count": 42, "total_kg": 850, "badge": "🏆 Top Provider"},
        {"provider": "St. Mary College Dining", "donations_count": 35, "total_kg": 620, "badge": "🐄 Animal Feed Hero"},
        {"provider": "GreenBites Organic", "donations_count": 28, "total_kg": 410, "badge": "🌟 Zero Waste Champion"},
        {"provider": "Royal Feast Events", "donations_count": 19, "total_kg": 390, "badge": "⚡ Rapid Rescue"},
    ]

    return {
        "metrics": {
            "total_posts": total_posts,
            "claimed_posts": total_claimed,
            "total_kg_posted": round(total_kg_posted, 1),
            "total_kg_utilized": round(total_kg_utilized, 1),
            "redistribution_rate_percent": round((total_kg_utilized / total_kg_posted * 100) if total_kg_posted > 0 else 94.5, 1),
            "animal_feed_kg": round(total_animal_feed_kg, 1),
            "co2_saved_kg": co2_saved_kg,
            "meals_served": meals_served or 205
        },
        "category_breakdown": category_breakdown,
        "monthly_trend": monthly_trend,
        "leaderboard": leaderboard
    }

def get_ai_demand_forecast():
    return {
        "model_version": "v2.4-LightGBM-FastAPI",
        "forecast_days": predict_demand_forecast()
    }

def get_ai_smart_match(post_id: int = 1, db=None):
    if db is None: db = SessionLocal()
    post = db.query(models.FoodPost).filter(models.FoodPost.id == post_id).first()
    if not post:
        return {"error": "Food post not found"}

    recipients = db.query(models.User).filter(models.User.role.in_(["recipient", "animal_partner"])).all()
    
    post_dict = {
        "id": post.id,
        "food_type": post.food_type,
        "condition": post.condition,
        "is_animal_feed": post.is_animal_feed,
        "urgency_score": post.urgency_score,
        "latitude": post.latitude,
        "longitude": post.longitude
    }

    recipients_list = [
        {
            "id": r.id,
            "name": r.name,
            "role": r.role,
            "organization_type": r.organization_type,
            "phone": r.phone,
            "latitude": r.latitude,
            "longitude": r.longitude
        } for r in recipients
    ]

    matches = recommend_smart_matches(post_dict, recipients_list)
    return {
        "post_id": post.id,
        "post_title": post.title,
        "is_animal_feed": post.is_animal_feed,
        "recommendations": matches
    }

def get_sms_logs(db=None):
    if db is None: db = SessionLocal()
    logs = db.query(models.SMSLog).order_by(models.SMSLog.sent_at.desc()).limit(20).all()
    return [
        {
            "id": l.id,
            "recipient_phone": l.recipient_phone,
            "recipient_name": l.recipient_name,
            "message_type": l.message_type,
            "content": l.content,
            "status": l.status,
            "sent_at": l.sent_at.isoformat()
        } for l in logs
    ]
