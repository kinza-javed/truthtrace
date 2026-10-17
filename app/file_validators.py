from fastapi import UploadFile, HTTPException
from PIL import Image
import io

ALLOWED_TYPES = ["image/jpeg", "image/png"]
MAX_SIZE_MB = 5
MIN_WIDTH = 100
MIN_HEIGHT = 100


def validate_image(file: UploadFile):
    # ❌ Wrong file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported format. Only JPG and PNG allowed."
        )

    contents = file.file.read()

    # ❌ File too large
    if len(contents) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Image too large. Max size is 5MB."
        )

    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()  # detect corrupted/fake image
    except:
        raise HTTPException(
            status_code=400,
            detail="Invalid or corrupted image file."
        )

    # reopen (verify() closes image)
    image = Image.open(io.BytesIO(contents))

    # ❌ Too small
    if image.width < MIN_WIDTH or image.height < MIN_HEIGHT:
        raise HTTPException(
            status_code=400,
            detail="Image too small. Minimum size is 100x100."
        )

    file.file.seek(0)  # reset pointer