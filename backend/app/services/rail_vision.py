def classify_railway_image(
    detected_label: str,
    confidence: float = 0.85
):
    """
    Convert AI image detection into RailMitra complaint category,
    priority level, and assigned railway department.
    """
    label = (detected_label or "Other").lower().strip()

    # Default baseline
    category = "Other"
    priority = "Medium"
    department = "General Complaint"

    # 1. FIRE / EMERGENCY
    if any(word in label for word in ["fire", "smoke", "flame", "burning", "explosion"]):
        category = "Fire/Emergency"
        priority = "Critical"
        department = "Emergency Response"

    # 2. TRACK ISSUE
    elif any(word in label for word in ["track", "railroad track", "railway tracks", "sleeper", "derail"]):
        category = "Track Issue"
        priority = "Critical"
        department = "Track Maintenance"

    # 3. SECURITY
    elif any(word in label for word in ["theft", "fight", "robbery", "harassment", "weapon"]):
        category = "Security"
        priority = "Critical"
        department = "Railway Protection Force"

    # 4. WATER LEAKAGE
    elif any(word in label for word in ["water leakage", "leakage", "water leak", "overflow", "tap"]):
        category = "Water Leakage"
        priority = "High"
        department = "Coach Maintenance"

    # 5. CLEANLINESS / TOILET
    elif any(word in label for word in ["dirty railway toilet", "dirty toilet", "toilet", "washroom", "bathroom"]):
        category = "Cleanliness"
        priority = "High"
        department = "Housekeeping"

    # 6. GARBAGE / WASTE
    elif any(word in label for word in ["garbage", "trash", "waste", "rubbish", "litter"]):
        category = "Garbage/Waste"
        priority = "High"
        department = "Housekeeping"

    # 7. DIRTY COACH
    elif any(word in label for word in ["dirty railway coach", "unclean", "filthy"]):
        category = "Cleanliness"
        priority = "High"
        department = "Housekeeping"

    # 8. CLEAN COACH / TOILET (Positive / Verification)
    elif any(word in label for word in ["clean railway toilet", "clean railway coach"]):
        category = "Cleanliness"
        priority = "Low"
        department = "Housekeeping"

    # 9. SEAT / COACH DAMAGE
    elif any(word in label for word in ["damaged railway seat", "broken railway seat", "seat", "bench", "berth"]):
        category = "Coach/Seat Issue"
        priority = "Medium"
        department = "Coach Maintenance"

    # 10. WINDOW DAMAGE
    elif any(word in label for word in ["damaged railway window", "broken railway window", "window", "glass"]):
        category = "Coach/Window Issue"
        priority = "High"
        department = "Coach Maintenance"

    # 11. FAN / LIGHT / ELECTRICAL
    elif any(word in label for word in ["fan", "light", "electrical", "wire", "switch", "darkness", "charging"]):
        category = "Electrical Issue"
        priority = "High"
        department = "Electrical Department"

    # 12. FOOD / CATERING
    elif any(word in label for word in ["food", "catering", "meal", "pantry", "tea", "coffee"]):
        category = "Food/Catering"
        priority = "Medium"
        department = "Catering Department"

    # 13. CROWD / PLATFORM
    elif any(word in label for word in ["crowd", "platform", "station"]):
        category = "Platform Issue"
        priority = "Medium"
        department = "Station Management"

    # 14. EQUIPMENT DAMAGE
    elif any(word in label for word in ["damaged railway equipment", "railway damage", "equipment"]):
        category = "Equipment Damage"
        priority = "High"
        department = "Coach Maintenance"

    return {
        "category": category,
        "priority": priority,
        "department": department,
        "confidence": round(float(confidence), 4)
    }