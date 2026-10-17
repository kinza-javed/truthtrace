import os
import uuid
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image

MARKED_DIR = "app/static/gradcam_marked"
os.makedirs(MARKED_DIR, exist_ok=True)

mp_face_mesh = mp.solutions.face_mesh

LANDMARK_GROUPS = {
    "Left Eye Region": [33, 133, 159, 145, 153, 154, 155, 173],
    "Right Eye Region": [362, 263, 386, 374, 380, 381, 382, 398],
    "Nose Bridge Region": [1, 2, 98, 327, 168, 197, 5],
    "Mouth and Lip Region": [61, 291, 13, 14, 17, 0, 78, 308],
    "Jawline Boundary": [152, 172, 136, 150, 149, 176, 400, 379, 365, 397],
    "Left Cheek Texture": [50, 101, 118, 119, 205],
    "Right Cheek Texture": [280, 330, 347, 348, 425],
    "Forehead and Hairline": [10, 67, 109, 151, 338, 297],
}


def _hot_region_mask(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower1 = np.array([0, 70, 110])
    upper1 = np.array([35, 255, 255])

    lower2 = np.array([160, 70, 110])
    upper2 = np.array([179, 255, 255])

    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)

    mask = cv2.bitwise_or(mask1, mask2)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)

    return mask


def _pil_to_cv2(pil_image: Image.Image, size=(224, 224)):
    img = pil_image.convert("RGB").resize(size)
    arr = np.array(img)
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def _landmark_bbox(landmarks, indexes, w, h, pad=8):
    points = []

    for idx in indexes:
        lm = landmarks[idx]
        x = int(lm.x * w)
        y = int(lm.y * h)
        points.append((x, y))

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    x1 = max(min(xs) - pad, 0)
    y1 = max(min(ys) - pad, 0)
    x2 = min(max(xs) + pad, w - 1)
    y2 = min(max(ys) + pad, h - 1)

    return x1, y1, x2, y2


def _face_mask_from_landmarks(landmarks, w, h):
    points = []

    for lm in landmarks:
        x = int(lm.x * w)
        y = int(lm.y * h)
        points.append([x, y])

    points = np.array(points, dtype=np.int32)
    hull = cv2.convexHull(points)

    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillConvexPoly(mask, hull, 255)

    kernel = np.ones((9, 9), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)

    return mask


def _attention_score(mask, face_mask, bbox):
    x1, y1, x2, y2 = bbox

    region = mask[y1:y2, x1:x2]
    face_region = face_mask[y1:y2, x1:x2]

    if region.size == 0:
        return 0.0

    region = cv2.bitwise_and(region, face_region)

    return float(np.mean(region) / 255.0)


def mark_gradcam_regions(gradcam_path: str, face_image: Image.Image):
    heatmap_img = cv2.imread(gradcam_path)

    if heatmap_img is None:
        return None

    heatmap_img = cv2.resize(heatmap_img, (224, 224))
    h, w, _ = heatmap_img.shape

    face_img = _pil_to_cv2(face_image, size=(224, 224))
    rgb_face = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)

    hot_mask = _hot_region_mask(heatmap_img)

    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
    ) as face_mesh:
        results = face_mesh.process(rgb_face)

    if not results.multi_face_landmarks:
        output_name = f"{uuid.uuid4().hex}.png"
        output_path = os.path.join(MARKED_DIR, output_name)
        cv2.imwrite(output_path, heatmap_img)

        return {
            "marked_path": output_path,
            "regions": [
                {
                    "id": "INFO",
                    "label": "Face landmarks were not available, so landmark-based marking was not generated.",
                    "score": 0,
                    "bbox": None,
                    "area": 0,
                }
            ],
        }

    landmarks = results.multi_face_landmarks[0].landmark
    face_mask = _face_mask_from_landmarks(landmarks, w, h)

    # Remove all background activations
    hot_mask = cv2.bitwise_and(hot_mask, face_mask)

    # Darken background outside face
    marked = heatmap_img.copy()
    dark_bg = (marked * 0.35).astype(np.uint8)
    marked = np.where(face_mask[:, :, None] == 255, marked, dark_bg)

    candidates = []
    minimum_display_score = 5

    for label, indexes in LANDMARK_GROUPS.items():
        bbox = _landmark_bbox(landmarks, indexes, w, h)
        score = _attention_score(hot_mask, face_mask, bbox)

        x1, y1, x2, y2 = bbox
        candidates.append(
            {
                "label": label,
                "score": round(score * 100, 2),
                "bbox": {
                    "x": int(x1),
                    "y": int(y1),
                    "width": int(x2 - x1),
                    "height": int(y2 - y1),
                },
                "area": float((x2 - x1) * (y2 - y1)),
            }
        )

    candidates = sorted(candidates, key=lambda item: item["score"], reverse=True)[:3]

    regions = []

    if not candidates:
        regions.append(
            {
                "id": "INFO",
                "label": "No face-landmark region crossed the marking threshold.",
                "score": 0,
                "bbox": None,
                "area": 0,
            }
        )
    elif candidates[0]["score"] < 8:
        regions.append(
            {
                "id": "INFO",
                "label": "Grad-CAM attention was distributed across the face; no strong localized region was found.",
                "score": candidates[0]["score"],
                "bbox": None,
                "area": 0,
            }
        )
    else:
        drawable = [r for r in candidates if r["score"] >= minimum_display_score]

        if not drawable:
            regions.append(
                {
                    "id": "INFO",
                    "label": "Grad-CAM attention was distributed across the face; no strong localized region was found.",
                    "score": candidates[0]["score"],
                    "bbox": None,
                    "area": 0,
                }
            )
        else:
            for i, region in enumerate(drawable, start=1):
                region_id = f"R{i}"
                region["id"] = region_id
                regions.append(region)

                x = region["bbox"]["x"]
                y = region["bbox"]["y"]
                bw = region["bbox"]["width"]
                bh = region["bbox"]["height"]

                cv2.rectangle(marked, (x, y), (x + bw, y + bh), (37, 99, 235), 2)

                tag_x = max(x, 4)
                tag_y = max(y - 26, 4)

                cv2.rectangle(
                    marked,
                    (tag_x, tag_y),
                    (tag_x + 46, tag_y + 24),
                    (37, 99, 235),
                    -1,
                )

                cv2.putText(
                    marked,
                    region_id,
                    (tag_x + 9, tag_y + 17),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.58,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

    output_name = f"{uuid.uuid4().hex}.png"
    output_path = os.path.join(MARKED_DIR, output_name)

    cv2.imwrite(output_path, marked)

    return {
        "marked_path": output_path,
        "regions": regions,
    }