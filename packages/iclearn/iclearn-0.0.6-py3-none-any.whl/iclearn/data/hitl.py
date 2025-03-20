import glob
import cv2
from torch.utils.data import Dataset


class HitlSemanticSegmentationTorchDataset(Dataset):
    def __init__(self, root, transforms=None):
        self.image_paths = sorted(glob(f"{root}/*/images/*.jpg"))
        self.ground_truth_paths = sorted(glob(f"{root}/*/masks/*.png"))
        self.transforms = transforms
        self.num_classes = 5
        assert len(self.image_paths) == len(self.ground_truth_paths)

    def load(self):
        pass

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        im, gt = self.get_image_ground_truth(
            self.image_paths[idx], self.ground_truth_paths[idx]
        )
        if self.transforms:
            im, gt = self.apply_transformations(im, gt)
        return im, gt

    def get_image_ground_truth(self, im_path, gt_path):
        return self.read_image(im_path), self.read_image(gt_path)

    def read_image(self, path):
        return cv2.cvtColor(cv2.imread(path, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)

    def apply_transformations(self, im, gt):
        transformed = self.transforms(image=im, mask=gt)
        return transformed["image"], transformed["mask"]
