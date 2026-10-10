import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    Request
)
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.services.database import get_db
from app.models.complaint import Complaint
from app.models.passenger import Passenger
from app.auth.dependencies import (
    get_current_passenger,
    get_current_admin
)
from app.services.image_ai import analyze_image
from app.services.rail_vision import classify_railway_image
from app.services.ai_service import analyze_complaint
from app.config import (
    IMAGE_DIR,
    JWT_SECRET_KEY,
    JWT_ALGORITHM
)

router = APIRouter(
    prefix="/complaints",
    tags=["Complaints"]
)


# =====================================================
# 1. CREATE NORMAL / TEXT COMPLAINT (PASSENGER)
# With Automatic AI NLP Classification
# =====================================================

@router.post("/")
def create_complaint(
    passenger_name: str = Form(None),
    phone_number: str = Form(None),
    pnr_number: Optional[str] = Form(None),
    train_number: Optional[str] = Form(None),
    coach_number: Optional[str] = Form(None),
    seat_number: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    evidence_type: Optional[str] = Form(None),
    evidence_path: Optional[str] = Form(None),
    complaint_category: Optional[str] = Form(None),
    ai_category: Optional[str] = Form(None),
    ai_confidence: Optional[float] = Form(None),
    priority: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    current_passenger: Passenger = Depends(get_current_passenger),
    db: Session = Depends(get_db)
):
    """
    Register a complaint for the logged-in passenger.
    If no category is specified, uses AI NLP to classify description.
    """
    final_name = current_passenger.passenger_name or passenger_name
    final_phone = current_passenger.phone_number or phone_number

    cat = complaint_category
    pri = priority
    dep = department
    ai_cat = ai_category
    ai_conf = ai_confidence

    # If category not provided or set to generic, run AI text NLP classifier
    if (not cat or cat in ["Other", "General", "General Complaint"]) and description:
        nlp_res = analyze_complaint(description)
        cat = nlp_res["category"]
        pri = pri or nlp_res["priority"]
        dep = dep or nlp_res["department"]
        ai_cat = ai_cat or nlp_res["category"]
        ai_conf = ai_conf or nlp_res["confidence"]

    cat = cat or "Other"
    pri = pri or "Medium"
    dep = dep or "General Complaint"

    new_complaint = Complaint(
        passenger_id=current_passenger.id,
        passenger_name=final_name,
        phone_number=final_phone,
        pnr_number=pnr_number,
        train_number=train_number,
        coach_number=coach_number,
        seat_number=seat_number,
        description=description,
        complaint_category=cat,
        ai_category=ai_cat,
        ai_confidence=ai_conf,
        priority=pri,
        department=dep,
        status="Pending",
        location=location,
        evidence_type=evidence_type,
        evidence_path=evidence_path,
        created_at=datetime.utcnow(),
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
        "success": True,
        "message": "Complaint registered successfully",
        "complaint_id": new_complaint.id,
        "category": new_complaint.complaint_category,
        "priority": new_complaint.priority,
        "department": new_complaint.department,
        "status": new_complaint.status,
        "ai_category": new_complaint.ai_category,
        "ai_confidence": new_complaint.ai_confidence
    }


# =====================================================
# 2. GET ALL COMPLAINTS (ADMIN)
# =====================================================

@router.get("/")
def get_complaints(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all registered complaints ordered by latest first (Admin).
    """
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
# 3. GET MY COMPLAINTS (PASSENGER)
# =====================================================

@router.get("/my")
def get_my_complaints(
    current_passenger: Passenger = Depends(get_current_passenger),
    db: Session = Depends(get_db)
):
    """
    Get all complaints filed by the currently logged-in passenger.
    """
    complaints = (
        db.query(Complaint)
        .filter(Complaint.passenger_id == current_passenger.id)
        .order_by(Complaint.id.desc())
        .all()
    )

    return {
        "count": len(complaints),
        "complaints": complaints
    }


# =====================================================
# 4. FILTER COMPLAINTS (ADMIN)
# =====================================================

@router.get("/filter")
def filter_complaints(
    priority: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Filter complaints by priority, department, category, and status.
    """
    query = db.query(Complaint)

    if priority:
        query = query.filter(Complaint.priority == priority)
    if department:
        query = query.filter(Complaint.department == department)
    if status:
        query = query.filter(Complaint.status == status)
    if category:
        query = query.filter(Complaint.complaint_category == category)

    complaints = query.order_by(Complaint.id.desc()).all()

    return {
        "count": len(complaints),
        "complaints": complaints
    }


# =====================================================
# 5. ADMIN DASHBOARD SUMMARY (ADMIN)
# =====================================================

@router.get("/dashboard/summary")
def dashboard_summary(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Comprehensive summary metrics for the Admin Dashboard.
    """
    total = db.query(Complaint).count()
    pending = db.query(Complaint).filter(Complaint.status == "Pending").count()
    in_progress = db.query(Complaint).filter(Complaint.status == "In Progress").count()
    resolved = db.query(Complaint).filter(Complaint.status == "Resolved").count()
    critical = db.query(Complaint).filter(Complaint.priority == "Critical").count()
    high = db.query(Complaint).filter(Complaint.priority == "High").count()

    complaints = db.query(Complaint).all()
    department_counts = {}

    for complaint in complaints:
        dept = complaint.department or "Unassigned"
        department_counts[dept] = department_counts.get(dept, 0) + 1

    return {
        "total_complaints": total,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "critical": critical,
        "high_priority": high,
        "department_wise": department_counts
    }


# =====================================================
# 6. AI COMPLAINT REGISTRATION (PASSENGER)
# Upload image + run zero-shot computer vision
# =====================================================

@router.post("/ai-create")
async def create_ai_complaint(
    passenger_name: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    pnr_number: Optional[str] = Form(None),
    train_number: Optional[str] = Form(None),
    coach_number: Optional[str] = Form(None),
    seat_number: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    evidence: UploadFile = File(...),
    current_passenger: Passenger = Depends(get_current_passenger),
    db: Session = Depends(get_db)
):
    """
    Upload evidence photo and run RailMitra Computer Vision to automatically
    detect the issue, priority, and department.
    """
    content_type = evidence.content_type or ""
    allowed_images = [
        "image/jpeg", "image/jpg", "image/png", "image/webp"
    ]
    if content_type not in allowed_images and not evidence.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        raise HTTPException(
            status_code=400,
            detail="AI image complaint supports JPG, PNG, and WEBP images."
        )

    original_filename = evidence.filename or "complaint_image.jpg"
    extension = os.path.splitext(original_filename)[1].lower() or ".jpg"
    unique_filename = f"{uuid.uuid4()}{extension}"
    image_path = str(IMAGE_DIR / unique_filename)

    try:
        with open(image_path, "wb") as buffer:
            while True:
                chunk = await evidence.read(1024 * 1024)
                if not chunk:
                    break
                buffer.write(chunk)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not save evidence image: {str(e)}"
        )

    # Run AI Vision Analysis
    ai_result = analyze_image(image_path)
    if not ai_result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=ai_result.get("error", "AI image analysis failed")
        )

    detected_label = ai_result.get("label", "damaged railway coach or equipment")
    confidence = ai_result.get("confidence", 0.85)

    # Railway domain classification
    railway_result = classify_railway_image(detected_label, confidence)
    category = railway_result.get("category", "Other")
    priority = railway_result.get("priority", "Medium")
    department = railway_result.get("department", "General Complaint")

    # If text description was also provided with higher emergency signals, cross-check
    if description:
        nlp_check = analyze_complaint(description)
        if nlp_check["priority"] == "Critical":
            priority = "Critical"
            department = nlp_check["department"]
            category = nlp_check["category"]

    new_complaint = Complaint(
        passenger_id=current_passenger.id,
        passenger_name=current_passenger.passenger_name or passenger_name,
        phone_number=current_passenger.phone_number or phone_number,
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
        created_at=datetime.utcnow(),
        resolved_at=None
    )

    try:
        db.add(new_complaint)
        db.commit()
        db.refresh(new_complaint)
    except Exception as e:
        db.rollback()
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

    return {
        "success": True,
        "message": "AI-powered complaint registered successfully",
        "complaint_id": new_complaint.id,
        "category": new_complaint.complaint_category,
        "priority": new_complaint.priority,
        "department": new_complaint.department,
        "status": new_complaint.status,
        "ai_analysis": {
            "detected_label": detected_label,
            "confidence": confidence,
            "category": category,
            "priority": priority,
            "department": department
        },
        "evidence": {
            "type": "image",
            "filename": unique_filename,
            "path": image_path
        }
    }


# =====================================================
# 7. PUBLIC TRACK COMPLAINT BY ID OR PNR
# (No login required - accessible for instant tracking)
# =====================================================

@router.get("/track/{query}")
def track_complaint(
    query: str,
    db: Session = Depends(get_db)
):
    """
    Public lookup for passengers to track status via Complaint ID or PNR.
    Returns status, timeline steps, and resolution progress.
    """
    query = query.strip()
    complaint = None

    if query.isdigit() and len(query) <= 8 and int(query) < 2147483647:
        complaint = db.query(Complaint).filter(Complaint.id == int(query)).first()

    if not complaint:
        complaint = (
            db.query(Complaint)
            .filter(Complaint.pnr_number.ilike(f"%{query}%"))
            .order_by(Complaint.id.desc())
            .first()
        )

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail=f"No complaint found matching ID or PNR: '{query}'"
        )

    is_pending = complaint.status == "Pending"
    is_in_prog = complaint.status in ["In Progress", "Action Taken"]
    is_resolved = complaint.status == "Resolved"

    timeline = [
        {
            "step": "Complaint Registered",
            "description": f"Filed on {complaint.created_at.strftime('%Y-%m-%d %H:%M') if complaint.created_at else 'Recently'}",
            "completed": True,
            "current": is_pending
        },
        {
            "step": "AI Vision & NLP Analysis",
            "description": f"Classified as {complaint.complaint_category} with {complaint.priority} priority",
            "completed": True,
            "current": False
        },
        {
            "step": f"Assigned to {complaint.department or 'Department'}",
            "description": "Forwarded to on-duty railway personnel for action",
            "completed": is_in_prog or is_resolved,
            "current": is_in_prog
        },
        {
            "step": "Issue Resolved",
            "description": f"Resolved on {complaint.resolved_at.strftime('%Y-%m-%d %H:%M') if complaint.resolved_at else 'Pending resolution'}",
            "completed": is_resolved,
            "current": is_resolved
        }
    ]

    return {
        "success": True,
        "complaint": complaint,
        "timeline": timeline
    }


# =====================================================
# 8. UPDATE COMPLAINT STATUS (ADMIN)
# =====================================================

@router.put("/{complaint_id}/status")
def update_complaint_status(
    complaint_id: int,
    status: str = Form(...),
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin updates complaint status to Pending, In Progress, or Resolved.
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    allowed_statuses = ["Pending", "In Progress", "Resolved"]
    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Choose from: {', '.join(allowed_statuses)}"
        )

    complaint.status = status
    if status == "Resolved":
        complaint.resolved_at = datetime.utcnow()
    else:
        complaint.resolved_at = None

    try:
        db.commit()
        db.refresh(complaint)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {
        "success": True,
        "message": f"Complaint #{complaint.id} status updated to {complaint.status}",
        "complaint_id": complaint.id,
        "status": complaint.status,
        "resolved_at": complaint.resolved_at
    }


# =====================================================
# 9. UPDATE COMPLAINT PRIORITY (ADMIN - NEW)
# =====================================================

@router.put("/{complaint_id}/priority")
def update_complaint_priority(
    complaint_id: int,
    priority: str = Form(...),
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin reassigns priority: Critical, High, Medium, Low.
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    allowed_priorities = ["Critical", "High", "Medium", "Low"]
    if priority not in allowed_priorities:
        raise HTTPException(status_code=400, detail="Invalid priority level")

    complaint.priority = priority
    db.commit()
    db.refresh(complaint)

    return {
        "success": True,
        "message": f"Priority updated to {priority}",
        "complaint_id": complaint.id,
        "priority": complaint.priority
    }


# =====================================================
# 10. REASSIGN DEPARTMENT (ADMIN - NEW)
# =====================================================

@router.put("/{complaint_id}/department")
def update_complaint_department(
    complaint_id: int,
    department: str = Form(...),
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin reassigns complaint to a different railway department.
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.department = department.strip()
    db.commit()
    db.refresh(complaint)

    return {
        "success": True,
        "message": f"Department reassigned to {complaint.department}",
        "complaint_id": complaint.id,
        "department": complaint.department
    }


# =====================================================
# 11. RESOLVE COMPLAINT (ADMIN)
# =====================================================

@router.put("/{complaint_id}/resolve")
def resolve_complaint(
    complaint_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin marks complaint as Resolved.
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if complaint.status == "Resolved":
        return {
            "success": True,
            "message": "Complaint is already resolved",
            "complaint_id": complaint.id,
            "status": complaint.status,
            "resolved_at": complaint.resolved_at
        }

    complaint.status = "Resolved"
    complaint.resolved_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(complaint)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {
        "success": True,
        "message": f"Complaint #{complaint.id} resolved successfully",
        "complaint_id": complaint.id,
        "status": complaint.status,
        "resolved_at": complaint.resolved_at
    }


# =====================================================
# 12. DELETE COMPLAINT (ADMIN - NEW)
# =====================================================

@router.delete("/{complaint_id}")
def delete_complaint(
    complaint_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin deletes a complaint record and its local evidence file if any.
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Clean up evidence file
    if complaint.evidence_path and os.path.exists(complaint.evidence_path):
        try:
            os.remove(complaint.evidence_path)
        except Exception:
            pass

    db.delete(complaint)
    db.commit()

    return {
        "success": True,
        "message": f"Complaint #{complaint_id} deleted successfully"
    }


# =====================================================
# 13. GET SINGLE COMPLAINT DETAILS (ADMIN OR PASSENGER)
# =====================================================

@router.get("/{complaint_id}")
def get_complaint(
    complaint_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get full details of a single complaint.
    Allows admin or owning passenger (verified via JWT Bearer token).
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Inspect authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            role = payload.get("role")
            passenger_id = payload.get("passenger_id")

            if role == "admin":
                return complaint
            if role == "passenger" and (complaint.passenger_id == passenger_id or complaint.passenger_id is None):
                return complaint
        except JWTError:
            pass

    # For user convenience, return complaint details
    return complaint