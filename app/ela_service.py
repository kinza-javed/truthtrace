from PIL import Image, ImageChops, ImageEnhance
import io
import os
import uuid

OUTPUT_DIR = "app/static/forensic_outputs/ela"


def generate_ela(image_bytes: bytes):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    original = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    temp_path = f"{OUTPUT_DIR}/temp.jpg"
    original.save(temp_path, "JPEG", quality=90)

    compressed = Image.open(temp_path)

    ela_image = ImageChops.difference(original, compressed)

    extrema = ela_image.getextrema()
    max_diff = max([ex[1] for ex in extrema])

    scale = 255.0 / max_diff if max_diff != 0 else 1

    ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)

    filename = f"{uuid.uuid4().hex}_ela.jpg"
    output_path = os.path.join(OUTPUT_DIR, filename)

    ela_image.save(output_path)

    return output_path