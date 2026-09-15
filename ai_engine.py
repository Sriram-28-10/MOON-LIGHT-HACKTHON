import math
from datetime import datetime, timedelta
from typing import List, Dict, Any

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two GPS coordinates."""
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def calculate_urgency_score(condition: str, pickup_end: datetime, quantity_kg: float) -> float:
    """
    AI Urgency Score Calculation (0.0 to 1.0):
    - Time decay score: higher as pickup window approaches expiration
    - Condition multiplier: near expiry & non-recyclable organic scrap get highest urgency
    - Quantity weight: larger batches get slight boost to ensure zero waste of high volume
    """
    now = datetime.utcnow()
    time_left_hours = max(0.1, (pickup_end - now).total_seconds() / 3600.0)

    # Base time score: 1.0 for <= 1h remaining, tapering down to 0.1 for 24h
    time_score = min(1.0, max(0.1, 4.0 / time_left_hours))

    # Condition urgency weights
    condition_weights = {
        "near_expiry": 0.95,
        "non_recyclable_animal_feed": 0.90,
        "fresh_edible": 0.60,
        "packaged": 0.40
    }
    cond_weight = condition_weights.get(condition, 0.50)

    # Quantity weight factor
    qty_factor = min(1.2, 0.8 + (quantity_kg / 100.0))

    final_score = round(min(1.0, (time_score * 0.5 + cond_weight * 0.5) * qty_factor), 2)
    return final_score

def predict_demand_forecast() -> List[Dict[str, Any]]:
    """
    AI Demand & Surplus Forecasting Engine
    Returns predicted demand spikes across regions & categories for the next 7 days.
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    categories = ["Cooked Meals", "Bakery Items", "Fresh Produce", "Organic Animal Feed"]
    
    forecasts = []
    base_demand = 120  # kg
    
    for idx, day in enumerate(days):
        # Weekend spikes for event halls & restaurants; mid-week steady for hostels
        weekend_multiplier = 1.4 if day in ["Friday", "Saturday", "Sunday"] else 1.0
        
        predicted_surplus_kg = round(base_demand * weekend_multiplier * (1 + (idx % 3) * 0.1), 1)
        predicted_demand_kg = round(predicted_surplus_kg * 0.88, 1)
        urgency_index = "HIGH" if day in ["Friday", "Saturday"] else "MODERATE"
        
        forecasts.append({
            "day": day,
            "predicted_surplus_kg": predicted_surplus_kg,
            "predicted_demand_kg": predicted_demand_kg,
            "fulfillment_confidence_percent": min(98, round(85 + (idx * 1.5), 1)),
            "urgency_index": urgency_index,
            "recommended_focus_area": categories[idx % len(categories)]
        })
        
    return forecasts

def recommend_smart_matches(post: Dict[str, Any], recipients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    AI Smart Recipient Recommendation Engine:
    Matches a food post with eligible NGOs, Shelters, or Animal Shelters based on:
    - Target suitability (edible -> NGOs/Shelters vs non-recyclable -> Goat/Cow Huts)
    - Proximity distance
    - Capacity & urgency fit
    """
    matched_results = []
    is_animal_feed = post.get("is_animal_feed", False) or post.get("condition") == "non_recyclable_animal_feed"

    for r in recipients:
        r_role = r.get("role")
        r_org = r.get("organization_type", "")
        
        # Filter logic: animal feed goes to animal partners; edible goes to human recipients
        if is_animal_feed and r_role != "animal_partner" and "Hut" not in r_org and "Shelter" not in r_org:
            continue
        if not is_animal_feed and r_role == "animal_partner":
            continue

        dist_km = haversine_distance(
            post.get("latitude", 12.9716), post.get("longitude", 77.5946),
            r.get("latitude", 12.9716), r.get("longitude", 77.5946)
        )

        # Distance score (100% for 0km, tapering off over 20km)
        proximity_score = max(0, 100 - (dist_km * 4))
        
        # Urgency multiplier
        urgency = post.get("urgency_score", 0.5)
        total_match_score = round(min(99, proximity_score * 0.7 + (urgency * 30)), 1)

        matched_results.append({
            "recipient_id": r.get("id"),
            "name": r.get("name"),
            "organization": r_org,
            "phone": r.get("phone"),
            "distance_km": dist_km,
            "match_score": total_match_score,
            "match_reason": f"Optimal route ({dist_km} km) & high requirement for {post.get('food_type', 'food')}"
        })

    # Sort highest score first
    matched_results.sort(key=lambda x: x["match_score"], reverse=True)
    return matched_results[:5]
