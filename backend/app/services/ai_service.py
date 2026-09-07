def analyze_complaint(text: str):
    """
    Basic AI-style complaint classification.
    This is our initial classifier.
    Later we will replace/upgrade this with
    real ML/AI models for image, video and audio.
    """

    text = text.lower()

    # Default values
    category = "Other"
    confidence = 0.50
    priority = "Medium"
    department = "General Complaint"


    # -----------------------------
    # CLEANLINESS
    # -----------------------------

    cleanliness_words = [
        "dirty",
        "garbage",
        "dust",
        "unclean",
        "cleanliness",
        "filthy",
        "toilet",
        "washroom",
        "waste",
        "smell"
    ]

    if any(word in text for word in cleanliness_words):

        category = "Cleanliness"
        confidence = 0.92
        priority = "High"
        department = "Housekeeping"


    # -----------------------------
    # FIRE / EMERGENCY
    # -----------------------------

    emergency_words = [
        "fire",
        "smoke",
        "burning",
        "explosion",
        "emergency"
    ]

    if any(word in text for word in emergency_words):

        category = "Fire/Emergency"
        confidence = 0.98
        priority = "Critical"
        department = "Emergency Response"


    # -----------------------------
    # ELECTRICAL
    # -----------------------------

    electrical_words = [
        "fan",
        "light",
        "electricity",
        "electrical",
        "switch",
        "charging point",
        "socket",
        "power"
    ]

    if any(word in text for word in electrical_words):

        category = "Electrical"
        confidence = 0.91
        priority = "High"
        department = "Electrical Department"


    # -----------------------------
    # WATER
    # -----------------------------

    water_words = [
        "water",
        "drinking water",
        "water leakage",
        "tap",
        "leakage"
    ]

    if any(word in text for word in water_words):

        category = "Water Supply"
        confidence = 0.90
        priority = "High"
        department = "Water Supply Department"


    # -----------------------------
    # STAFF BEHAVIOUR
    # -----------------------------

    staff_words = [
        "staff",
        "employee",
        "attendant",
        "rude",
        "behaviour",
        "behavior",
        "misbehaviour",
        "misbehavior"
    ]

    if any(word in text for word in staff_words):

        category = "Staff Behaviour"
        confidence = 0.89
        priority = "Medium"
        department = "Personnel Department"


    # -----------------------------
    # SECURITY
    # -----------------------------

    security_words = [
        "theft",
        "stolen",
        "robbery",
        "security",
        "fight",
        "harassment",
        "suspicious"
    ]

    if any(word in text for word in security_words):

        category = "Security"
        confidence = 0.95
        priority = "Critical"
        department = "Railway Protection Force"


    # -----------------------------
    # MEDICAL
    # -----------------------------

    medical_words = [
        "medical",
        "doctor",
        "injury",
        "injured",
        "ambulance",
        "sick",
        "unconscious",
        "medicine"
    ]

    if any(word in text for word in medical_words):

        category = "Medical Emergency"
        confidence = 0.96
        priority = "Critical"
        department = "Medical Department"


    return {
        "category": category,
        "confidence": confidence,
        "priority": priority,
        "department": department
    }