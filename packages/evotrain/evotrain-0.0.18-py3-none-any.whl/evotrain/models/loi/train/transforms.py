from torchvision.transforms import v2
from torchvision.transforms.functional import rotate
import torch
import random
import numpy as np


class NumpyToTensor:
    def __call__(self, arr):
        assert isinstance(arr, np.ndarray)
        return torch.tensor(arr)


class Rotate:
    def __init__(self, angle):
        self.angle = angle

    def __call__(self, x):
        return rotate(x, self.angle)


class EvoTransforms(torch.nn.Module):
    def __init__(self, flip_augmentation=True, rotate_augmentation=True):
        super().__init__()

        self.flip_augmentation = flip_augmentation
        self.rotate_augmentation = rotate_augmentation

        self.base_t = [NumpyToTensor()]

        self.flip_t = [
            [v2.RandomHorizontalFlip(p=1)],
            [v2.RandomVerticalFlip(p=1)],
            [v2.RandomHorizontalFlip(p=1), v2.RandomVerticalFlip(p=1)],
            [],
        ]

        self.rotate_t = [[Rotate(90)], [Rotate(-90)], []]

        self.out_t = [v2.ToDtype(torch.float32)]

    def __call__(self, *imgs):
        torch_transforms = self.base_t.copy()

        if self.flip_augmentation:
            torch_transforms.extend(random.choice(self.flip_t))

        if self.rotate_augmentation:
            torch_transforms.extend(random.choice(self.rotate_t))

        torch_transforms += self.out_t

        transforms_compose = v2.Compose(torch_transforms)
        return [transforms_compose(img) for img in imgs]
