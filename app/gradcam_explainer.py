import cv2
import numpy as np


def _region_score(region):
    if region.size == 0:
        return 0.0
    return float(np.mean(region) / 255.0)


def explain_gradcam(gradcam_path: str):
    img = cv2.imread(gradcam_path)

    if img is None:
        return {
            "summary": ["Grad-CAM explanation unavailable."],
            "regions": {},
            "risk_level": "UNKNOWN"
        }

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    h, w = gray.shape

    forehead = gray[0:int(h * 0.25), :]
    eyes_nose = gray[int(h * 0.25):int(h * 0.60), :]
    mouth_jaw = gray[int(h * 0.60):h, :]
    left_face = gray[:, 0:int(w * 0.33)]
    center_face = gray[:, int(w * 0.33):int(w * 0.66)]
    right_face = gray[:, int(w * 0.66):w]

    regions = {
        "Forehead / Hairline": round(_region_score(forehead) * 100, 2),
        "Eyes / Nose Region": round(_region_score(eyes_nose) * 100, 2),
        "Mouth / Jaw Region": round(_region_score(mouth_jaw) * 100, 2),
        "Left Facial Boundary": round(_region_score(left_face) * 100, 2),
        "Center Facial Texture": round(_region_score(center_face) * 100, 2),
        "Right Facial Boundary": round(_region_score(right_face) * 100, 2),
    }

    sorted_regions = sorted(regions.items(), key=lambda x: x[1], reverse=True)
    top_regions = sorted_regions[:3]

    max_score = top_regions[0][1]

    if max_score >= 70:
        risk_level = "HIGH"
    elif max_score >= 45:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    summary = []

    for region, score in top_regions:
        if score < 25:
            continue

        if "Eyes" in region:
            summary.append(
                f"Strong model attention around the eyes/nose region ({score}%), which may indicate reflection, alignment, or facial feature inconsistencies."
            )
        elif "Mouth" in region:
            summary.append(
                f"Noticeable attention around the mouth/jaw region ({score}%), which may suggest blending, expression, or boundary artifacts."
            )
        elif "Forehead" in region:
            summary.append(
                f"Attention appears around the forehead/hairline region ({score}%), which may relate to texture smoothing or boundary inconsistencies."
            )
        elif "Boundary" in region:
            summary.append(
                f"Attention appears near facial boundary areas ({score}%), which may indicate possible blending artifacts."
            )
        elif "Texture" in region:
            summary.append(
                f"Model attention is concentrated on central facial texture ({score}%), suggesting possible skin texture or pixel-level irregularities."
            )

    if not summary:
        summary.append(
            "Grad-CAM does not show a strong localized activation region. The model decision may be based on distributed facial patterns."
        )

    return {
        "summary": summary,
        "regions": regions,
        "top_regions": top_regions,
        "risk_level": risk_level
    }