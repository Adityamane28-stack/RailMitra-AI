from pydantic import BaseModel
from typing import Optional


class ComplaintCreate(BaseModel):

    passenger_name: str

    phone_number: str

    pnr_number: Optional[str] = None

    train_number: Optional[str] = None

    coach_number: Optional[str] = None

    seat_number: Optional[str] = None

    description: Optional[str] = None

    complaint_category: Optional[str] = None

    priority: Optional[str] = None

    location: Optional[str] = None

    evidence_type: Optional[str] = None

    evidence_path: Optional[str] = None


class ComplaintResponse(BaseModel):

    id: int

    passenger_name: str

    phone_number: str

    pnr_number: Optional[str] = None

    train_number: Optional[str] = None

    coach_number: Optional[str] = None

    seat_number: Optional[str] = None

    description: Optional[str] = None

    complaint_category: Optional[str] = None

    priority: Optional[str] = None

    location: Optional[str] = None

    evidence_type: Optional[str] = None

    evidence_path: Optional[str] = None

    ai_detected_label: Optional[str] = None

    ai_confidence: Optional[float] = None

    ai_department: Optional[str] = None

    ai_processed: Optional[str] = None

    class Config:
        from_attributes = True