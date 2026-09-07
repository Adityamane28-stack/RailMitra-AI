import os
import uuid
from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form
)

from sqlalchemy.orm import Session

from app.services.database import get_db
from app.models.complaint import Complaint
from app.models.passenger import Passenger

from app.auth.dependencies import (
    get_current_passenger,
    get_current_admin
)

from app.services.image_ai import analyze_image
from app.services.rail_vision import classify_railway_image


router = APIRouter(
    prefix="/complaints",
    tags=["Complaints"]
)


# =====================================================
# 1. CREATE NORMAL COMPLAINT
# PASSENGER USE
# =====================================================

@router.post("/")
def create_complaint(
    passenger_name: str = Form(...),
    phone_number: str = Form(...),

    pnr_number: str = Form(None),
    train_number: str = Form(None),
    coach_number: str = Form(None),
    seat_number: str = Form(None),

    description: str = Form(None),
    location: str = Form(None),

    evidence_type: str = Form(None),
    evidence_path: str = Form(None),

    # AI classification fields
    complaint_category: str = Form("Other"),
    ai_category: str = Form(None),
    ai_confidence: float = Form(None),
    priority: str = Form("Medium"),
    department: str = Form("General Complaint"),

    current_passenger: Passenger = Depends(get_current_passenger),

    db: Session = Depends(get_db)
):

    passenger_id = current_passenger.id

    passenger_name = current_passenger.passenger_name
    phone_number = current_passenger.phone_number

    new_complaint = Complaint(
        passenger_id=passenger_id,

        passenger_name=passenger_name,
        phone_number=phone_number,

        pnr_number=pnr_number,
        train_number=train_number,
        coach_number=coach_number,
        seat_number=seat_number,

        description=description,

        complaint_category=complaint_category,

        ai_category=ai_category,
        ai_confidence=ai_confidence,

        priority=priority,

        department=department,

        status="Pending",

        location=location,

        evidence_type=evidence_type,
        evidence_path=evidence_path,

        created_at=datetime.now(),
        resolved_at=None
    )

    try:

        db.add(new_complaint)
        db.commit()
        db.refresh(new_complaint)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

    return {
        "message": "Complaint registered successfully",

        "complaint_id": new_complaint.id,

        "category": new_complaint.complaint_category,

        "priority": new_complaint.priority,

        "department": new_complaint.department,

        "status": new_complaint.status
    }


# =====================================================
# 2. GET ALL COMPLAINTS
# ADMIN USE
# =====================================================

@router.get("/")
def get_complaints(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):

    complaints = (
        db.query(Complaint)
        .order_by(Complaint.id.desc())
        .all()
    )

    return {
        "count": len(complaints),
        "complaints": complaints
    }


# =====================================================
# 3. GET MY COMPLAINTS
# PASSENGER USE
# =====================================================

@router.get("/my")
def get_my_complaints(
    current_passenger: Passenger = Depends(get_current_passenger),
    db: Session = Depends(get_db)
):

    complaints = (
        db.query(Complaint)
        .filter(
            Complaint.passenger_id == current_passenger.id
        )
        .order_by(Complaint.id.desc())
        .all()
    )

    return {
        "count": len(complaints),
        "complaints": complaints
    }


# =====================================================
# 4. FILTER COMPLAINTS
# ADMIN USE
# =====================================================

@router.get("/filter")
def filter_complaints(
    priority: str = None,
    department: str = None,
    status: str = None,

    current_admin: dict = Depends(get_current_admin),

    db: Session = Depends(get_db)
):

    query = db.query(Complaint)

    if priority:

        query = query.filter(
            Complaint.priority == priority
        )

    if department:

        query = query.filter(
            Complaint.department == department
        )

    if status:

        query = query.filter(
            Complaint.status == status
        )

    complaints = (
        query
        .order_by(Complaint.id.desc())
        .all()
    )

    return {
        "count": len(complaints),
        "complaints": complaints
    }


# =====================================================
# 5. ADMIN DASHBOARD SUMMARY
# ADMIN USE
# =====================================================

@router.get("/dashboard/summary")
def dashboard_summary(

    current_admin: dict = Depends(get_current_admin),

    db: Session = Depends(get_db)
):

    total_complaints = (
        db.query(Complaint)
        .count()
    )

    pending_complaints = (
        db.query(Complaint)
        .filter(
            Complaint.status == "Pending"
        )
        .count()
    )

    in_progress_complaints = (
        db.query(Complaint)
        .filter(
            Complaint.status == "In Progress"
        )
        .count()
    )

    resolved_complaints = (
        db.query(Complaint)
        .filter(
            Complaint.status == "Resolved"
        )
        .count()
    )

    critical_complaints = (
        db.query(Complaint)
        .filter(
            Complaint.priority == "Critical"
        )
        .count()
    )

    high_priority_complaints = (
        db.query(Complaint)
        .filter(
            Complaint.priority == "High"
        )
        .count()
    )

    complaints = (
        db.query(Complaint)
        .all()
    )

    department_counts = {}

    for complaint in complaints:

        department = (
            complaint.department
            or "Unassigned"
        )

        department_counts[department] = (
            department_counts.get(department, 0) + 1
        )

    return {

        "total_complaints":
            total_complaints,

        "pending":
            pending_complaints,

        "in_progress":
            in_progress_complaints,

        "resolved":
            resolved_complaints,

        "critical":
            critical_complaints,

        "high_priority":
            high_priority_complaints,

        "department_wise":
            department_counts
    }


# =====================================================
# 6. AI COMPLAINT REGISTRATION
# PASSENGER USE
# =====================================================

@router.post("/ai-create")
async def create_ai_complaint(

    passenger_name: str = Form(...),

    phone_number: str = Form(...),

    pnr_number: str = Form(None),

    train_number: str = Form(None),

    coach_number: str = Form(None),

    seat_number: str = Form(None),

    description: str = Form(None),

    location: str = Form(None),

    evidence: UploadFile = File(...),

    current_passenger: Passenger = Depends(get_current_passenger),

    db: Session = Depends(get_db)
):

    # =================================================
    # CHECK IMAGE TYPE
    # =================================================

    allowed_images = [
        "image/jpeg",
        "image/jpg",
        "image/png"
    ]

    if evidence.content_type not in allowed_images:

        raise HTTPException(
            status_code=400,
            detail=(
                "AI complaint currently supports "
                "JPG, JPEG and PNG images only."
            )
        )

    # =================================================
    # CREATE UPLOAD DIRECTORY
    # =================================================

    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )

    image_folder = os.path.join(
        base_dir,
        "uploads",
        "images"
    )

    os.makedirs(
        image_folder,
        exist_ok=True
    )

    # =================================================
    # UNIQUE FILE NAME
    # =================================================

    original_filename = (
        evidence.filename
        or "complaint_image.jpg"
    )

    extension = os.path.splitext(
        original_filename
    )[1].lower()

    if not extension:
        extension = ".jpg"

    unique_filename = (
        str(uuid.uuid4())
        + extension
    )

    image_path = os.path.join(
        image_folder,
        unique_filename
    )

    # =================================================
    # SAVE IMAGE
    # =================================================

    try:

        with open(
            image_path,
            "wb"
        ) as buffer:

            while True:

                chunk = await evidence.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                buffer.write(chunk)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not save image: {str(e)}"
        )

    # =================================================
    # RUN AI IMAGE ANALYSIS
    # =================================================

    try:

        ai_result = analyze_image(
            image_path
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"AI image analysis failed: {str(e)}"
        )

    if not ai_result:

        raise HTTPException(
            status_code=500,
            detail="AI returned an empty result"
        )

    if not ai_result.get("success"):

        raise HTTPException(
            status_code=500,
            detail=ai_result.get(
                "error",
                "AI analysis failed"
            )
        )

    # =================================================
    # GET AI LABEL
    # =================================================

    detected_label = ai_result.get(
        "label",
        "Unknown"
    )

    confidence = ai_result.get(
        "confidence",
        0.0
    )

    # =================================================
    # RAILWAY CLASSIFICATION
    # =================================================

    try:

        railway_result = classify_railway_image(
            detected_label,
            confidence
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Railway classification failed: "
                f"{str(e)}"
            )
        )

    category = railway_result.get(
        "category",
        "Other"
    )

    priority = railway_result.get(
        "priority",
        "Medium"
    )

    department = railway_result.get(
        "department",
        "General Complaint"
    )

    # =================================================
    # CREATE DATABASE OBJECT
    # =================================================

    new_complaint = Complaint(

        passenger_id=current_passenger.id,

        passenger_name=current_passenger.passenger_name,

        phone_number=current_passenger.phone_number,

        pnr_number=pnr_number,

        train_number=train_number,

        coach_number=coach_number,

        seat_number=seat_number,

        description=description,

        complaint_category=category,

        ai_category=detected_label,

        ai_confidence=confidence,

        priority=priority,

        department=department,

        status="Pending",

        location=location,

        evidence_type="image",

        evidence_path=image_path,

        created_at=datetime.now(),

        resolved_at=None
    )

    # =================================================
    # SAVE TO DATABASE
    # =================================================

    try:

        db.add(
            new_complaint
        )

        db.commit()

        db.refresh(
            new_complaint
        )

    except Exception as e:

        db.rollback()

        try:

            if os.path.exists(image_path):
                os.remove(image_path)

        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

    # =================================================
    # FINAL RESPONSE
    # =================================================

    return {

        "message":
            "AI-powered complaint registered successfully",

        "complaint_id":
            new_complaint.id,

        "complaint": {

            "id":
                new_complaint.id,

            "passenger_name":
                new_complaint.passenger_name,

            "phone_number":
                new_complaint.phone_number,

            "pnr_number":
                new_complaint.pnr_number,

            "train_number":
                new_complaint.train_number,

            "coach_number":
                new_complaint.coach_number,

            "seat_number":
                new_complaint.seat_number,

            "description":
                new_complaint.description,

            "location":
                new_complaint.location,

            "category":
                new_complaint.complaint_category,

            "priority":
                new_complaint.priority,

            "department":
                new_complaint.department,

            "status":
                new_complaint.status
        },

        "ai_analysis": {

            "detected_label":
                detected_label,

            "confidence":
                confidence,

            "category":
                category,

            "priority":
                priority,

            "department":
                department
        },

        "evidence": {

            "type":
                "image",

            "filename":
                unique_filename,

            "path":
                image_path
        }
    }


# =====================================================
# 7. UPDATE COMPLAINT STATUS
# ADMIN USE
# =====================================================

@router.put("/{complaint_id}/status")
def update_complaint_status(

    complaint_id: int,

    status: str = Form(...),

    current_admin: dict = Depends(get_current_admin),

    db: Session = Depends(get_db)

):

    complaint = (
        db.query(Complaint)
        .filter(
            Complaint.id == complaint_id
        )
        .first()
    )

    if not complaint:

        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    allowed_statuses = [
        "Pending",
        "In Progress",
        "Resolved"
    ]

    if status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid status. Use: "
                "Pending, In Progress or Resolved"
            )
        )

    complaint.status = status

    if status == "Resolved":

        complaint.resolved_at = datetime.now()

    else:

        complaint.resolved_at = None

    try:

        db.commit()

        db.refresh(
            complaint
        )

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

    return {

        "message":
            "Complaint status updated successfully",

        "complaint_id":
            complaint.id,

        "status":
            complaint.status,

        "resolved_at":
            complaint.resolved_at
    }


# =====================================================
# 8. RESOLVE COMPLAINT
# ADMIN USE
# =====================================================

@router.put("/{complaint_id}/resolve")
def resolve_complaint(

    complaint_id: int,

    current_admin: dict = Depends(get_current_admin),

    db: Session = Depends(get_db)

):

    complaint = (
        db.query(Complaint)
        .filter(
            Complaint.id == complaint_id
        )
        .first()
    )

    if not complaint:

        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    if complaint.status == "Resolved":

        return {

            "message":
                "Complaint is already resolved",

            "complaint_id":
                complaint.id,

            "status":
                complaint.status,

            "resolved_at":
                complaint.resolved_at
        }

    complaint.status = "Resolved"

    complaint.resolved_at = datetime.now()

    try:

        db.commit()

        db.refresh(
            complaint
        )

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

    return {

        "message":
            "Complaint resolved successfully",

        "complaint_id":
            complaint.id,

        "status":
            complaint.status,

        "resolved_at":
            complaint.resolved_at
    }


# =====================================================
# 9. GET SINGLE COMPLAINT
# ADMIN USE
# =====================================================

@router.get("/{complaint_id}")
def get_complaint(

    complaint_id: int,

    current_admin: dict = Depends(get_current_admin),

    db: Session = Depends(get_db)

):

    complaint = (
        db.query(Complaint)
        .filter(
            Complaint.id == complaint_id
        )
        .first()
    )

    if not complaint:

        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    return complaint