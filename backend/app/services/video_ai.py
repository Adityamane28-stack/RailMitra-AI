import cv2
import os
from PIL import Image
from .image_ai import analyze_image_pil, RAILWAY_LABELS
from .rail_vision import classify_railway_image


def analyze_video(video_path: str):
    """
    Sample video frames, run Computer Vision & AI classification,
    and compute consensus railway issue detection.
    """
    try:
        if not os.path.exists(video_path):
            return {
                "success": False,
                "error": f"Video file not found: {video_path}"
            }

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            return {
                "success": False,
                "error": "Could not open video file"
            }

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 1.0

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if frame_count > 0 else 0

        # Select frames for analysis (up to 5 frames)
        sample_count = 5
        if frame_count > 0:
            sample_count = min(sample_count, frame_count)

        if sample_count <= 1:
            positions = [0]
        else:
            positions = [
                int(i * (frame_count - 1) / (sample_count - 1))
                for i in range(sample_count)
            ]

        frames_analyzed = 0
        brightness_values = []
        all_results = []

        filename = os.path.basename(video_path)

        for pos in positions:
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
            success, frame = cap.read()
            if not success or frame is None:
                continue

            frames_analyzed += 1

            # Brightness check
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness_values.append(float(gray.mean()))

            # Convert to PIL RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)

            # Analyze frame
            analysis = analyze_image_pil(pil_img, filename)
            if analysis.get("success"):
                all_results.append({
                    "label": analysis["label"],
                    "confidence": analysis.get("confidence", 0.8)
                })

        cap.release()

        if frames_analyzed == 0:
            return {
                "success": False,
                "error": "Could not decode any video frames"
            }

        # Find best detection across frames
        if all_results:
            label_scores = {}
            for res in all_results:
                lbl = res["label"]
                score = res["confidence"]
                if lbl not in label_scores:
                    label_scores[lbl] = []
                label_scores[lbl].append(score)

            # Compute average score per label
            avg_scores = {
                lbl: sum(scores) / len(scores)
                for lbl, scores in label_scores.items()
            }
            detected_label = max(avg_scores, key=avg_scores.get)
            confidence = avg_scores[detected_label]
        else:
            detected_label = "general railway video evidence"
            confidence = 0.75

        # Classify railway problem
        rail_class = classify_railway_image(detected_label, confidence)
        category = rail_class["category"]
        priority = rail_class["priority"]
        department = rail_class["department"]

        # Check low brightness override if not an emergency
        avg_brightness = sum(brightness_values) / len(brightness_values) if brightness_values else 100
        if avg_brightness < 45 and priority != "Critical":
            category = "Electrical/Lighting"
            priority = "High"
            department = "Electrical Department"
            detected_label = "dark coach or broken lighting"

        return {
            "success": True,
            "frames_analyzed": frames_analyzed,
            "video_info": {
                "duration_seconds": round(duration, 2),
                "fps": round(fps, 2),
                "width": width,
                "height": height
            },
            "best_detection": {
                "label": detected_label,
                "confidence": round(confidence, 4)
            },
            "classification": {
                "category": category,
                "priority": priority,
                "department": department,
                "confidence": round(confidence, 4)
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }