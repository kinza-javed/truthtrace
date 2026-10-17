import io
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image


def image_quality_check(face_np):
    gray = cv2.cvtColor(face_np, cv2.COLOR_RGB2GRAY)

    brightness = float(np.mean(gray))
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    warnings = []

    if brightness < 45:
        warnings.append("Face area is too dark or poorly lit.")
    if brightness > 220:
        warnings.append("Face area is overexposed.")
    if blur_score < 25:
        warnings.append("Face appears blurry or difficult to recognize.")

    return {
        "brightness": round(brightness, 2),
        "blur_score": round(blur_score, 2),
        "warnings": warnings
    }


def detect_faces(image_bytes: bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_np = np.array(image)

    h, w, _ = img_np.shape

    mp_face_detection = mp.solutions.face_detection
    detected_faces = []

    with mp_face_detection.FaceDetection(
        model_selection=1,
        min_detection_confidence=0.35
    ) as face_detection:

        results = face_detection.process(img_np)

        if not results.detections:
            return [], w, h

        for index, detection in enumerate(results.detections):
            bbox = detection.location_data.relative_bounding_box

            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            bw = int(bbox.width * w)
            bh = int(bbox.height * h)

            margin = int(0.25 * max(bw, bh))

            x1 = max(0, x - margin)
            y1 = max(0, y - margin)
            x2 = min(w, x + bw + margin)
            y2 = min(h, y + bh + margin)

            face_crop = image.crop((x1, y1, x2, y2))
            face_np = np.array(face_crop)

            quality = image_quality_check(face_np)
            face_area_ratio = ((x2 - x1) * (y2 - y1)) / (w * h)

            if face_area_ratio < 0.015:
                quality["warnings"].append(
                    "Detected face is too small for reliable analysis."
                )

            detected_faces.append({
                "face_index": index + 1,
                "crop": face_crop,
                "bbox": {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2
                },
                "quality": quality
            })

    return detected_faces, w, h