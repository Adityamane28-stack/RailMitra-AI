import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.models.passenger import Passenger
from app.auth.dependencies import get_current_passenger
from app.services.image_ai import analyze_image
from app.services.rail_vision import classify_railway_image
from app.services.audio_ai import analyze_audio
from app.services.video_ai import analyze_video
from app.config import IMAGE_DIR, VIDEO_DIR, AUDIO_DIR

router = APIRouter(prefix="/evidence", tags=["Evidence"])

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/jpg",
    "image/webp"
}

ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/mpeg",
    "video/quicktime",
    "video/webm",
    "video/x-msvideo"
}

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/mp3",
    "audio/webm",
    "audio/ogg",
    "audio/mp4"
}


@router.post("/upload")
async def upload_evidence(
    file: UploadFile = File(...),
    passenger: Passenger = Depends(get_current_passenger)
):
    """
    General multi-format evidence upload endpoint for passengers.
    """
    content_type = file.content_type or ""

    if content_type in ALLOWED_IMAGE_TYPES or file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        evidence_type = "image"
        save_dir = IMAGE_DIR
    elif content_type in ALLOWED_VIDEO_TYPES or file.filename.lower().endswith((".mp4", ".mpeg", ".mov", ".webm", ".avi")):
        evidence_type = "video"
        save_dir = VIDEO_DIR
    elif content_type in ALLOWED_AUDIO_TYPES or file.filename.lower().endswith((".mp3", ".wav", ".ogg", ".webm", ".m4a")):
        evidence_type = "audio"
        save_dir = AUDIO_DIR
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported evidence file format. Supported: JPG, PNG, WEBP, MP4, MOV, WEBM, MP3, WAV"
        )

    original_filename = file.filename or "evidence_file"
    extension = os.path.splitext(original_filename)[1].lower()
    if not extension:
        extension = ".bin"

    saved_filename = f"{uuid.uuid4()}{extension}"
    file_path = str(save_dir / saved_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return {
        "message": "Evidence uploaded successfully",
        "original_filename": original_filename,
        "saved_filename": saved_filename,
        "file_type": content_type,
        "evidence_type": evidence_type,
        "file_path": file_path
    }


@router.post("/analyze-image")
async def analyze_uploaded_image(
    file: UploadFile = File(...),
    passenger: Passenger = Depends(get_current_passenger)
):
    """
    Upload and run AI computer vision analysis on image evidence.
    """
    content_type = file.content_type or ""
    if content_type not in ALLOWED_IMAGE_TYPES and not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        raise HTTPException(
            status_code=400,
            detail="Only image files (JPG, PNG, WEBP) are allowed"
        )

    original_filename = file.filename or "evidence.jpg"
    extension = os.path.splitext(original_filename)[1].lower() or ".jpg"
    saved_filename = f"{uuid.uuid4()}{extension}"
    image_path = str(IMAGE_DIR / saved_filename)

    with open(image_path, "wb") as buffer:
        buffer.write(await file.read())

    # AI analysis
    ai_result = analyze_image(image_path)

    if not ai_result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=ai_result.get("error", "Image AI analysis failed")
        )

    detected_label = ai_result.get("label", "damaged railway coach or equipment")
    confidence = ai_result.get("confidence", 0.85)

    # Railway classification (FIXED BUG: pass 2 args and receive dict)
    railway_result = classify_railway_image(detected_label, confidence)
    category = railway_result.get("category", "Other")
    priority = railway_result.get("priority", "Medium")
    department = railway_result.get("department", "General Complaint")

    return {
        "message": "Image analyzed successfully",
        "file": {
            "original_filename": original_filename,
            "saved_filename": saved_filename,
            "path": image_path
        },
        "ai_analysis": {
            "detected_label": detected_label,
            "confidence": confidence,
            "category": category,
            "priority": priority,
            "department": department
        }
    }


@router.post("/analyze-audio")
async def analyze_uploaded_audio(
    file: UploadFile = File(...),
    passenger: Passenger = Depends(get_current_passenger)
):
    """
    Upload and run AI audio analysis on audio recording evidence.
    """
    content_type = file.content_type or ""
    if content_type not in ALLOWED_AUDIO_TYPES and not file.filename.lower().endswith((".mp3", ".wav", ".ogg", ".webm", ".m4a")):
        raise HTTPException(
            status_code=400,
            detail="Only audio files (MP3, WAV, OGG, WEBM) are allowed"
        )

    original_filename = file.filename or "audio_evidence.mp3"
    extension = os.path.splitext(original_filename)[1].lower() or ".mp3"
    saved_filename = f"{uuid.uuid4()}{extension}"
    audio_path = str(AUDIO_DIR / saved_filename)

    with open(audio_path, "wb") as buffer:
        buffer.write(await file.read())

    ai_result = analyze_audio(audio_path)

    return {
        "message": "Audio analyzed successfully",
        "file": {
            "original_filename": original_filename,
            "saved_filename": saved_filename,
            "path": audio_path
        },
        "ai_analysis": ai_result
    }


@router.post("/analyze-video")
async def analyze_uploaded_video(
    file: UploadFile = File(...),
    passenger: Passenger = Depends(get_current_passenger)
):
    """
    Upload and run AI video frame sampling & classification on video evidence.
    """
    content_type = file.content_type or ""
    if content_type not in ALLOWED_VIDEO_TYPES and not file.filename.lower().endswith((".mp4", ".mpeg", ".mov", ".webm", ".avi")):
        raise HTTPException(
            status_code=400,
            detail="Only video files (MP4, MPEG, MOV, WEBM) are allowed"
        )

    original_filename = file.filename or "video_evidence.mp4"
    extension = os.path.splitext(original_filename)[1].lower() or ".mp4"
    saved_filename = f"{uuid.uuid4()}{extension}"
    video_path = str(VIDEO_DIR / saved_filename)

    with open(video_path, "wb") as buffer:
        buffer.write(await file.read())

    ai_result = analyze_video(video_path)

    if not ai_result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=ai_result.get("error", "Video AI analysis failed")
        )

    return {
        "message": "Video analyzed successfully",
        "file": {
            "original_filename": original_filename,
            "saved_filename": saved_filename,
            "path": video_path
        },
        "video_info": ai_result.get("video_info", {}),
        "ai_analysis": ai_result.get("classification", {}),
        "best_detection": ai_result.get("best_detection", {})
    }