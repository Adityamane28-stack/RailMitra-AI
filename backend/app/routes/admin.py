from fastapi import APIRouter, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date

from app.auth.dependencies import get_current_admin
from app.services.database import get_db
from app.models.complaint import Complaint
from app.config import (
    ADMIN_USERNAME,
    ADMIN_PASSWORD,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    TOKEN_EXPIRE_MINUTES
)
from jose import jwt

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


def create_admin_access_token(username: str):
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    payload = {
        "username": username,
        "role": "admin",
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


@router.post("/login")
def admin_login(
    username: str = Form(...),
    password: str = Form(...)
):
    """
    Authenticate Railway Admin and return JWT Bearer token.
    """
    username = username.strip()

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        access_token = create_admin_access_token(username)
        return {
            "success": True,
            "message": "Admin login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "role": "admin",
            "username": username
        }

    return {
        "success": False,
        "message": "Invalid username or password"
    }


@router.get("/me")
def get_admin_profile(
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get profile of logged-in admin.
    """
    return {
        "success": True,
        "username": current_admin["username"],
        "role": "admin"
    }


@router.get("/stats")
def get_admin_stats(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get advanced operational metrics, resolution rates, and department analytics.
    """
    total = db.query(Complaint).count()
    pending = db.query(Complaint).filter(Complaint.status == "Pending").count()
    in_progress = db.query(Complaint).filter(Complaint.status == "In Progress").count()
    resolved = db.query(Complaint).filter(Complaint.status == "Resolved").count()

    critical = db.query(Complaint).filter(Complaint.priority == "Critical").count()
    high = db.query(Complaint).filter(Complaint.priority == "High").count()
    medium = db.query(Complaint).filter(Complaint.priority == "Medium").count()
    low = db.query(Complaint).filter(Complaint.priority == "Low").count()

    today_date = date.today()
    today_count = db.query(Complaint).filter(Complaint.created_at >= today_date).count()

    resolution_rate = round((resolved / total * 100), 1) if total > 0 else 100.0

    all_complaints = db.query(Complaint).all()
    departments = {}
    categories = {}

    for c in all_complaints:
        dep = c.department or "Unassigned"
        departments[dep] = departments.get(dep, 0) + 1

        cat = c.complaint_category or "Other"
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "success": True,
        "total_complaints": total,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
        "today_complaints": today_count,
        "resolution_rate_percent": resolution_rate,
        "department_distribution": departments,
        "category_distribution": categories
    }