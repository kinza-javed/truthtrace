import cv2
import numpy as np
import os
import uuid

OUTPUT_DIR = "app/static/forensic_outputs/noise"


def generate_noise(image_bytes: bytes):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    noise = cv2.Laplacian(gray, cv2.CV_64F)
    noise = cv2.convertScaleAbs(noise)

    filename = f"{uuid.uuid4().hex}_noise.jpg"
    path = os.path.join(OUTPUT_DIR, filename)

    cv2.imwrite(path, noise)

    return path