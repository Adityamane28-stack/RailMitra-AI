import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:adi281#2@127.0.0.1:5432/railmitra"
)

# Server configuration
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "127.0.0.1")

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "excellent-railmitra-secret-key-2026")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 120

# Admin default credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Uploads directory
UPLOADS_DIR = BASE_DIR / "uploads"
IMAGE_DIR = UPLOADS_DIR / "images"
VIDEO_DIR = UPLOADS_DIR / "videos"
AUDIO_DIR = UPLOADS_DIR / "audio"

for directory in (IMAGE_DIR, VIDEO_DIR, AUDIO_DIR):
    directory.mkdir(parents=True, exist_ok=True)

