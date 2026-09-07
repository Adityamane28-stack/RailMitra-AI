def classify_railway_image(
    detected_label: str,
    confidence: float
):
    """
    Convert AI image detection into
    RailMitra complaint category,
    priority and department.
    """

    label = detected_label.lower().strip()

    # =================================================
    # DEFAULT
    # =================================================

    category = "Other"
    priority = "Medium"
    department = "General Complaint"


    # =================================================
    # 1. FIRE / EMERGENCY
    # =================================================

    if any(word in label for word in [
        "fire",
        "smoke",
        "flame"
    ]):

        category = "Fire/Emergency"
        priority = "Critical"
        department = "Emergency Response"


    # =================================================
    # 2. WATER LEAKAGE
    # =================================================

    elif any(word in label for word in [
        "water leakage",
        "leakage",
        "water leak"
    ]):

        category = "Water Leakage"
        priority = "High"
        department = "Coach Maintenance"


    # =================================================
    # 3. CLEANLINESS / TOILET
    # =================================================

    elif any(word in label for word in [
        "dirty railway toilet",
        "dirty toilet",
        "toilet",
        "bathroom",
        "garbage",
        "trash",
        "waste",
        "dirty railway coach"
    ]):

        category = "Cleanliness"
        priority = "High"
        department = "Housekeeping"


    # =================================================
    # 4. GARBAGE
    # =================================================

    elif any(word in label for word in [
        "garbage inside railway coach",
        "garbage at railway station",
        "trash"
    ]):

        category = "Garbage/Waste"
        priority = "High"
        department = "Housekeeping"


    # =================================================
    # 5. SEAT / COACH DAMAGE
    # =================================================

    elif any(word in label for word in [
        "damaged railway seat",
        "broken railway seat",
        "seat",
        "bench"
    ]):

        category = "Coach/Seat Issue"
        priority = "Medium"
        department = "Coach Maintenance"


    # =================================================
    # 6. WINDOW DAMAGE
    # =================================================

    elif any(word in label for word in [
        "damaged railway window",
        "broken railway window",
        "window"
    ]):

        category = "Coach/Window Issue"
        priority = "High"
        department = "Coach Maintenance"


    # =================================================
    # 7. FAN / ELECTRICAL
    # =================================================

    elif any(word in label for word in [
        "broken railway fan",
        "fan",
        "broken railway light",
        "light",
        "electrical"
    ]):

        category = "Electrical Issue"
        priority = "High"
        department = "Electrical Department"


    # =================================================
    # 8. RAILWAY TRACK
    # =================================================

    elif any(word in label for word in [
        "railway track problem",
        "railway track",
        "railroad track",
        "railway tracks"
    ]):

        category = "Track Issue"
        priority = "Critical"
        department = "Track Maintenance"


    # =================================================
    # 9. FOOD / CATERING
    # =================================================

    elif any(word in label for word in [
        "food",
        "catering"
    ]):

        category = "Food/Catering"
        priority = "Medium"
        department = "Catering Department"


    # =================================================
    # 10. CROWD / PLATFORM
    # =================================================

    elif any(word in label for word in [
        "crowded railway platform",
        "railway platform"
    ]):

        category = "Platform Issue"
        priority = "Medium"
        department = "Station Management"


    # =================================================
    # 11. GENERAL RAILWAY DAMAGE
    # =================================================

    elif any(word in label for word in [
        "damaged railway equipment",
        "railway damage"
    ]):

        category = "Equipment Damage"
        priority = "High"
        department = "Maintenance"


    # =================================================
    # RETURN RESULT
    # =================================================

    return {
        "category": category,
        "priority": priority,
        "department": department,
        "confidence": confidence
    }