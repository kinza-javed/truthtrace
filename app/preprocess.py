import cv2
import numpy as np


def preprocess_image(face_img):
    resized = cv2.resize(face_img, (224, 224))

    # Normalize (0–1)
    img = resized.astype("float32") / 255.0

    # Convert HWC → CHW
    img = np.transpose(img, (2, 0, 1))

    # Add batch dimension
    img = np.expand_dims(img, axis=0)

    return img