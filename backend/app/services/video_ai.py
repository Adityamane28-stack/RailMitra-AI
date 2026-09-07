import cv2
from PIL import Image

from .image_ai import image_classifier, RAILWAY_LABELS


def analyze_video(video_path: str):

    try:

        print("Opening video...")

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            return {
                "success": False,
                "error": "Could not open video"
            }

        # -----------------------------------------
        # Get video information
        # -----------------------------------------

        fps = cap.get(cv2.CAP_PROP_FPS)

        if fps <= 0:
            fps = 1.0

        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        width = int(
            cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        )

        height = int(
            cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )

        duration = 0

        if frame_count > 0:
            duration = frame_count / fps

        # -----------------------------------------
        # Select frames for AI analysis
        # -----------------------------------------

        sample_count = 5

        if frame_count > 0:
            sample_count = min(
                sample_count,
                int(frame_count)
            )

        positions = []

        if sample_count == 1:

            positions = [0]

        elif sample_count > 1:

            positions = [
                int(
                    i * (frame_count - 1)
                    / (sample_count - 1)
                )
                for i in range(sample_count)
            ]

        # -----------------------------------------
        # Analyze video frames
        # -----------------------------------------

        frames_analyzed = 0
        brightness_values = []
        all_results = []

        for position in positions:

            cap.set(
                cv2.CAP_PROP_POS_FRAMES,
                position
            )

            success, frame = cap.read()

            if not success:
                continue

            frames_analyzed += 1

            # -------------------------------------
            # Calculate brightness
            # -------------------------------------

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            brightness_values.append(
                float(gray.mean())
            )

            # -------------------------------------
            # Convert frame to PIL image
            # -------------------------------------

            frame_rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            image = Image.fromarray(frame_rgb)

            # -------------------------------------
            # Run CLIP AI
            # -------------------------------------

            results = image_classifier(
                image,
                candidate_labels=RAILWAY_LABELS
            )

            if results:

                best_result = results[0]

                all_results.append({
                    "label": best_result["label"],
                    "confidence": float(
                        best_result["score"]
                    )
                })

        # -----------------------------------------
        # Release video
        # -----------------------------------------

        cap.release()

        # -----------------------------------------
        # Check if frames were analyzed
        # -----------------------------------------

        if frames_analyzed == 0:

            return {
                "success": False,
                "error": "Could not read any video frames"
            }

        # -----------------------------------------
        # Find most consistent AI detection
        # -----------------------------------------

        if all_results:

            label_scores = {}

            for result in all_results:

                label = result["label"]
                score = result["confidence"]

                if label not in label_scores:
                    label_scores[label] = []

                label_scores[label].append(score)

            # Calculate average confidence
            # for every detected label

            average_scores = {}

            for label, scores in label_scores.items():

                average_scores[label] = (
                    sum(scores) / len(scores)
                )

            # Select label with highest
            # average confidence

            detected_label = max(
                average_scores,
                key=average_scores.get
            )

            confidence = average_scores[
                detected_label
            ]

        else:

            detected_label = "railway complaint video"
            confidence = 0.0

        # -----------------------------------------
        # Default classification
        # -----------------------------------------

        category = "Video Evidence"
        priority = "Medium"
        department = "General Complaint"

        # -----------------------------------------
        # Map CLIP label to RailMitra category
        # -----------------------------------------

        label = detected_label.lower()

        # Cleanliness
        if (
            "dirty railway toilet" in label
            or "garbage inside railway coach" in label
            or "garbage at railway station" in label
            or "dirty railway coach" in label
        ):

            category = "Cleanliness"
            priority = "High"
            department = "Housekeeping"

        # Clean toilet / coach
        elif (
            "clean railway toilet" in label
            or "clean railway coach" in label
        ):

            category = "Cleanliness"
            priority = "Low"
            department = "Housekeeping"

        # Water leakage
        elif "water leakage" in label:

            category = "Water Leakage"
            priority = "High"
            department = "Coach Maintenance"

        # Seat problem
        elif (
            "damaged railway seat" in label
            or "broken railway seat" in label
        ):

            category = "Coach/Seat Issue"
            priority = "Medium"
            department = "Coach Maintenance"

        # Window problem
        elif (
            "damaged railway window" in label
            or "broken railway window" in label
        ):

            category = "Coach/Window Issue"
            priority = "High"
            department = "Coach Maintenance"

        # Fan / light / electrical
        elif (
            "broken railway fan" in label
            or "broken railway light" in label
            or "railway electrical problem" in label
        ):

            category = "Electrical Issue"
            priority = "High"
            department = "Electrical Department"

        # Track
        elif "railway track problem" in label:

            category = "Track Issue"
            priority = "Critical"
            department = "Track Maintenance"

        # Food / catering
        elif "food or catering problem" in label:

            category = "Food/Catering"
            priority = "Medium"
            department = "Catering Department"

        # Platform
        elif (
            "crowded railway platform" in label
            or "railway platform" in label
        ):

            category = "Platform Issue"
            priority = "Medium"
            department = "Station Management"

        # Damaged equipment
        elif "damaged railway equipment" in label:

            category = "Equipment Issue"
            priority = "High"
            department = "Coach Maintenance"

        # Train
        elif "railway train" in label:

            category = "General Railway Issue"
            priority = "Medium"
            department = "General Complaint"

        # -----------------------------------------
        # Brightness analysis
        # -----------------------------------------

        average_brightness = 0

        if brightness_values:

            average_brightness = (
                sum(brightness_values)
                / len(brightness_values)
            )

        # Only classify as lighting issue when
        # CLIP has not detected another problem

        if (
            average_brightness < 50
            and category == "Video Evidence"
        ):

            category = "Lighting Issue"
            priority = "Medium"
            department = "Electrical Department"

        # -----------------------------------------
        # Final result
        # -----------------------------------------

        return {

            "success": True,

            "frames_analyzed": frames_analyzed,

            "video_info": {

                "duration_seconds": round(
                    duration,
                    2
                ),

                "fps": round(
                    fps,
                    2
                ),

                "width": width,

                "height": height
            },

            "best_detection": {

                "label": detected_label,

                "confidence": round(
                    confidence,
                    4
                )
            },

            "classification": {

                "category": category,

                "priority": priority,

                "department": department,

                "confidence": round(
                    confidence,
                    4
                )
            }

        }

    except Exception as e:

        return {

            "success": False,

            "error": str(e)
        }