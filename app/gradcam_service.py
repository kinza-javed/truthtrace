import os
import uuid
import torch
import torch.nn as nn
import numpy as np
from PIL import Image

import open_clip
from torchvision import transforms

from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget


GRADCAM_DIR = "app/static/gradcam"
os.makedirs(GRADCAM_DIR, exist_ok=True)


class CockatoosCLIPClassifier(nn.Module):
    def __init__(self, checkpoint_path: str):
        super().__init__()

        self.clip_model = open_clip.create_model(
            "ViT-B-32",
            pretrained="openai"
        )

        embed_dim = self.clip_model.visual.output_dim
        self.classifier = nn.Linear(embed_dim, 2)

        checkpoint = torch.load(checkpoint_path, map_location="cpu")

        if isinstance(checkpoint, dict):
            state_dict = (
                checkpoint.get("model_state_dict")
                or checkpoint.get("state_dict")
                or checkpoint
            )
        else:
            state_dict = checkpoint

        clean_state = {}
        for k, v in state_dict.items():
            new_key = k.replace("module.", "")
            clean_state[new_key] = v

        self.load_state_dict(clean_state, strict=False)
        self.eval()

    def forward(self, x):
        features = self.clip_model.encode_image(x)
        features = features.float()
        logits = self.classifier(features)
        return logits


class CLIPGradCAMService:
    def __init__(self, checkpoint_path: str):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model = CockatoosCLIPClassifier(checkpoint_path)
        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=(0.48145466, 0.4578275, 0.40821073),
                std=(0.26862954, 0.26130258, 0.27577711),
            ),
        ])

        self.target_layers = [
            self.model.clip_model.visual.transformer.resblocks[-1].ln_1
        ]

    def reshape_transform(self, tensor):
        # ViT output: [batch, tokens, channels]
        # remove CLS token
        result = tensor[:, 1:, :]

        # ViT-B/32 uses 7x7 patches for 224 input
        result = result.reshape(tensor.size(0), 7, 7, tensor.size(2))

        # convert to [batch, channels, height, width]
        result = result.permute(0, 3, 1, 2)
        return result

    def generate(self, pil_image: Image.Image, target_class: int | None = None) -> str:
        image = pil_image.convert("RGB").resize((224, 224))

        input_tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(input_tensor)
            predicted_class = int(torch.argmax(logits, dim=1).item())

        if target_class is None:
            target_class = predicted_class

        targets = [ClassifierOutputTarget(target_class)]

        rgb_img = np.array(image).astype(np.float32) / 255.0

        cam = GradCAM(
            model=self.model,
            target_layers=self.target_layers,
            reshape_transform=self.reshape_transform
        )

        grayscale_cam = cam(
            input_tensor=input_tensor,
            targets=targets
        )[0]

        cam_image = show_cam_on_image(
            rgb_img,
            grayscale_cam,
            use_rgb=True
        )

        output_name = f"{uuid.uuid4().hex}.png"
        output_path = os.path.join(GRADCAM_DIR, output_name)

        Image.fromarray(cam_image).save(output_path)

        return output_path


gradcam_service = CLIPGradCAMService(
    checkpoint_path="exports/phase3_best.pt"
)


def generate_gradcam(pil_image: Image.Image, target_class: int | None = None) -> str:
    return gradcam_service.generate(pil_image, target_class)