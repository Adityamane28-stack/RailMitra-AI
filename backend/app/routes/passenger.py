from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import bcrypt
from jose import jwt

from app.services.database import get_db
from app.models.passenger import Passenger
from app.auth.dependencies import get_current_passenger
from app.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    TOKEN_EXPIRE_MINUTES
)

router = APIRouter(
    prefix="/passenger",
    tags=["Passenger"]
)


def create_access_token(passenger_id: int, username: str):
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    payload = {
        "passenger_id": passenger_id,
        "username": username,
        "role": "passenger",
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


@router.post("/register")
def register_passenger(
    username: str = Form(...),
    password: str = Form(...),
    passenger_name: str = Form(...),
    phone_number: str = Form(...),
    db: Session = Depends(get_db)
):
    username = username.strip()
    passenger_name = passenger_name.strip()
    phone_number = phone_number.strip()

    if not username:
        raise HTTPException(status_code=400, detail="Username is required")
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")
    if not passenger_name:
        raise HTTPException(status_code=400, detail="Passenger name is required")
    if not phone_number:
        raise HTTPException(status_code=400, detail="Phone number is required")

    if len(password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password must be 72 bytes or less")

    existing_passenger = (
        db.query(Passenger)
        .filter(Passenger.username == username)
        .first()
    )

    if existing_passenger:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    passenger = Passenger(
        username=username,
        password=hashed_password,
        passenger_name=passenger_name,
        phone_number=phone_number
    )

    db.add(passenger)
    db.commit()
    db.refresh(passenger)

    return {
        "success": True,
        "message": "Passenger account created successfully",
        "passenger_id": passenger.id,
        "username": passenger.username
    }


@router.post("/login")
def passenger_login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    username = username.strip()

    passenger = (
        db.query(Passenger)
        .filter(Passenger.username == username)
        .first()
    )

    if not passenger:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    password_correct = bcrypt.checkpw(
        password.encode("utf-8"),
        passenger.password.encode("utf-8")
    )

    if not password_correct:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(passenger.id, passenger.username)

    return {
        "success": True,
        "message": "Passenger login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "passenger_id": passenger.id,
        "username": passenger.username,
        "passenger_name": passenger.passenger_name,
        "phone_number": passenger.phone_number
    }


@router.get("/me")
def get_my_profile(
    current_passenger: Passenger = Depends(get_current_passenger)
):
    return {
        "success": True,
        "passenger_id": current_passenger.id,
        "username": current_passenger.username,
        "passenger_name": current_passenger.passenger_name,
        "phone_number": current_passenger.phone_number
    }


@router.put("/profile")
def update_my_profile(
    passenger_name: str = Form(...),
    phone_number: str = Form(...),
    current_passenger: Passenger = Depends(get_current_passenger),
    db: Session = Depends(get_db)
):
    current_passenger.passenger_name = passenger_name.strip()
    current_passenger.phone_number = phone_number.strip()
    db.commit()
    db.refresh(current_passenger)

    return {
        "success": True,
        "message": "Profile updated successfully",
        "passenger_id": current_passenger.id,
        "passenger_name": current_passenger.passenger_name,
        "phone_number": current_passenger.phone_number
    }