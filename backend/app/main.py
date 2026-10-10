import os
import sys
from pathlib import Path

# =====================================================
# BACKEND PATH
# =====================================================

backend_root = Path(__file__).resolve().parent.parent
project_root = backend_root.parent

if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from dotenv import load_dotenv

from app.config import PORT, HOST, UPLOADS_DIR
from app.services.database import engine, Base

# Database models
from app.models.complaint import Complaint
from app.models.passenger import Passenger

# Routes
from app.routes.complaints import router as complaints_router
from app.routes.evidence import router as evidence_router
from app.routes.admin import router as admin_router
from app.routes.passenger import router as passenger_router

load_dotenv()

# =====================================================
# CREATE DATABASE TABLES
# =====================================================

try:
    Base.metadata.create_all(bind=engine)
except Exception as db_err:
    print(f"[Warning] Table auto-creation: {db_err}")

# =====================================================
# FASTAPI APPLICATION
# =====================================================

app = FastAPI(
    title="RailMitra AI",
    description="AI-powered RailMadad Complaint Management System",
    version="2.0.0"
)

# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:8001",
        "http://localhost:8001",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "null"
    ],
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# UPLOADS / EVIDENCE STATIC MOUNT
# =====================================================

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
app.mount(
    "/uploads",
    StaticFiles(directory=str(UPLOADS_DIR)),
    name="uploads"
)

# =====================================================
# FRONTEND STATIC MOUNT
# =====================================================

frontend_dir = project_root / "frontend"
if frontend_dir.exists():
    app.mount(
        "/frontend",
        StaticFiles(directory=str(frontend_dir)),
        name="frontend"
    )

# =====================================================
# ROUTERS
# =====================================================

app.include_router(complaints_router)
app.include_router(evidence_router)
app.include_router(admin_router)
app.include_router(passenger_router)

# =====================================================
# ROOT & WEB ENTRY
# =====================================================

@app.get("/")
def root():
    index_path = project_root / "frontend" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {
        "message": "RailMitra AI API is running",
        "status": "success",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "RailMitra AI",
        "version": "2.0.0"
    }

@app.get("/database-test")
def database_test():
    try:
        with engine.connect():
            return {
                "database": "connected",
                "status": "success",
                "engine": str(engine.url).split("@")[-1] if "@" in str(engine.url) else "sqlite"
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
        host=HOST,
        port=PORT,
        reload=True
    )