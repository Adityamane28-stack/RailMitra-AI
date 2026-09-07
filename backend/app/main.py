import os
import sys
from pathlib import Path

# =====================================================
# BACKEND PATH
# =====================================================

backend_root = Path(__file__).resolve().parent.parent

if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))


# =====================================================
# IMPORTS
# =====================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from app.services.database import engine, Base

# Database models
from app.models.complaint import Complaint
from app.models.passenger import Passenger

# Routes
from app.routes.complaints import router as complaints_router
from app.routes.evidence import router as evidence_router
from app.routes.admin import router as admin_router
from app.routes.passenger import router as passenger_router

# =====================================================
# ENVIRONMENT
# =====================================================

load_dotenv()


# =====================================================
# CREATE DATABASE TABLES
# =====================================================

Base.metadata.create_all(bind=engine)


# =====================================================
# FASTAPI APPLICATION
# =====================================================

app = FastAPI(
    title="RailMitra AI",
    description="AI-powered RailMadad Complaint Management System",
    version="1.0.0"
)


# =====================================================
# UPLOADS / EVIDENCE IMAGES
# =====================================================

UPLOADS_DIR = backend_root / "uploads"

# Create uploads folder if it doesn't exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Make uploaded files accessible through the browser
app.mount(
    "/uploads",
    StaticFiles(directory=str(UPLOADS_DIR)),
    name="uploads"
)


# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8001",
        "http://localhost:8001"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =====================================================
# ROUTERS
# =====================================================

app.include_router(complaints_router)

app.include_router(evidence_router)

app.include_router(admin_router)

app.include_router(passenger_router)
# =====================================================
# ROOT
# =====================================================

@app.get("/")
def root():

    return {
        "message": "RailMitra AI API is running",
        "status": "success"
    }


# =====================================================
# HEALTH
# =====================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# =====================================================
# DATABASE TEST
# =====================================================

@app.get("/database-test")
def database_test():

    try:

        with engine.connect():

            return {
                "database": "connected",
                "status": "success"
            }

    except Exception as e:

        return {
            "database": "connection failed",
            "error": str(e)
        }


# =====================================================
# RUN SERVER
# =====================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True
    )