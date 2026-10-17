from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
import base64
import os

from app.database import get_db
from app.models import Analysis
from app.file_validators import validate_image
from app.hash_service import generate_sha256
from app.onnx_inference import Cockatoos
from app.ela_service import generate_ela
from app.noise_service import generate_noise
from app.exif_service import extract_exif
from app.pdf_service import build_forensic_pdf
from app.face_service import detect_faces
from app.upload_service import save_uploaded_image
from app.gradcam_service import generate_gradcam
from app.gradcam_marker import mark_gradcam_regions
from app.forensic_explainer import generate_forensic_explanation

router = APIRouter()

model = Cockatoos(onnx_path="export/cockatoos_vitb32_best.onnx")


def to_public_path(path: str | None):
    if not path:
        return None
    return path.replace("app/", "/")


def get_risk_level(fake_probability: float):
    if fake_probability < 0.60:
        return "LOW"
    if fake_probability < 0.80:
        return "MEDIUM"
    return "HIGH"


def build_report_payload(
    *,
    analysis_id,
    filename,
    image_path,
    sha256,
    prediction,
    confidence,
    real_prob,
    fake_prob,
    faces_detected,
    face_results,
    image_width,
    image_height,
    ela_path,
    noise_path,
    gradcam_path,
    marked_gradcam_path,
    exif_data,
):
    most_suspicious = max(face_results, key=lambda x: x["probabilities"]["fake"])

    return {
        "analysis_id": analysis_id,
        "filename": filename,
        "image_path": to_public_path(image_path),
        "prediction": prediction,
        "confidence": confidence,
        "probabilities": {
            "real": real_prob,
            "fake": fake_prob,
        },
        "real_probability": real_prob,
        "fake_probability": fake_prob,
        "faces_detected": faces_detected,
        "selected_face_index": most_suspicious.get("face_index"),
        "selected_face": most_suspicious,
        "face_results": face_results,
        "image_width": image_width,
        "image_height": image_height,
        "sha256": sha256,
        "ela": to_public_path(ela_path),
        "noise": to_public_path(noise_path),
        "gradcam": gradcam_path,
        "marked_gradcam": marked_gradcam_path,
        "exif": exif_data,
        "risk_level": most_suspicious.get("gradcam_explanation", {}).get(
            "risk_level", get_risk_level(fake_prob)
        ),
        "quality": most_suspicious.get("quality", {}),
        "attention_regions": most_suspicious.get("attention_regions", []),
        "gradcam_explanation": most_suspicious.get("gradcam_explanation", {}),
        "forensic_explanation": most_suspicious.get("forensic_explanation", {}),
        "report_sections": {
            "final_verdict": True,
            "probability_breakdown": True,
            "quality_metrics": True,
            "gradcam_evidence": True,
            "attention_regions": True,
            "xai_textual_explanation": True,
            "forensic_explanation": True,
            "audit_trail": True,
        },
    }


@router.post("/predict")
async def predict_image(
    file: UploadFile = File(...),
    user_id: int | None = Form(None),
    allow_multiple_faces: bool = Form(True),
    enable_report_generation: bool = Form(True),
    db: Session = Depends(get_db),
):
    validate_image(file)

    contents = await file.read()
    sha256 = generate_sha256(contents)
    image_path = save_uploaded_image(contents, file.filename)

    faces, image_width, image_height = detect_faces(contents)

    if not faces:
        raise HTTPException(
            status_code=400,
            detail="No human face detected. Please upload a clear image with a visible human face.",
        )

    if len(faces) > 5:
        raise HTTPException(
            status_code=400,
            detail="Too many faces detected. Max supported is 5 faces per image.",
        )

    if not allow_multiple_faces:
        faces = [
            max(
                faces,
                key=lambda face: (
                    (face["bbox"]["x2"] - face["bbox"]["x1"])
                    * (face["bbox"]["y2"] - face["bbox"]["y1"])
                ),
            )
        ]

    face_results = []

    for index, face in enumerate(faces, start=1):
        warnings = face["quality"].get("warnings", [])
        warnings_text = str(warnings).lower()

        if "too dark" in warnings_text or "poorly lit" in warnings_text:
            raise HTTPException(
                status_code=400,
                detail="Face area is too dark or poorly lit. Please upload an image with better lighting.",
            )

        if "overexposed" in warnings_text:
            raise HTTPException(
                status_code=400,
                detail="Face area is overexposed. Please upload an image with normal lighting.",
            )

        if "blurry" in warnings_text:
            raise HTTPException(
                status_code=400,
                detail="Face appears blurry or difficult to recognize. Please upload a sharper image.",
            )

        if "too small" in warnings_text:
            raise HTTPException(
                status_code=400,
                detail="Detected face is too small for reliable analysis. Please upload a clearer close-up image.",
            )

        try:
            result = model.predict_pil(face["crop"])
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Model inference failed. Please try another clear image.",
            )

        target_class = 1 if result["prediction"] == "FAKE" else 0

        try:
            gradcam_path = generate_gradcam(
                face["crop"],
                target_class=target_class,
            )

            marked_result = mark_gradcam_regions(
                gradcam_path=gradcam_path,
                face_image=face["crop"],
            )

            marked_gradcam_path = (
                marked_result["marked_path"] if marked_result else None
            )

            attention_regions = (
                marked_result["regions"] if marked_result else []
            )

            visible_regions = [
                region for region in attention_regions if region.get("bbox")
            ]

            gradcam_explanation = {
                "summary": [
                    f"Model attention was strongest around {visible_regions[0]['label']}."
                    if visible_regions
                    else "No single face-landmark region crossed the marking threshold.",
                    "The marked Grad-CAM regions show where the model focused during prediction.",
                    "These highlighted regions are attention zones, not confirmed manipulated areas.",
                ],
                "regions": {
                    region["label"]: region.get("score", 0)
                    for region in visible_regions
                },
                "top_regions": [
                    [region["label"], region.get("score", 0)]
                    for region in visible_regions
                ],
                "risk_level": get_risk_level(result["probabilities"]["fake"]),
            }

        except Exception:
            gradcam_path = None
            marked_gradcam_path = None
            attention_regions = []

            gradcam_explanation = {
                "summary": ["Grad-CAM explanation unavailable."],
                "regions": {},
                "top_regions": [],
                "risk_level": "UNKNOWN",
            }

        forensic_explanation = generate_forensic_explanation(
            face=face,
            result=result,
            attention_regions=attention_regions,
        )

        face_results.append(
            {
                "face_index": index,
                "bbox": face["bbox"],
                "prediction": result["prediction"],
                "confidence": result["confidence"],
                "probabilities": result["probabilities"],
                "quality": face["quality"],
                "gradcam": to_public_path(gradcam_path),
                "marked_gradcam": to_public_path(marked_gradcam_path),
                "attention_regions": attention_regions,
                "gradcam_explanation": gradcam_explanation,
                "forensic_explanation": forensic_explanation,
            }
        )

    most_suspicious = max(face_results, key=lambda x: x["probabilities"]["fake"])

    prediction = most_suspicious["prediction"]
    confidence = most_suspicious["confidence"]
    real_prob = most_suspicious["probabilities"]["real"]
    fake_prob = most_suspicious["probabilities"]["fake"]
    gradcam_path = most_suspicious.get("gradcam")
    marked_gradcam_path = most_suspicious.get("marked_gradcam")

    ela_path = generate_ela(contents)
    noise_path = generate_noise(contents)
    exif_data = extract_exif(contents)

    analysis = Analysis(
        user_id=user_id,
        filename=file.filename,
        image_path=image_path,
        sha256=sha256,
        prediction=prediction,
        confidence=confidence,
        real_prob=real_prob,
        fake_prob=fake_prob,
        report_path=None,
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    report_payload = build_report_payload(
        analysis_id=analysis.id,
        filename=file.filename,
        image_path=image_path,
        sha256=sha256,
        prediction=prediction,
        confidence=confidence,
        real_prob=real_prob,
        fake_prob=fake_prob,
        faces_detected=len(face_results),
        face_results=face_results,
        image_width=image_width,
        image_height=image_height,
        ela_path=ela_path,
        noise_path=noise_path,
        gradcam_path=gradcam_path,
        marked_gradcam_path=marked_gradcam_path,
        exif_data=exif_data,
    )

    pdf_path = None

    if enable_report_generation:
        try:
            os.makedirs("app/static/reports", exist_ok=True)

            report_name = f"report_{analysis.id}.pdf"
            pdf_path = f"app/static/reports/{report_name}"

            build_forensic_pdf(
                result=report_payload,
                output_path=pdf_path,
                api_base_path="app",
            )

        except Exception as e:
            print("PDF generation failed:", e)
            pdf_path = None

        analysis.report_path = pdf_path
        db.commit()
        db.refresh(analysis)

    image_base64 = base64.b64encode(contents).decode("utf-8")

    response_payload = {
        **report_payload,
        "image": image_base64,
        "report": to_public_path(pdf_path),
        "settings_used": {
            "allow_multiple_faces": allow_multiple_faces,
            "enable_report_generation": enable_report_generation,
        },
    }

    return response_payload