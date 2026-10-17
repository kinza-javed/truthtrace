from pathlib import Path

KAGGLE_DATASET_DEFAULT = ""

def ensure_weights(kaggle_dataset: str = ""):
    return Path("export/cockatoos_vitb32_best.onnx")