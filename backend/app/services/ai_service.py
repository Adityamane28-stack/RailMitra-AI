def analyze_complaint(text: str) -> dict:
    """
    Intelligent NLP RailMitra Complaint Classifier.
    Analyzes complaint description text, categorizes issues,
    determines urgency/priority, and automatically routes to the proper railway department.
    """
    if not text:
        return {
            "category": "General Complaint",
            "confidence": 0.60,
            "priority": "Medium",
            "department": "General Helpdesk"
        }

    text_lower = text.lower()

    # 1. FIRE / SMOKE / CRITICAL LIFE SAFETY
    emergency_words = [
        "fire", "smoke", "burning", "explosion", "spark", "blast",
        "gas leak", "flame", "cylinder", "choking"
    ]
    if any(word in text_lower for word in emergency_words):
        return {
            "category": "Fire/Emergency",
            "confidence": 0.98,
            "priority": "Critical",
            "department": "Emergency Response"
        }

    # 2. MEDICAL EMERGENCY
    medical_words = [
        "medical", "doctor", "injury", "injured", "ambulance", "sick",
        "unconscious", "medicine", "heart attack", "bleeding", "fainted",
        "pregnant", "vomiting", "pain", "fever"
    ]
    if any(word in text_lower for word in medical_words):
        return {
            "category": "Medical Emergency",
            "confidence": 0.97,
            "priority": "Critical",
            "department": "Medical Department"
        }

    # 3. SECURITY / THEFT / HARASSMENT / CRIME
    security_words = [
        "theft", "stolen", "robbery", "thief", "pickpocket", "security",
        "fight", "harassment", "harass", "molest", "threat", "suspicious",
        "police", "rpf", "unauthorized", "drunk", "goons"
    ]
    if any(word in text_lower for word in security_words):
        return {
            "category": "Security",
            "confidence": 0.96,
            "priority": "Critical",
            "department": "Railway Protection Force"
        }

    # 4. TRACK / TRAIN SAFETY ISSUE
    track_words = [
        "track", "derail", "broken rail", "fishplate", "obstacle on track",
        "signal", "brakes", "coupling"
    ]
    if any(word in text_lower for word in track_words):
        return {
            "category": "Track & Safety",
            "confidence": 0.96,
            "priority": "Critical",
            "department": "Track Maintenance"
        }

    # 5. CLEANLINESS / WASHROOM / GARBAGE (Evaluated before water supply)
    cleanliness_words = [
        "dirty", "garbage", "dust", "unclean", "cleanliness", "filthy",
        "toilet", "washroom", "waste", "smell", "stink", "foul", "cockroach",
        "rats", "mosquito", "insect", "dustbin", "litter", "spit"
    ]
    if any(word in text_lower for word in cleanliness_words):
        return {
            "category": "Cleanliness",
            "confidence": 0.95,
            "priority": "High",
            "department": "Housekeeping"
        }

    # 6. WATER SUPPLY & LEAKAGE
    water_words = [
        "water", "drinking water", "water leakage", "tap", "leakage",
        "no water", "overflow", "flush", "dry tap", "tank empty"
    ]
    if any(word in text_lower for word in water_words):
        return {
            "category": "Water Supply",
            "confidence": 0.93,
            "priority": "High",
            "department": "Water Supply Department"
        }

    # 7. ELECTRICAL / AC / FAN / LIGHT / CHARGING
    electrical_words = [
        "fan", "light", "electricity", "electrical", "switch",
        "charging point", "socket", "power", "ac not working",
        "air conditioning", "cooling", "ac temperature", "darkness", "wire"
    ]
    if any(word in text_lower for word in electrical_words):
        return {
            "category": "Electrical Issue",
            "confidence": 0.94,
            "priority": "High",
            "department": "Electrical Department"
        }

    # 8. COACH HARDWARE / SEAT / BERTH / WINDOW / DOOR
    coach_hardware_words = [
        "seat", "berth", "window", "door", "broken glass", "latch",
        "lock", "mirror", "bench", "cushion", "curtain", "shutter"
    ]
    if any(word in text_lower for word in coach_hardware_words):
        return {
            "category": "Coach/Seat Issue",
            "confidence": 0.92,
            "priority": "Medium",
            "department": "Coach Maintenance"
        }

    # 9. FOOD / CATERING / PANTRY / OVERCHARGING
    food_words = [
        "food", "catering", "meal", "pantry", "breakfast", "dinner",
        "lunch", "tea", "coffee", "rotten", "stale food", "bad taste",
        "overcharging", "rate list", "irctc food"
    ]
    if any(word in text_lower for word in food_words):
        return {
            "category": "Food/Catering",
            "confidence": 0.93,
            "priority": "Medium",
            "department": "Catering Department"
        }

    # 10. BEDROLL / LINEN
    bedroll_words = [
        "bedroll", "blanket", "bedsheet", "pillow", "linen", "towel", "dirty sheet"
    ]
    if any(word in text_lower for word in bedroll_words):
        return {
            "category": "Bedroll/Linen",
            "confidence": 0.91,
            "priority": "Medium",
            "department": "Housekeeping"
        }

    # 11. STAFF / TTE BEHAVIOUR
    staff_words = [
        "staff", "employee", "attendant", "rude", "behaviour", "behavior",
        "misbehaviour", "misbehavior", "tte", "conductor", "bribe", "harsh"
    ]
    if any(word in text_lower for word in staff_words):
        return {
            "category": "Staff Behaviour",
            "confidence": 0.90,
            "priority": "Medium",
            "department": "Personnel Department"
        }

    # 12. TRAIN DELAY / PUNCTUALITY
    delay_words = [
        "delay", "late", "punctuality", "halt", "stopped", "rescheduled"
    ]
    if any(word in text_lower for word in delay_words):
        return {
            "category": "Punctuality/Delay",
            "confidence": 0.88,
            "priority": "Medium",
            "department": "Operating Department"
        }

    # Default fallback
    return {
        "category": "General Complaint",
        "confidence": 0.70,
        "priority": "Medium",
        "department": "General Helpdesk"
    }