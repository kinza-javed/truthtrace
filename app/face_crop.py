import io
import cv2
import numpy as np
from PIL import Image
from fastapi import HTTPException


def crop_face_pil(image_bytes: bytes) -> Image.Image:
    pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = np.array(pil_img)

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(60, 60)
    )

    if len(faces) == 0:
        raise HTTPException(status_code=400, detail="No face detected in image")

    x, y, w, h = max(faces, key=lambda box: box[2] * box[3])

    margin = int(0.25 * w)

    x1 = max(0, x - margin)
    y1 = max(0, y - margin)
    x2 = min(img.shape[1], x + w + margin)
    y2 = min(img.shape[0], y + h + margin)

    cropped = pil_img.crop((x1, y1, x2, y2))

    return cropped