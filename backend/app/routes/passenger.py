from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session

from app.services.database import get_db
from app.models.passenger import Passenger
from app.auth.dependencies import get_current_passenger

from dotenv import load_dotenv
from jose import jwt
import bcrypt
import os
from datetime import datetime, timedelta


# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY is not set in the .env file")

JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60


# =====================================================
# ROUTER
# =====================================================

router = APIRouter(
    prefix="/passenger",
    tags=["Passenger"]
)


# =====================================================
# CREATE JWT TOKEN
# =====================================================

def create_access_token(passenger_id: int, username: str):

    expire = datetime.utcnow() + timedelta(
        minutes=TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "passenger_id": passenger_id,
        "username": username,
        "role": "passenger",
        "exp": expire
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token


# =====================================================
# PASSENGER REGISTRATION
# =====================================================

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
        raise HTTPException(
            status_code=400,
            detail="Username is required"
        )

    if not password:
        raise HTTPException(
            status_code=400,
            detail="Password is required"
        )

    if not passenger_name:
        raise HTTPException(
            status_code=400,
            detail="Passenger name is required"
        )

    if not phone_number:
        raise HTTPException(
            status_code=400,
            detail="Phone number is required"
        )

    if len(password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password must be 72 bytes or less"
        )

    existing_passenger = (
        db.query(Passenger)
        .filter(Passenger.username == username)
        .first()
    )

    if existing_passenger:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

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


# =====================================================
# PASSENGER LOGIN
# =====================================================

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
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    password_correct = bcrypt.checkpw(
        password.encode("utf-8"),
        passenger.password.encode("utf-8")
    )

    if not password_correct:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Create secure login token
    access_token = create_access_token(
        passenger.id,
        passenger.username
    )

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
# =====================================================
# TEST CURRENT PASSENGER
# =====================================================

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