import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.models.passenger import Passenger
from app.auth.dependencies import get_current_passenger, get_current_admin

from app.services.image_ai import analyze_image
from app.services.rail_vision import classify_railway_image
from app.services.audio_ai import analyze_audio
from app.services.video_ai import analyze_video


router = APIRouter(prefix="/evidence", tags=["Evidence"])


# ---------------------------------------------------------
# UPLOAD DIRECTORIES
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

IMAGE_DIR = os.path.join(UPLOAD_DIR, "images")
VIDEO_DIR = os.path.join(UPLOAD_DIR, "videos")
AUDIO_DIR = os.path.join(UPLOAD_DIR, "audio")


os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)


# ---------------------------------------------------------
# ALLOWED FILE TYPES
# ---------------------------------------------------------

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/jpg"
}

ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/mpeg",
    "video/quicktime"
}

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/mp3"
}


# ---------------------------------------------------------
# GENERAL EVIDENCE UPLOAD
# ---------------------------------------------------------

@router.post("/upload")
async def upload_evidence(
    file: UploadFile = File(...),
    passenger: Passenger = Depends(get_current_passenger)
):

    content_type = file.content_type

    if content_type in ALLOWED_IMAGE_TYPES:
        evidence_type = "image"
        save_dir = IMAGE_DIR

    elif content_type in ALLOWED_VIDEO_TYPES:
        evidence_type = "video"
        save_dir = VIDEO_DIR

    elif content_type in ALLOWED_AUDIO_TYPES:
        evidence_type = "audio"
        save_dir = AUDIO_DIR

    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported evidence file type"
        )

    original_filename = file.filename

    extension = os.path.splitext(original_filename)[1]

    saved_filename = f"{uuid.uuid4()}{extension}"

    file_path = os.path.join(
        save_dir,
        saved_filename
    )

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


# ---------------------------------------------------------
# IMAGE AI ANALYSIS
# ---------------------------------------------------------

@router.post("/analyze-image")
async def analyze_uploaded_image(
    file: UploadFile = File(...),
    passenger: Passenger = Depends(get_current_passenger)
):

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed"
        )

    original_filename = file.filename

    extension = os.path.splitext(original_filename)[1]

    saved_filename = f"{uuid.uuid4()}{extension}"

    image_path = os.path.join(
        IMAGE_DIR,
        saved_filename
    )

    with open(image_path, "wb") as buffer:
        buffer.write(await file.read())

    # AI analysis
    ai_result = analyze_image(image_path)

    if not ai_result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=ai_result.get(
                "error",
                "Image AI analysis failed"
            )
        )

    detected_label = ai_result.get("label")
    confidence = ai_result.get("confidence")

    # Railway classification
    category, priority, department = classify_railway_image(
        detected_label
    )

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


# ---------------------------------------------------------
# AUDIO AI ANALYSIS
# ---------------------------------------------------------

@router.post("/analyze-audio")
async def analyze_uploaded_audio(
    file: UploadFile = File(...),
    passenger: Passenger = Depends(get_current_passenger)
):

    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only audio files are allowed"
        )

    original_filename = file.filename

    extension = os.path.splitext(original_filename)[1]

    saved_filename = f"{uuid.uuid4()}{extension}"

    audio_path = os.path.join(
        AUDIO_DIR,
        saved_filename
    )

    with open(audio_path, "wb") as buffer:
        buffer.write(await file.read())

    # AI analysis
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


# ---------------------------------------------------------
# VIDEO AI ANALYSIS
# ---------------------------------------------------------

@router.post("/analyze-video")
async def analyze_uploaded_video(
    file: UploadFile = File(...),
    passenger: Passenger = Depends(get_current_passenger)
):

    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only video files are allowed"
        )

    original_filename = file.filename

    extension = os.path.splitext(original_filename)[1]

    saved_filename = f"{uuid.uuid4()}{extension}"

    video_path = os.path.join(
        VIDEO_DIR,
        saved_filename
    )

    with open(video_path, "wb") as buffer:
        buffer.write(await file.read())

    # AI analysis
    ai_result = analyze_video(video_path)

    if not ai_result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=ai_result.get(
                "error",
                "Video AI analysis failed"
            )
        )

    return {
        "message": "Video analyzed successfully",

        "file": {
            "original_filename": original_filename,
            "saved_filename": saved_filename,
            "path": video_path
        },

        "video_info": ai_result.get(
            "video_info",
            {}
        ),

        "ai_analysis": ai_result.get(
            "classification",
            {}
        ),

        "best_detection": ai_result.get(
            "best_detection",
            {}
        )
    }