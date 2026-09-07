from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from dotenv import load_dotenv

import os

from app.services.database import get_db
from app.models.passenger import Passenger


# =====================================================
# JWT SETTINGS
# =====================================================

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"


# =====================================================
# BEARER TOKEN
# =====================================================

security = HTTPBearer()


# =====================================================
# GET LOGGED-IN PASSENGER
# =====================================================

def get_current_passenger(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        # Make sure this is a passenger token
        role = payload.get("role")

        if role != "passenger":
            raise HTTPException(
                status_code=403,
                detail="Passenger access required"
            )

        passenger_id = payload.get("passenger_id")

        if passenger_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token"
        )

    # Find passenger in database
    passenger = (
        db.query(Passenger)
        .filter(Passenger.id == passenger_id)
        .first()
    )

    if passenger is None:
        raise HTTPException(
            status_code=401,
            detail="Passenger account not found"
        )

    return passenger


# =====================================================
# GET LOGGED-IN ADMIN
# =====================================================

def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        # Check admin role
        role = payload.get("role")

        if role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Admin access required"
            )

        username = payload.get("username")

        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid admin authentication token"
            )

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token"
        )

    return {
        "username": username,
        "role": "admin"
    }