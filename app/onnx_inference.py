from __future__ import annotations
from pathlib import Path
import io

import numpy as np
from PIL import Image
import onnxruntime as ort
import torchvision.transforms as T

from .utils import CLIP_MEAN, CLIP_STD, LABEL_MAP, softmax
from ._weights import ensure_weights, KAGGLE_DATASET_DEFAULT

class Cockatoos:
    def __init__(
        self,
        onnx_path: str | Path | None = None,
        kaggle_dataset: str = KAGGLE_DATASET_DEFAULT,
        providers=None,
    ):
        if onnx_path is None:
            onnx_path = ensure_weights(kaggle_dataset=kaggle_dataset)
        self.onnx_path = Path(onnx_path)

        if providers is None:
            providers = ["CPUExecutionProvider"]

        self.session = ort.InferenceSession(str(self.onnx_path), providers=providers)

        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

        self.transform = T.Compose([
            T.Resize((224, 224)),
            T.ToTensor(),
            T.Normalize(mean=CLIP_MEAN, std=CLIP_STD),
        ])

    def _preprocess(self, image_bytes: bytes) -> np.ndarray:
        from .face_crop import crop_face_pil

        img = crop_face_pil(image_bytes)
        x = self.transform(img).unsqueeze(0).numpy()
        return x

    def predict_bytes(self, image_bytes: bytes) -> dict:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        x = self.transform(img).unsqueeze(0).numpy() # (1,3,224,224)
        x = self._preprocess(image_bytes)
        logits = self.session.run([self.output_name], {self.input_name: x})[0]
        probs = softmax(logits)[0]

        idx = int(np.argmax(probs))
        conf = float(probs[idx])

        return {
            "prediction": LABEL_MAP[idx],
            "confidence": round(conf, 4),
            "probabilities": {
                "real": round(float(probs[0]), 4),
                "fake": round(float(probs[1]), 4),
            },
        }

    def predict_pil(self, pil_image) -> dict:
        img = pil_image.convert("RGB")
        x = self.transform(img).unsqueeze(0).numpy()

        logits = self.session.run([self.output_name], {self.input_name: x})[0]
        probs = softmax(logits)[0]

        idx = int(np.argmax(probs))
        conf = float(probs[idx])

        return {
            "prediction": LABEL_MAP[idx],
            "confidence": round(conf, 4),
            "probabilities": {
                "real": round(float(probs[0]), 4),
                "fake": round(float(probs[1]), 4),
            },
        }
