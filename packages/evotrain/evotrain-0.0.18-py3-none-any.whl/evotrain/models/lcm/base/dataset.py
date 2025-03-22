import json
import random
from pathlib import Path

import numpy as np
import torch
import xarray as xr
from torch.utils.data import DataLoader, Dataset
from torchvision.transforms import v2
from torchvision.transforms.functional import rotate

from evotrain.models.lcm10.v12 import (
    DEFAULT_AUX_BANDS,
    DEFAULT_BANDS,
    NET_LABELS,
)
from evotrain.v2 import EvoTrainV2Dataset
from evotrain.v2.bands import BANDS_V2_S2_FEATS


class NumpyToTensor:
    def __call__(self, arr):
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


def logistic(x, L=1, k=3.60, x0=0, y0=-0.5, s=2):
    return (L / (1 + np.exp(-k * (x - x0))) + y0) * s


def random_jitter(n):
    return random.uniform(-n, n)


def apply_augmented_scaling(
    *darrs,
    k_factor=5,
    k_factor_jitter=2,
    lat_lon_jitter=1,
):
    k_noised_signal = k_factor + random_jitter(k_factor_jitter)
    k_noised_dem = k_factor + random_jitter(k_factor_jitter)
    lat_jitter = random_jitter(lat_lon_jitter)
    lon_jitter = random_jitter(lat_lon_jitter)

    out_darrs = [
        _apply_augmented_scaling(
            darr, k_noised_signal, k_noised_dem, lat_jitter, lon_jitter
        )
        for darr in darrs
    ]

    if len(darrs) == 1:
        out_darrs = out_darrs[0]

    return out_darrs


def _apply_augmented_scaling(
    darr, k_noised_signal, k_noised_dem, lat_jitter, lon_jitter
):
    dem_scaling = 4000
    lat_scaling = 90
    lon_scaling = 180

    # distinguish on bands that require special scaling
    signal_bands = [b for b in darr.band.values if b in BANDS_V2_S2_FEATS]

    # we rescale the dem band by 4000 as upper limit for high altitudes
    # we then apply the logistic scaling to it as well
    dem_band = ["cop-DEM-alt"] if "cop-DEM-alt" in darr.band.values else None  # noqa: E501
    lat_band = ["lat"] if "lat" in darr.band.values else None
    lon_band = ["lon"] if "lon" in darr.band.values else None

    # we rescale lat lon bands between their ranges, no logistic scaling
    darr_signal = darr.sel(band=signal_bands)
    if k_noised_signal > 0:
        darr_signal = logistic(darr_signal, k=k_noised_signal)

    darr_dem = (
        darr.sel(band=dem_band) / dem_scaling if dem_band is not None else None
    )
    if (k_noised_dem > 0) and (dem_band is not None):
        darr_dem = logistic(darr_dem, k=k_noised_dem)

    darr_lat = (
        (darr.sel(band=["lat"]) + lat_jitter) / lat_scaling
        if lat_band is not None
        else None
    )
    darr_lon = (
        (darr.sel(band=["lon"]) + lon_jitter) / lon_scaling
        if lon_band is not None
        else None
    )

    darrs = [
        d for d in (darr_signal, darr_dem, darr_lat, darr_lon) if d is not None
    ]

    if len(darrs) > 1:
        darr = xr.concat(darrs, dim="band")
    else:
        darr = darrs[0]

    return darr


def label_to_probs(
    label,
    classes,
    soft_labels_mapping=None,
    soft_labels_weight=1,
    normalize=True,
):
    """Transform a 2-D label array in a 3D target probs array"""

    probs = np.zeros(
        (len(classes), label.shape[0], label.shape[1]), dtype=np.float32
    )

    classes_idx = {ind: lab for ind, lab in enumerate(classes)}

    for ind, lab in classes_idx.items():
        mask = label == lab
        probs[ind, :, :] += mask

        if soft_labels_mapping is not None:
            for soft_lab, soft_prob in soft_labels_mapping.get(
                lab, {}
            ).items():  # noqa: E501
                soft_lab = int(soft_lab)  # it's a str from json config
                probs[classes.index(soft_lab), :, :] += (
                    mask * soft_prob * soft_labels_weight
                )  # noqa: E501

    if normalize:
        eps = 1e-6
        probs = probs / (probs.sum(axis=0, keepdims=True) + eps)

    return probs


def load_evo_dataset(dataset_path=None):
    evo_ds = EvoTrainV2Dataset(dataset_path=dataset_path, locs_tag="locs_v3")
    # locs = evo_ds.locs

    # remove_users = ["Darius (VITO) Admin", "Jean (External)", "Katya (IIASA)"]
    # locs = locs[~locs.user_alias.isin(remove_users)].copy()
    # locs["test"] = False

    # superusers = ["Maria (IIASA)", "Myroslava (IIASA)", "Daniele (VITO) Admin"]

    # locs.loc[
    #     (locs.status == "ACCEPTED") | (locs.user_alias.isin(superusers)),
    #     "test",
    # ] = True

    # evo_ds._locs = locs

    return evo_ds


def get_train_val_locs(locs_scenario="base", n_val_locs=None):
    evo_ds = load_evo_dataset()
    v3_locs = evo_ds.locs
    v3_locs = v3_locs[v3_locs.aux]  # discard locs without aux tifs. to check

    group0 = v3_locs[v3_locs.group == 0]
    train_locs0 = group0[
        (group0.lab_50 > 0.05)
        | (group0.lab_70 > 0.05)
        | (group0.lab_20 > 0.72)
    ].location_id.values

    group1 = v3_locs[v3_locs.group == 1]
    train_locs = group1.location_id.values
    train_locs = np.concatenate([train_locs0, train_locs])

    # group2 = v3_locs[v3_locs.group == 2].sample(n=n_val_locs, random_state=42)
    # val_locs = group2.location_id.values

    group2 = v3_locs[v3_locs.group == 2]
    lab_cols = [col for col in group2.columns if "lab" in col]

    # sample a bit more balanced val dataset
    val_locs = []
    for lab in lab_cols:
        if lab in ["lab_10", "lab_30"]:
            continue
        g = group2[group2[lab] > 0.30]
        val_locs += g.sample(
            min(1000, len(g)), random_state=42
        ).location_id.values.tolist()
    val_locs = list(set(val_locs))
    # -> 7330
    max_val_samples = len(val_locs)
    if n_val_locs is None:
        n_val_locs = max_val_samples

    elif n_val_locs > max_val_samples:
        from loguru import logger

        n_val_locs = max_val_samples
        logger.warning(
            f"n_val_locs is greater than the maximum number of samples available. "
            f"Setting n_val_locs to {max_val_samples}"
        )
    val_locs_group = group2[group2.location_id.isin(val_locs)]
    print(val_locs_group.shape)
    val_locs = val_locs_group.sample(
        n=n_val_locs, random_state=42
    ).location_id.values

    return train_locs, val_locs


def evo_target_to_probs(target):
    target_probs = np.zeros(
        (len(NET_LABELS), *target.shape[-2:]), dtype=np.float32
    )

    prim_probs = target_probs.copy()
    sec_probs = target_probs.copy()
    ter_probs = target_probs.copy()
    nans = np.isnan(target.data).sum(axis=0)

    primary = nans == 2
    primary_secondary = nans == 1
    primary_secondary_tertiary = nans == 0

    for i, label in enumerate(NET_LABELS):
        mask = (target.data[0] == label) & (primary)
        prim_probs[i][mask] = 1

        mask = (target.data[0] == label) & (primary_secondary)
        prim_probs[i][mask] = 0.7

        mask = (target.data[0] == label) & (primary_secondary_tertiary)
        prim_probs[i][mask] = 0.5

        mask = target.data[1] == label
        sec_probs[i][mask] = 0.3  # always 0.3

        mask = target.data[2] == label
        ter_probs[i] = mask * 0.2  # always 0.2
    target_probs = prim_probs + sec_probs + ter_probs
    return target_probs


class EvoNetV1Dataset(Dataset):
    def __init__(
        self,
        location_ids=None,
        dataset_path=None,
        bands=None,
        bands_head=["latlon", "meteo"],
        rgb_bands=None,
        flip_augmentation=True,
        rotate_augmentation=True,
        k_factor=5,
        k_factor_jitter=2,
        meteo_jitter=0.05,
        latlon_jitter=0.5,
        shuffle_locs=False,
        sort_locs_by_latitude=True,
    ):
        evo_dataset = load_evo_dataset(dataset_path)
        self.evo_dataset = evo_dataset
        self._reader = evo_dataset._reader(dataset_path)

        self.reference_year = 2020

        if location_ids is None:
            if shuffle_locs:
                self.ids = evo_dataset.locs.sample(
                    frac=1, random_state=42
                ).location_id.values
            if sort_locs_by_latitude:
                evo_dataset.locs["abs_lat"] = evo_dataset.locs.lat.abs()
                self.ids = evo_dataset.locs.sort_values(
                    "abs_lat"
                ).location_id.values
            else:
                self.ids = evo_dataset.locs.location_id.values
        else:
            self.ids = location_ids

        self.labels = NET_LABELS

        self.bands = bands if bands is not None else DEFAULT_BANDS
        self.aux_bands = DEFAULT_AUX_BANDS
        self.rgb_bands = rgb_bands

        self.transforms = EvoTransforms(
            flip_augmentation=flip_augmentation,
            rotate_augmentation=rotate_augmentation,
        )

        self._augmented_scaling_params = dict(
            k_factor=k_factor,
            k_factor_jitter=k_factor_jitter,
            lat_lon_jitter=latlon_jitter,
        )

        self._meteo_jitter = meteo_jitter
        self._latlon_jitter = latlon_jitter

        self._shuffle_locs = shuffle_locs
        self._sort_locs_by_latitude = sort_locs_by_latitude

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, idx):
        location_id = self.ids[idx]

        feats = self.read_feats(
            location_id,
            self.reference_year,
            self.bands,
            augmented_scaling=True,
            augmented_scaling_params=self._augmented_scaling_params,
        )

        feats = feats.fillna(0)  # fill nans for safety
        # latlon = feats.sel(band=["lat", "lon"])
        # feats = feats.sel(
        #     band=[b for b in self.bands if b not in ["lat", "lon"]]
        # )
        remapping_labels = {}  # removed mapping from v10
        try:
            target_probs = self.read_evov1_target(
                location_id, remapping_labels
            )
        except Exception:
            # logger.error(
            #     f"Error reading evo target for location {location_id}"
            # )
            target_probs = self.read_worldcover2021_target(
                location_id, remapping_labels
            )

        feats_head = self.evo_dataset.read_head_features(
            location_id,
            self.reference_year,
            meteo_jitter=self._meteo_jitter,
            latlon_jitter=self._latlon_jitter,
        )

        # transformed = self.transforms(feats.data, target_probs, latlon.data)
        transformed = self.transforms(feats.data, feats_head, target_probs)
        return transformed

    def read_feats(
        self,
        location_id,
        year,
        bands,
        augmented_scaling=False,
        augmented_scaling_params=None,
    ):
        feats = self.evo_dataset.read(location_id, year, bands)

        if augmented_scaling:
            augmented_scaling_params = (
                augmented_scaling_params or self._augmented_scaling_params
            )
            feats = apply_augmented_scaling(feats, **augmented_scaling_params)

        return feats

    def read_evov1_target(self, location_id, remapping_labels=None):
        year = 2020
        target = self.evo_dataset.read_annotation(
            location_id, year, annotation_name="evo-v1"
        )

        if remapping_labels is not None:
            for k, v in remapping_labels.items():
                target.data[target.data == k] = v

        target_probs = evo_target_to_probs(target)
        return target_probs

    def read_worldcover2021_target(self, location_id, remapping_labels=None):
        year = 2021
        target = self.evo_dataset.read_annotation(
            location_id, year, annotation_name="worldcover-v200"
        )

        if remapping_labels is not None:
            for k, v in remapping_labels.items():
                target.data[target.data == k] = v

        target_probs = label_to_probs(
            target.data[0],
            self.labels,
            soft_labels_mapping=None,
            soft_labels_weight=1,
        )

        return target_probs


def get_train_val_dataloaders(config):
    if isinstance(config, str) | isinstance(config, Path):
        with open(config) as f:
            config = json.load(f)

    config_dataloader = config["dataloader"]

    bands = config["model"]["bands"]

    shuffle_locs = config_dataloader["shuffle_locs"]
    sort_locs_by_latitude = config_dataloader["sort_locs_by_latitude"]
    shuffle_train = config_dataloader["shuffle_train"]
    k_factor = config_dataloader["k_factor"]
    k_factor_jitter = config_dataloader["k_factor_jitter"]
    meteo_jitter = config_dataloader["meteo_jitter"]
    latlon_jitter = config_dataloader["latlon_jitter"]

    batch_size = config_dataloader["batch_size"]
    workers = config_dataloader["workers"]

    flip_augmentation = config_dataloader["flip_augmentation"]
    rotate_augmentation = config_dataloader["rotate_augmentation"]

    train_locs, val_locs = get_train_val_locs(
        locs_scenario=config_dataloader["locs_scenario"],
        n_val_locs=config_dataloader["n_val_locs"],
    )

    if config["trainer"]["debug"]:
        train_locs = train_locs[:300]
        val_locs = val_locs[:50]

    train_dataset = EvoNetV1Dataset(
        location_ids=train_locs,
        bands=bands,
        flip_augmentation=flip_augmentation,
        rotate_augmentation=rotate_augmentation,
        k_factor=k_factor,
        k_factor_jitter=k_factor_jitter,
        meteo_jitter=meteo_jitter,
        latlon_jitter=latlon_jitter,
        shuffle_locs=shuffle_locs,
        sort_locs_by_latitude=sort_locs_by_latitude,
    )

    val_dataset = EvoNetV1Dataset(
        location_ids=val_locs,
        bands=bands,
        flip_augmentation=False,
        rotate_augmentation=False,
        k_factor=k_factor,
        k_factor_jitter=0,
        meteo_jitter=0,
        latlon_jitter=0,
        shuffle_locs=False,
        sort_locs_by_latitude=False,
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        num_workers=workers,
        shuffle=shuffle_train,
    )

    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, num_workers=workers, shuffle=False
    )

    return train_loader, val_loader, train_dataset, val_dataset
