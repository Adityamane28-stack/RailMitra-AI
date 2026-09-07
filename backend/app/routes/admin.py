from fastapi import APIRouter, Form
from dotenv import load_dotenv
from jose import jwt

import os
from datetime import datetime, timedelta


load_dotenv()


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# TEMPORARY ADMIN CREDENTIALS
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# JWT SETTINGS
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY is not set in the .env file")

JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60


def create_admin_access_token(username: str):

    expire = datetime.utcnow() + timedelta(
        minutes=TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "username": username,
        "role": "admin",
        "exp": expire
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token


@router.post("/login")
def admin_login(
    username: str = Form(...),
    password: str = Form(...)
):

    if (
        username == ADMIN_USERNAME
        and password == ADMIN_PASSWORD
    ):

        access_token = create_admin_access_token(username)

        return {
            "success": True,
            "message": "Admin login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "role": "admin"
        }

    return {
        "success": False,
        "message": "Invalid username or password"
    }