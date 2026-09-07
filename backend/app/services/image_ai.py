from PIL import Image
from transformers import pipeline


# =====================================================
# RAILMITRA AI IMAGE CLASSIFIER
# =====================================================

image_classifier = pipeline(
    "zero-shot-image-classification",
    model="openai/clip-vit-base-patch32"
)


# =====================================================
# RAILWAY COMPLAINT LABELS
# =====================================================

RAILWAY_LABELS = [
    "dirty railway toilet",
    "clean railway toilet",
    "garbage inside railway coach",
    "garbage at railway station",
    "damaged railway seat",
    "broken railway seat",
    "damaged railway window",
    "broken railway window",
    "water leakage inside railway coach",
    "dirty railway coach",
    "clean railway coach",
    "broken railway fan",
    "broken railway light",
    "railway electrical problem",
    "damaged railway equipment",
    "railway track problem",
    "crowded railway platform",
    "railway platform",
    "railway train",
    "food or catering problem",
    "other railway problem"
]


# =====================================================
# ANALYZE IMAGE
# =====================================================

def analyze_image(image_path: str):

    try:

        # ---------------------------------------------
        # Open image
        # ---------------------------------------------

        image = Image.open(image_path).convert("RGB")


        # ---------------------------------------------
        # Run zero-shot AI classification
        # ---------------------------------------------

        results = image_classifier(
            image,
            candidate_labels=RAILWAY_LABELS
        )


        # ---------------------------------------------
        # Get highest-confidence result
        # ---------------------------------------------

        best_result = results[0]

        label = best_result["label"]

        confidence = float(
            best_result["score"]
        )


        # ---------------------------------------------
        # Return AI result
        # ---------------------------------------------

        return {

            "success": True,

            "label": label,

            "confidence": round(
                confidence,
                4
            )

        }


    except Exception as e:

        return {

            "success": False,

            "error": str(e)

        }