from PIL import Image
import io


def extract_exif(image_bytes: bytes):
    img = Image.open(io.BytesIO(image_bytes))

    exif_data = {}

    if hasattr(img, "_getexif") and img._getexif():
        for tag, value in img._getexif().items():
            exif_data[str(tag)] = str(value)

    return exif_data