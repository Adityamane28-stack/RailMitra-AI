from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.sql import func

from app.services.database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)

    # =====================================================
    # PASSENGER ACCOUNT
    # =====================================================

    # Links complaint to the passenger account
    passenger_id = Column(Integer, nullable=True, index=True)

    # Passenger information
    passenger_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)

    # Journey information
    pnr_number = Column(String(20), nullable=True)
    train_number = Column(String(20), nullable=True)
    coach_number = Column(String(20), nullable=True)
    seat_number = Column(String(20), nullable=True)

    # Complaint information
    description = Column(Text, nullable=True)

    # AI classification
    complaint_category = Column(String(100), nullable=True)
    ai_category = Column(String(100), nullable=True)
    ai_confidence = Column(Float, nullable=True)

    # Priority and routing
    priority = Column(String(30), default="Medium")
    department = Column(String(100), nullable=True)

    # Complaint status
    status = Column(String(30), default="Pending")

    # Location
    location = Column(String(255), nullable=True)

    # Evidence
    evidence_type = Column(String(30), nullable=True)
    evidence_path = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    resolved_at = Column(
        DateTime(timezone=True),
        nullable=True
    )