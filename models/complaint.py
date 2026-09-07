from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from datetime import datetime

from app.services.database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # PASSENGER INFORMATION
    # =====================================================

    passenger_name = Column(
        String(100),
        nullable=False
    )

    phone_number = Column(
        String(20),
        nullable=False
    )

    # =====================================================
    # JOURNEY INFORMATION
    # =====================================================

    pnr_number = Column(
        String(20),
        nullable=True
    )

    train_number = Column(
        String(20),
        nullable=True
    )

    coach_number = Column(
        String(20),
        nullable=True
    )

    seat_number = Column(
        String(20),
        nullable=True
    )

    # =====================================================
    # COMPLAINT INFORMATION
    # =====================================================

    description = Column(
        Text,
        nullable=True
    )

    complaint_category = Column(
        String(100),
        nullable=True
    )

    # =====================================================
    # AI INFORMATION
    # =====================================================

    ai_category = Column(
        String(100),
        nullable=True
    )

    ai_confidence = Column(
        Float,
        nullable=True
    )

    # =====================================================
    # COMPLAINT MANAGEMENT
    # =====================================================

    priority = Column(
        String(50),
        nullable=True
    )

    department = Column(
        String(100),
        nullable=True
    )

    status = Column(
        String(50),
        default="Pending",
        nullable=False
    )

    # =====================================================
    # LOCATION
    # =====================================================

    location = Column(
        String(255),
        nullable=True
    )

    # =====================================================
    # EVIDENCE
    # =====================================================

    evidence_type = Column(
        String(50),
        nullable=True
    )

    evidence_path = Column(
        String(500),
        nullable=True
    )

    # =====================================================
    # TIMESTAMPS
    # =====================================================

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    resolved_at = Column(
        DateTime,
        nullable=True
    )