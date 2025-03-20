# This library does unsolicited update checks, until
# we remove this library disable this horrible 'feature'
import os

os.environ["NO_ALBUMENTATIONS_UPDATE"] = "1"  # NOQA
import albumentations as A  # NOQA
from albumentations.pytorch import ToTensorV2  # NOQA

from torchvision import transforms as tfs  # NOQA

ZEROS = [0.0, 0.0, 0.0]
ONES = [1.0, 1.0, 1.0]


def resize(size):
    return tfs.Compose([tfs.Resize(size), tfs.ToTensor()])


class ImageNormalTransform:
    def __init__(self, mean, std, size, scale=255) -> None:
        self.mean = mean
        self.std = std
        self.size = size
        self.scale = scale

    def transform_func(self):
        return A.Compose(
            [
                A.Resize(self.size[1], self.size[0]),
                A.augmentations.transforms.Normalize(mean=self.mean, std=self.std),
                ToTensorV2(transpose_mask=True),
            ]
        )

    def inverse(self):
        return tfs.Compose(
            [
                tfs.Normalize(mean=ZEROS, std=self._invert(self.std)),
                tfs.Normalize(mean=self._flip(self.mean), std=ONES),
            ]
        )

    def _invert(self, t):
        return [1 / t[0], 1 / t[1], 1 / t[2]]

    def _flip(self, t):
        return [-t[0], -t[1], -t[2]]
