import random

import torch
import torchvision.transforms.v2 as v2
import numpy as np
from torchvision.transforms.functional import rotate, affine


class NumpyToTensor:
    def __call__(self, arr):
        return torch.tensor(arr)


class Rotate:
    def __init__(self, angle, fill=-1):
        self.angle = angle
        self.fill = fill

    def __call__(self, x):
        return rotate(x, self.angle, fill=self.fill)


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


class GaussianNoise:
    """Add Gaussian noise to simulate sensor variations."""

    def __init__(self, mean=0, std=0.01):
        self.mean = mean
        self.std = std

    def __call__(self, x):
        noise = torch.randn_like(x) * self.std + self.mean
        return x + noise


class SpectralBlocking:
    """Simulate spectral band blocking or dropout."""

    def __init__(self, block_prob=0.2, num_bands_to_block=1):
        self.block_prob = block_prob
        self.num_bands_to_block = num_bands_to_block

    def __call__(self, x):
        if random.random() < self.block_prob:
            # Create a copy to avoid modifying the original tensor
            x_blocked = x.clone()

            # Randomly select bands to block
            num_bands = x.shape[0]
            bands_to_block = random.sample(
                range(num_bands), min(self.num_bands_to_block, num_bands)
            )

            # Zero out selected bands
            for band in bands_to_block:
                x_blocked[band, :, :] = 0

            return x_blocked
        return x


class ImageTranslation:
    """Perform random image translation to simulate sensor shifts."""

    def __init__(self, max_shift=10):
        self.max_shift = max_shift

    def __call__(self, x):
        # Random shifts in x and y directions
        dx = random.randint(-self.max_shift, self.max_shift)
        dy = random.randint(-self.max_shift, self.max_shift)

        # Use affine transform for translation
        translated = affine(x, angle=0, translate=[dx, dy], scale=1.0, shear=0)
        return translated


class RegionMasking:
    """Mask out random regions of the image."""

    def __init__(self, mask_prob=0.2, max_mask_size=0.2):
        self.mask_prob = mask_prob
        self.max_mask_size = max_mask_size

    def __call__(self, x):
        if random.random() < self.mask_prob:
            # Create a copy to avoid modifying the original tensor
            x_masked = x.clone()

            # Get image dimensions
            C, H, W = x.shape

            # Random mask size (percentage of image)
            mask_height = int(H * random.uniform(0.05, self.max_mask_size))
            mask_width = int(W * random.uniform(0.05, self.max_mask_size))

            # Random starting position for mask
            start_x = random.randint(0, W - mask_width)
            start_y = random.randint(0, H - mask_height)

            # Zero out the region for all channels
            x_masked[
                :, start_y : start_y + mask_height, start_x : start_x + mask_width
            ] = 0

            return x_masked
        return x


class SpectralJittering:
    """Simulate slight spectral variations."""

    def __init__(self, jitter_std=0.05):
        self.jitter_std = jitter_std

    def __call__(self, x):
        # Create multiplicative jitter for each band
        jitter = torch.normal(1.0, self.jitter_std, size=(x.shape[0], 1, 1))
        return x * jitter


class EvoTransforms_v2(torch.nn.Module):
    def __init__(
        self,
        flip_augmentation=True,
        rotate_augmentation=True,
        noise_augmentation=True,
        spectral_augmentation=True,
        translation_augmentation=True,
        masking_augmentation=True,
        fill=-1,
    ):
        super().__init__()

        self.flip_augmentation = flip_augmentation
        self.rotate_augmentation = rotate_augmentation
        self.noise_augmentation = noise_augmentation
        self.spectral_augmentation = spectral_augmentation
        self.translation_augmentation = translation_augmentation
        self.masking_augmentation = masking_augmentation
        self.fill = fill

        self.base_t = [NumpyToTensor()]

        self.flip_t = [
            [v2.RandomHorizontalFlip(p=1)],
            [v2.RandomVerticalFlip(p=1)],
            [v2.RandomHorizontalFlip(p=1), v2.RandomVerticalFlip(p=1)],
            [],
        ]

        self.noise_t = [[GaussianNoise(std=0.01)], [GaussianNoise(std=0.02)], []]

        self.spectral_t = [
            [SpectralBlocking(block_prob=0.2)],
            [SpectralJittering(jitter_std=0.05)],
            [],
        ]

        self.translation_t = [
            [ImageTranslation(max_shift=10)],
            [ImageTranslation(max_shift=20)],
            [],
        ]

        self.masking_t = [
            [RegionMasking(mask_prob=0.2)],
            [RegionMasking(mask_prob=0.3, max_mask_size=0.1)],
            [],
        ]

        self.out_t = [v2.ToDtype(torch.float32)]

    def __call__(self, *imgs):
        torch_transforms = self.base_t.copy()

        if self.flip_augmentation:
            torch_transforms.extend(random.choice(self.flip_t))

        if self.rotate_augmentation:
            deg = random.randrange(-180, 180)
            torch_transforms.extend([Rotate(deg, fill=self.fill)])

        if self.noise_augmentation:
            torch_transforms.extend(random.choice(self.noise_t))

        if self.spectral_augmentation:
            torch_transforms.extend(random.choice(self.spectral_t))

        if self.translation_augmentation:
            torch_transforms.extend(random.choice(self.translation_t))

        if self.masking_augmentation:
            torch_transforms.extend(random.choice(self.masking_t))

        torch_transforms += self.out_t

        transforms_compose = v2.Compose(torch_transforms)

        return [transforms_compose(img) for img in imgs]
