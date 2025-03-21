import os
import json
import requests
from tqdm import tqdm

from rfdetr.config import RFDETRBaseConfig, RFDETRLargeConfig, TrainConfig, ModelConfig
from rfdetr.main import Model
from rfdetr.util.files import download_file
from functools import partial
from logging import getLogger
import torch
import torchvision.transforms.functional as F
from typing import Union
from PIL import Image
import numpy as np
from collections import defaultdict
import supervision as sv

logger = getLogger(__name__)
HOSTED_MODELS = {
    "rf-detr-base.pth": "https://storage.googleapis.com/rfdetr/rf-detr-base-coco.pth",
    # below is a less converged model that may be better for finetuning but worse for inference
    "rf-detr-base-2.pth": "https://storage.googleapis.com/rfdetr/rf-detr-base-2.pth",
    "rf-detr-large.pth": "https://storage.googleapis.com/rfdetr/rf-detr-large.pth"
}

class RFDETR:
    means = [0.485, 0.456, 0.406]
    stds = [0.229, 0.224, 0.225]

    def __init__(self, **kwargs):
        self.model_config = self.get_model_config(**kwargs)
        self.maybe_download_pretrain_weights()
        self.model = self.get_model(self.model_config)
        self.callbacks = defaultdict(list)

    def maybe_download_pretrain_weights(self):
        if self.model_config.pretrain_weights in HOSTED_MODELS:
            if not os.path.exists(self.model_config.pretrain_weights):
                logger.info(
                    f"Downloading pretrained weights for {self.model_config.pretrain_weights}"
                )
                download_file(
                    HOSTED_MODELS[self.model_config.pretrain_weights],
                    self.model_config.pretrain_weights,
                )

    def get_model_config(self, **kwargs):
        return ModelConfig(**kwargs)

    def train(self, **kwargs):
        config = self.get_train_config(**kwargs)
        self.train_from_config(config, **kwargs)

    def train_from_config(self, config: TrainConfig, **kwargs):
        with open(
            os.path.join(config.dataset_dir, "train", "_annotations.coco.json"), "r"
        ) as f:
            anns = json.load(f)
            num_classes = len(anns["categories"])

        if self.model_config.num_classes != num_classes:
            logger.warning(
                f"num_classes mismatch: model has {self.model_config.num_classes} classes, but your dataset has {num_classes} classes\n"
                f"reinitializing your detection head with {num_classes} classes."
            )
            self.model.reinitialize_detection_head(num_classes)
        
        train_config = config.dict()
        model_config = self.model_config.dict()
        model_config.pop("num_classes")
        for k, v in train_config.items():
            if k in model_config:
                model_config.pop(k)
            if k in kwargs:
                kwargs.pop(k)
        

        all_kwargs = {**model_config, **train_config, **kwargs, "num_classes": num_classes}
        

        self.model.train(
            **all_kwargs,
            callbacks=self.callbacks,
        )

    def get_train_config(self, **kwargs):
        return TrainConfig(**kwargs)

    def get_model(self, config: ModelConfig):
        return Model(**config.dict())

    def predict(
        self,
        image_or_path: Union[str, Image.Image, np.ndarray, torch.Tensor],
        threshold: float = 0.5,
        **kwargs,
    ):
        self.model.model.eval()
        with torch.inference_mode():
            if isinstance(image_or_path, str):
                image_or_path = Image.open(image_or_path)
                w, h = image_or_path.size

            if not isinstance(image_or_path, torch.Tensor):
                image = F.to_tensor(image_or_path)
                _, h, w = image.shape
            else:
                logger.warning(
                    "image_or_path is a torch.Tensor\n",
                    "we expect an image divided by 255 at (C, H, W)",
                )
                assert image_or_path.shape[0] == 3, "image must have 3 channels"
                h, w = image_or_path.shape[1:]

            image = image.to(self.model.device)
            image = F.normalize(image, self.means, self.stds)
            image = F.resize(image, (self.model.resolution, self.model.resolution))

            predictions = self.model.model.forward(image[None, :])
            bboxes = predictions["pred_boxes"]
            results = self.model.postprocessors["bbox"](
                predictions,
                target_sizes=torch.tensor([[h, w]], device=self.model.device),
            )
            scores, labels, boxes = [], [], []
            for result in results:
                scores.append(result["scores"])
                labels.append(result["labels"])
                boxes.append(result["boxes"])

            scores = torch.stack(scores)
            labels = torch.stack(labels)
            boxes = torch.stack(boxes)

            keep_inds = scores > threshold
            boxes = boxes[keep_inds]
            labels = labels[keep_inds]
            scores = scores[keep_inds]
            detections = sv.Detections(
                xyxy=boxes.cpu().numpy(),
                class_id=labels.cpu().numpy(),
                confidence=scores.cpu().numpy(),
            )
            return detections


class RFDETRBase(RFDETR):
    def get_model_config(self, **kwargs):
        return RFDETRBaseConfig(**kwargs)

    def get_train_config(self, **kwargs):
        return TrainConfig(**kwargs)

class RFDETRLarge(RFDETR):
    def get_model_config(self, **kwargs):
        return RFDETRLargeConfig(**kwargs)

    def get_train_config(self, **kwargs):
        return TrainConfig(**kwargs)
