import random

import numpy as np
import torch
import xarray as xr
from loguru import logger
from torch.utils.data import DataLoader, Dataset
from torchvision.transforms import v2 as transforms

from evotrain.labels import WORLDCOVER_LABELS
from evotrain.v2 import EvoTrainV2Dataset
from evotrain.v2.bands import BANDS_V2_AUX, BANDS_V2_S2_FEATS

DEFAULT_BANDS = BANDS_V2_S2_FEATS + BANDS_V2_AUX


class NumpyToTensor:
    def __call__(self, arr):
        return torch.tensor(arr)


BASE_TRANSFORMS = [NumpyToTensor()]
FLIP_TRANSFORMS = [
    transforms.RandomHorizontalFlip(0.5),
    transforms.RandomVerticalFlip(0.5),
]
DEFAUT_CROSS_LABELS_MAPPING = {
    10: {20: 0.5, 30: 0.25},
    20: {10: 0.5, 30: 0.5},
    30: {10: 0.25, 20: 0.5},
    40: {30: 0.25, 90: 0.1},
    50: {60: 0.5},
    70: {30: 0.5},
    90: {30: 0.25},
    95: {10: 0.25},
}


def label_to_probs(label, classes, cross_labels_mapping=None):
    """Transform a 2-D label array in a 3D target probs array"""

    probs = np.zeros((len(classes), label.shape[0], label.shape[1]), dtype=np.float32)

    classes_idx = {ind: lab for ind, lab in enumerate(classes)}

    for ind, lab in classes_idx.items():
        probs[ind, :, :] = label == lab
        if cross_labels_mapping is not None:
            for cross_lab, cross_prob in cross_labels_mapping.get(lab, {}).items():  # noqa: E501
                cross_lab = int(cross_lab)  # it's a str from json config
                probs[classes_idx[cross_lab], :, :] = cross_prob
    return probs


def logistic(x, L=1, k=3.60, x0=0, y0=-0.5, s=2):
    return (L / (1 + np.exp(-k * (x - x0))) + y0) * s


def random_jitter(n):
    return random.uniform(-n, n)


def apply_augmented_scaling(
    darr,
    k_factor=5,
    k_factor_jitter=2,
    lat_lon_jitter=1,
    dem_scaling=4000,
    lat_scaling=90,
    lon_scaling=180,
):
    k_noised_signal = k_factor + random_jitter(k_factor_jitter)
    k_noised_dem = k_factor + random_jitter(k_factor_jitter)
    lat_jitter = random_jitter(lat_lon_jitter)
    lon_jitter = random_jitter(lat_lon_jitter)

    # distinguish on bands that require special scaling
    signal_bands = [b for b in darr.band.values if b in BANDS_V2_S2_FEATS]

    # we rescale the dem band by 4000 as upper limit for high altitudes
    # we then apply the logistic scaling to it as well
    dem_band = ["cop-DEM-alt"] if "cop-DEM-alt" in darr.band.values else None  # noqa: E501
    lat_band = ["lat"] if "lat" in darr.band.values else None
    lon_band = ["lon"] if "lon" in darr.band.values else None

    # we rescale lat lon bands between their ranges, no logistic scaling
    darr_signal = darr.sel(band=signal_bands)
    if k_factor > 0:
        darr_signal = logistic(darr_signal, k=k_noised_signal)

    darr_dem = darr.sel(band=dem_band) / dem_scaling if dem_band is not None else None
    if (k_factor > 0) and (dem_band is not None):
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

    darrs = [d for d in (darr_signal, darr_dem, darr_lat, darr_lon) if d is not None]

    if len(darrs) > 1:
        darr = xr.concat([darr_signal, darr_dem, darr_lat, darr_lon], dim="band")
    else:
        darr = darrs[0]

    return darr


def apply_k_scaling_bands_ndvi(darr, bands_k_factor=5, ndvi_k_factor=0):
    # distinguish on bands that require special scaling
    signal_bands = [b for b in darr.band.values if b in BANDS_V2_S2_FEATS]

    b_bands = [b for b in signal_bands if "ndvi" not in b]
    ndvi_bands = [b for b in signal_bands if "ndvi" in b]
    other_bands = [b for b in darr.band.values if b not in signal_bands]

    # we rescale lat lon bands between their ranges, no logistic scaling
    darr_bands = darr.sel(band=b_bands)
    if bands_k_factor:
        darr_bands = logistic(darr_bands, k=bands_k_factor)

    darr_ndvi = darr.sel(band=ndvi_bands)
    if ndvi_k_factor:
        darr_ndvi = logistic(darr_ndvi, k=ndvi_k_factor)

    darrs = [darr_bands, darr_ndvi]
    if len(other_bands) > 0:
        darrs.append(darr.sel(band=other_bands))

    darr = xr.concat(darrs, dim="band").sel(band=darr.band.values)

    return darr


def apply_standard_scaling(darr, mean, std):
    darr = darr - np.broadcast_to(mean, darr.shape)
    darr = darr / np.broadcast_to(std, darr.shape)
    return darr


class SinglePatchDataset(Dataset):
    def __init__(
        self,
        dataset_path=None,
        patch_ids=None,
        bands=None,
        flip_augmentation=True,
        k_factor=5,
        k_factor_jitter=2,
        lat_lon_jitter=1,
        dem_scaling=4000,
        lat_scaling=90,
        lon_scaling=180,
        cross_labels_mapping=None,
    ):
        self.dataset_path = dataset_path
        evo_dataset = EvoTrainV2Dataset(dataset_path)
        self.evo_dataset = evo_dataset
        self._reader = evo_dataset._reader(dataset_path)

        self.ids = patch_ids if patch_ids is not None else evo_dataset.patch_ids()

        # remove target band, it will be loaded separately
        self.target_band = "worldcover_2021"
        self.labels = WORLDCOVER_LABELS

        self.bands = bands if bands is not None else DEFAULT_BANDS
        self.bands = [b for b in self.bands if b != self.target_band]

        torch_transforms = BASE_TRANSFORMS.copy()

        if flip_augmentation:
            torch_transforms += FLIP_TRANSFORMS

        torch_transforms += [transforms.ToDtype(torch.float32)]

        self._augmented_scaling_params = dict(
            k_factor=k_factor,
            k_factor_jitter=k_factor_jitter,
            lat_lon_jitter=lat_lon_jitter,
            dem_scaling=dem_scaling,
            lat_scaling=lat_scaling,
            lon_scaling=lon_scaling,
        )

        self.transforms = transforms.Compose(torch_transforms)
        self._cross_labels_mapping = cross_labels_mapping

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, idx):
        location_id, year = self.ids[idx]
        try:
            feats, target = self.read(
                location_id, year, load_target=True, augmented_scaling=False
            )

            feats = self.apply_augmented_scaling(feats)

            feats = feats.data  # still a dataarray here
            feats, target = self.apply_transforms(feats, target)
        except Exception as e:
            logger.error(
                f"Failed to load {location_id} - {year} sample. "
                f"Loading dummy sample. Error: {e}"
            )
            feats = torch.from_numpy(
                np.zeros((len(self.bands), 128, 128), dtype=np.float32)
            )
            target = torch.from_numpy(np.zeros((11, 128, 128), dtype=np.float32))
        return feats, target

    def apply_augmented_scaling(self, darr):
        return apply_augmented_scaling(darr, **self._augmented_scaling_params)

    def apply_transforms(self, feats, target):
        feats_n_bands = feats.shape[0]
        feats_target = np.concatenate([feats, target], axis=0)
        feats_target = self.transforms(feats_target)
        feats, target = (feats_target[:feats_n_bands], feats_target[feats_n_bands:])
        return feats, target

    def read(
        self,
        location_id,
        year,
        load_target=True,
        target_to_probs=True,
        augmented_scaling=False,
        augmented_scaling_params=None,
    ):
        bands = [b for b in self.bands]  # copy
        # logger.debug(f"bands: {bands}")
        if load_target:
            bands.append(self.target_band)
        darr = self.evo_dataset.read(location_id, year, bands)
        feats = darr.sel(band=self.bands)
        # logger.debug(f"feats bands: {feats.band.values}")
        if augmented_scaling:
            augmented_scaling_params = (
                augmented_scaling_params or self._augmented_scaling_params
            )
            print(augmented_scaling_params)
            feats = apply_augmented_scaling(feats, **augmented_scaling_params)
            # logger.debug(f"feats augmented bands: {feats.band.values}")
        if load_target:
            label = darr.sel(band=self.target_band).round().astype(int)

            if target_to_probs:
                target = label_to_probs(label, self.labels, self._cross_labels_mapping)
            else:
                target = label
            return feats, target
        else:
            return feats


class SinglePatchFeaturesDataset(SinglePatchDataset):
    def __getitem__(self, idx):
        location_id, year = self.ids[idx]

        try:
            feats = self.read(
                location_id, year, load_target=False, standard_scaling=self._standardize
            )
            feats = feats.data  # still a dataarray here
            feats = self.transforms(feats)
        except Exception as e:
            logger.error(
                f"Failed to load {location_id} - {year} sample. "
                f"Loading dummy sample. Error: {e}"
            )
            feats = torch.from_numpy(
                np.zeros((len(self.bands), 128, 128), dtype=np.float32)
            )
        return feats


class ChangeNetDataset(SinglePatchDataset):
    def __init__(self, dataset_df, **kwargs):
        self.dataset_df = dataset_df
        super().__init__(**kwargs)

    def __len__(self):
        return len(self.dataset_df)

    def __getitem__(self, idx):
        row = self.dataset_df.iloc[idx]
        loc_id_anchor = row.location_id_anchor
        loc_id_distant = row.location_id_distant

        anchor, anchor_lab = self.read(
            loc_id_anchor,
            year=2021,
            load_target=True,
            target_to_probs=False,
            augmented_scaling=False,
        )
        distant, distant_lab = self.read(
            loc_id_distant,
            year=2021,
            load_target=True,
            target_to_probs=False,
            augmented_scaling=False,
        )

        anchor = self.apply_augmented_scaling(anchor)
        distant = self.apply_augmented_scaling(distant)

        diff_map = self._get_diff_map(anchor_lab, distant_lab)

        (anchor, distant, diff_map, anchor_lab, distant_lab) = self.apply_transforms(
            anchor, distant, diff_map, anchor_lab, distant_lab
        )

        return anchor, distant, diff_map, anchor_lab, distant_lab

    def _get_diff_map(self, anchor_lab, distant_lab):
        return ((abs(anchor_lab - distant_lab) > 0) * 1, anchor_lab, distant_lab)

    def apply_transforms(self, anchor, distant, diff_map, anchor_lab, distant_lab):
        feats_ind1 = anchor.shape[0]
        feats_ind2 = feats_ind1 * 2
        lab_ind1 = feats_ind2 + anchor_lab.shape[0]
        lab_ind2 = lab_ind1 + anchor_lab.shape[0]

        feats_transformed = np.concatenate(
            [anchor, distant, anchor_lab, distant_lab, diff_map], axis=0
        )
        feats_transformed = self.transforms(feats_transformed)
        (anchor, distant, anchor_lab, distant_lab, diff_map) = (
            feats_transformed[:feats_ind1],
            feats_transformed[feats_ind1:feats_ind2],
            feats_transformed[feats_ind2:lab_ind1],
            feats_transformed[lab_ind1:lab_ind2],
            torch.from_numpy(np.expand_dims(feats_transformed[-1], 0)),
        )
        return (anchor, distant, diff_map, anchor_lab, distant_lab)


def get_single_patch_dataloaders(
    bands,
    dataset_frac=1,
    train_frac=0.7,
    features_only=False,
    flip_augmentation=True,
    dataset_path=None,
    random_state=0,
    train_years=(2021,),
    val_years=(2018, 2019, 2020, 2021, 2022),
    train_batch_size=50,
    train_shuffle=True,
    val_batch_size=50,
    val_shuffle=True,
    dataloader_workers=12,
    locs_tag="locs_h3",
    locs_groups=[1],
    k_factor=5,
    k_factor_jitter=2,
    lat_lon_jitter=1,
    dem_scaling=4000,
    lat_scaling=90,
    lon_scaling=180,
    cross_labels_mapping=None,
):
    evo_dataset = EvoTrainV2Dataset(
        dataset_path, locs_tag=locs_tag, locs_groups=locs_groups
    )
    loc_ids = evo_dataset.location_ids.sample(frac=dataset_frac, random_state=0)
    train_locs = loc_ids.sample(frac=train_frac, random_state=random_state).values
    val_locs = loc_ids[~loc_ids.isin(train_locs)]

    train_patch_ids = [(loc_id, year) for loc_id in train_locs for year in train_years]

    val_patch_ids = [(loc_id, year) for loc_id in val_locs for year in val_years]

    # Initializes dataset depending on the features_only parameter
    init_class = SinglePatchFeaturesDataset if features_only else SinglePatchDataset

    train_dataset = init_class(
        dataset_path,
        patch_ids=train_patch_ids,
        bands=bands,
        flip_augmentation=flip_augmentation,
        k_factor=k_factor,
        k_factor_jitter=k_factor_jitter,
        lat_lon_jitter=lat_lon_jitter,
        dem_scaling=dem_scaling,
        lat_scaling=lat_scaling,
        lon_scaling=lon_scaling,
        cross_labels_mapping=cross_labels_mapping,
    )

    val_dataset = init_class(
        dataset_path,
        patch_ids=val_patch_ids,
        bands=bands,
        flip_augmentation=False,
        k_factor=k_factor,
        k_factor_jitter=0,
        lat_lon_jitter=0,
        dem_scaling=dem_scaling,
        lat_scaling=lat_scaling,
        lon_scaling=lon_scaling,
        cross_labels_mapping=cross_labels_mapping,
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=train_batch_size,
        shuffle=train_shuffle,
        num_workers=dataloader_workers,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=val_batch_size,
        shuffle=val_shuffle,
        num_workers=dataloader_workers,
    )

    return train_loader, val_loader, train_dataset, val_dataset
