import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from database import SessionLocal, Base, engine
import models
from whatsapp_service import send_whatsapp_message
from main import (
    health_check,
    get_users,
    create_user,
    UserCreateDict,
    get_food_posts,
    create_food_post,
    claim_food_post,
    get_animal_feed_alerts,
    trigger_animal_feed_alert,
    get_analytics,
    get_ai_demand_forecast,
    get_ai_smart_match,
    get_sms_logs
)

# Initialize DB
Base.metadata.create_all(bind=engine)

class ZeroWasteRequestHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        db = SessionLocal()
        try:
            if path == "/api/health":
                data = health_check()
            elif path == "/api/users":
                role = query.get("role", [None])[0]
                users = get_users(role=role, db=db)
                data = [{
                    "id": u.id, "name": u.name, "email": u.email, "phone": u.phone,
                    "role": u.role, "organization_type": u.organization_type, "address": u.address
                } for u in users]
            elif path == "/api/posts":
                is_animal = query.get("is_animal_feed", [None])[0]
                is_animal_bool = True if is_animal == "true" else (False if is_animal == "false" else None)
                condition = query.get("condition", [None])[0]
                status = query.get("status", ["available"])[0]
                search = query.get("search", [None])[0]
                data = get_food_posts(is_animal_feed=is_animal_bool, condition=condition, status=status, search=search, db=db)
            elif path == "/api/slots":
                bookings = db.query(models.SlotBooking).all()
                data = [{
                    "id": b.id, "date": b.booking_date, "time": b.time_slot,
                    "category": b.food_category_preference, "capacity_kg": b.estimated_capacity_kg, "status": b.status
                } for b in bookings]
            elif path == "/api/animal-feed-alerts":
                data = get_animal_feed_alerts(db=db)
            elif path == "/api/analytics":
                data = get_analytics(db=db)
            elif path == "/api/ai/forecast":
                data = get_ai_demand_forecast()
            elif path == "/api/ai/match":
                post_id = int(query.get("post_id", [1])[0])
                data = get_ai_smart_match(post_id=post_id, db=db)
            elif path == "/api/sms-logs":
                data = get_sms_logs(db=db)
            elif path == "/api/whatsapp/logs":
                w_logs = db.query(models.WhatsAppLog).order_by(models.WhatsAppLog.sent_at.desc()).limit(20).all()
                data = [{
                    "id": w.id, "recipient_phone": w.recipient_phone, "recipient_name": w.recipient_name,
                    "message_type": w.message_type, "content": w.content, "status": w.status, "sent_at": w.sent_at.isoformat()
                } for w in w_logs]
            else:
                self.send_response(404)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Not Found"}).encode("utf-8"))
                return

            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        finally:
            db.close()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(length) if length > 0 else b"{}"
        body_json = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}

        db = SessionLocal()
        try:
            if path == "/api/users":
                u = create_user(UserCreateDict(**body_json), db=db)
                data = {"id": u.id, "name": u.name, "email": u.email, "role": u.role}
            elif path == "/api/posts":
                class PostWrap:
                    def __init__(self, d):
                        for k, v in d.items():
                            setattr(self, k, v)
                        self.provider_id = int(d.get("provider_id", 1))
                        self.title = d.get("title", "Surplus Food")
                        self.food_type = d.get("food_type", "Cooked Meals")
                        self.quantity_kg = float(d.get("quantity_kg", 10.0))
                        self.servings_count = int(d.get("servings_count", 0))
                        self.condition = d.get("condition", "fresh_edible")
                        self.is_animal_feed = bool(d.get("is_animal_feed", False))
                        self.pickup_hours = float(d.get("pickup_hours", 4.0))
                        self.location_address = d.get("location_address", "Central Yard Gate 1")
                        self.delivery_address = d.get("delivery_address", "Partner Shelter Gate")
                        self.latitude = float(d.get("latitude", 12.9716))
                        self.longitude = float(d.get("longitude", 77.5946))
                        self.notes = d.get("notes")
                        self.image_url = d.get("image_url")
                p = create_food_post(PostWrap(body_json), db=db)
                
                # Auto WhatsApp alert
                wa_msg = f"💬 ZEROWASTE WHATSAPP ALERT: Item '{p.title}' ({p.quantity_kg}kg) posted! Pickup address: {p.location_address}."
                wa_res = send_whatsapp_message("+19876543210", "Partner Organization", "pickup_dispatch", wa_msg)
                db_wa = models.WhatsAppLog(
                    recipient_phone="+19876543210",
                    recipient_name="Partner Organization",
                    message_type="pickup_dispatch",
                    content=wa_msg,
                    status=wa_res.get("status", "delivered_whatsapp_simulated")
                )
                db.add(db_wa)
                db.commit()

                data = {"id": p.id, "title": p.title, "status": p.status, "urgency_score": p.urgency_score, "whatsapp_sent": True}
            elif path == "/api/claims":
                class ClaimWrap:
                    def __init__(self, d):
                        self.post_id = int(d.get("post_id", 1))
                        self.recipient_id = int(d.get("recipient_id", 4))
                        self.notes = d.get("notes")
                data = claim_food_post(ClaimWrap(body_json), db=db)
            elif path == "/api/slots/book":
                b = models.SlotBooking(
                    partner_id=int(body_json.get("partner_id", 4)),
                    booking_date=body_json.get("date", "2026-09-16"),
                    time_slot=body_json.get("slot", "09:00 AM - 12:00 PM"),
                    food_category_preference=body_json.get("category", "Cooked Meals"),
                    estimated_capacity_kg=float(body_json.get("capacity_kg", 50.0)),
                    status="confirmed"
                )
                db.add(b)
                db.commit()
                db.refresh(b)
                
                # WhatsApp Slot Confirmation
                wa_msg = f"📅 ZEROWASTE SLOT CONFIRMED: Reserved pickup slot for {b.booking_date} ({b.time_slot}) for category {b.food_category_preference} (~{b.estimated_capacity_kg}kg)."
                wa_res = send_whatsapp_message("+19123456780", "Partner Shelter", "slot_confirmation", wa_msg)
                db_wa = models.WhatsAppLog(
                    recipient_phone="+19123456780",
                    recipient_name="Partner Shelter",
                    message_type="slot_confirmation",
                    content=wa_msg,
                    status=wa_res.get("status", "delivered_whatsapp_simulated")
                )
                db.add(db_wa)
                db.commit()

                data = {"booking_id": b.id, "date": b.booking_date, "slot": b.time_slot, "status": b.status}
            elif path == "/api/whatsapp/send":
                phone = body_json.get("phone", "+19876543210")
                name = body_json.get("recipient_name", "Partner Contact")
                msg = body_json.get("custom_message", "💬 ZeroWaste Alert: Pickup ready.")
                res = send_whatsapp_message(phone, name, "admin_dispatch", msg)
                
                db_wa = models.WhatsAppLog(
                    recipient_phone=phone,
                    recipient_name=name,
                    message_type="admin_dispatch",
                    content=msg,
                    status=res.get("status", "delivered_whatsapp_simulated")
                )
                db.add(db_wa)
                db.commit()

                data = res
            elif path == "/api/animal-feed-alerts/trigger":
                post_id = int(body_json.get("post_id", 1))
                msg = body_json.get("custom_message")
                data = trigger_animal_feed_alert(post_id=post_id, custom_message=msg, db=db)
            else:
                self.send_response(404)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Not Found"}).encode("utf-8"))
                return

            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        finally:
            db.close()

def run_server(port=8000):
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, ZeroWasteRequestHandler)
    print(f"ZeroWaste Python HTTP Server running on http://127.0.0.1:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
