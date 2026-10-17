import os
import uuid

UPLOAD_DIR = "app/static/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_uploaded_image(contents: bytes, original_filename: str) -> str:
    ext = original_filename.split(".")[-1].lower()

    if ext not in ["jpg", "jpeg", "png"]:
        ext = "jpg"

    unique_name = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        f.write(contents)

    return file_path