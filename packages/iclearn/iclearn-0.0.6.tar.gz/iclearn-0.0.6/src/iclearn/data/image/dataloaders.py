import logging
import ssl
from pathlib import Path

import torchvision

from iclearn.data.hitl import HitlSemanticSegmentationTorchDataset


def load_dataset(name: str, cache_dir: Path, transforms):

    # Pytorch endpoint certs not maintained
    # https://github.com/pytorch/pytorch/issues/33288
    ssl._create_default_https_context = ssl._create_unverified_context

    if name == "eurosat":
        logging.info("Loading eurosat dataset")
        dataset = torchvision.datasets.EuroSAT(
            root=cache_dir, transform=transforms, download=True
        )
        logging.info("Finished loading eurosat dataset")
    elif name == "hitl_semantic_segmentation":
        logging.info("Loading hitl_semantic_segmentation dataset")
        dataset = HitlSemanticSegmentationTorchDataset(
            root=cache_dir, transforms=transforms
        )
        dataset.fetch()
        logging.info("Finished hitl_semantic_segmentation dataset")
    else:
        raise RuntimeError(f"Requested dataset name not supported {name}")
