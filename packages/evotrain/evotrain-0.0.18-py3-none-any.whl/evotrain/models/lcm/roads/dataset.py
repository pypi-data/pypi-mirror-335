import json
from pathlib import Path

import numpy as np
from torch.utils.data import DataLoader, Dataset

from loguru import logger

from evotrain.models.lcm.roads import (
    NET_LABELS,
    NET_LABELS_MAPPING,
)
from evotrain.models.transforms import EvoTransforms, EvoTransforms_v2
from evotrain.models.lcm.roads.scaling import apply_augmented_scaling
from evotrain.v2 import EvoTrainV2Dataset


class EvoNetV1Dataset(Dataset):
    def __init__(
        self,
        location_ids=None,
        dataset_path=None,
        bands=None,
        bands_head=["latlon", "meteo"],
        bands_aux=["cop-DEM-alt"],
        rgb_bands=None,
        flip_augmentation=True,
        rotate_augmentation=True,
        noise_augmentation=True,
        spectral_augmentation=True,
        translation_augmentation=True,
        masking_augmentation=True,
        k_factor=5,
        k_factor_jitter=2,
        meteo_jitter=0.05,
        latlon_jitter=0.5,
        shuffle_locs=False,
        sort_locs_by_latitude=True,
        debug=False,
    ):
        self.debug = debug
        logger.debug(
            f"Initializing **EvoNetV1Dataset** with dataset_path: {dataset_path}"
        )
        evo_dataset = load_evo_dataset(dataset_path)
        self.evo_dataset = evo_dataset
        self._reader = evo_dataset._reader(dataset_path)
        logger.debug(f"Loaded evo_dataset: {evo_dataset}")

        self.reference_year = 2020
        logger.debug(f"Set reference_year to {self.reference_year}")

        if location_ids is None:
            if shuffle_locs:
                self.ids = evo_dataset.locs.sample(
                    frac=1, random_state=42
                ).location_id.values
                logger.debug("Shuffled location IDs")
            if sort_locs_by_latitude:
                evo_dataset.locs["abs_lat"] = evo_dataset.locs.lat.abs()
                self.ids = evo_dataset.locs.sort_values("abs_lat").location_id.values
                logger.debug("Sorted location IDs by latitude")
            else:
                self.ids = evo_dataset.locs.location_id.values
                logger.debug("Using location IDs without sorting or shuffling")
        else:
            self.ids = location_ids
            logger.debug(f"Using len(location_ids)={len(location_ids)} location IDs")

        self.labels = NET_LABELS
        self.labels_mapping = NET_LABELS_MAPPING
        logger.debug(f"Set labels to NET_LABELS: {NET_LABELS}")

        self.bands = bands
        self.bands_head = bands_head
        self.bands_aux = bands_aux
        self.rgb_bands = rgb_bands
        logger.debug(
            f"Set bands to: {self.bands}, bands_aux to: {self.bands_aux}, rgb_bands to: {self.rgb_bands}"
        )

        self.transforms = EvoTransforms_v2(
            flip_augmentation=flip_augmentation,
            rotate_augmentation=rotate_augmentation,
            noise_augmentation=noise_augmentation,
            spectral_augmentation=spectral_augmentation,
            translation_augmentation=translation_augmentation,
            masking_augmentation=masking_augmentation,
        )
        logger.debug(
            f"Transforms: flip_augmentation={flip_augmentation}, rotate_augmentation={rotate_augmentation}"
        )

        self._augmented_scaling_params = dict(
            k_factor=k_factor,
            k_factor_jitter=k_factor_jitter,
            lat_lon_jitter=latlon_jitter,
        )
        logger.debug(f"Set augmented scaling params: {self._augmented_scaling_params}")

        self._meteo_jitter = meteo_jitter
        self._latlon_jitter = latlon_jitter
        logger.debug(
            f"Set meteo_jitter to {self._meteo_jitter}, latlon_jitter to {self._latlon_jitter}"
        )

        self._shuffle_locs = shuffle_locs
        self._sort_locs_by_latitude = sort_locs_by_latitude
        logger.debug(
            f"Set shuffle_locs to {self._shuffle_locs}, sort_locs_by_latitude to {self._sort_locs_by_latitude}"
        )

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
        assert len(feats), f"No features found for {location_id}"

        feats = feats.fillna(0)  # fill nans for safety

        target_probs = self.read_osmroads_target(location_id)

        feats_head = self.evo_dataset.read_head_features(
            location_id,
            self.reference_year,
            meteo_jitter=self._meteo_jitter,
            latlon_jitter=self._latlon_jitter,
        )

        if self.debug:
            return feats, feats_head, target_probs
        else:
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

    def read_osmroads_target(self, location_id):
        target = self.evo_dataset.read_osmroads(location_id)

        targets_expanded = np.zeros(
            (len(NET_LABELS), target.shape[1], target.shape[2]), dtype=np.float32
        )
        # Assign values to the channel where NET_LABELS is built
        NET_LABELS_MAPPING_inv = {v: k for k, v in NET_LABELS_MAPPING.items()}
        channel_to_assign = NET_LABELS.index(NET_LABELS_MAPPING_inv["built"])
        targets_expanded[channel_to_assign] = target.squeeze().values

        return targets_expanded


def evo_target_to_probs(target):
    target_probs = np.zeros((len(NET_LABELS), *target.shape[-2:]), dtype=np.float32)

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


def label_to_probs(
    label,
    classes,
    soft_labels_mapping=None,
    soft_labels_weight=1,
    normalize=True,
):
    """Transform a 2-D label array in a 3D target probs array"""

    probs = np.zeros((len(classes), label.shape[0], label.shape[1]), dtype=np.float32)

    classes_idx = {ind: lab for ind, lab in enumerate(classes)}

    for ind, lab in classes_idx.items():
        mask = label == lab
        probs[ind, :, :] += mask

        if soft_labels_mapping is not None:
            for soft_lab, soft_prob in soft_labels_mapping.get(lab, {}).items():  # noqa: E501
                soft_lab = int(soft_lab)  # it's a str from json config
                probs[classes.index(soft_lab), :, :] += (
                    mask * soft_prob * soft_labels_weight
                )  # noqa: E501

    if normalize:
        eps = 1e-6
        probs = probs / (probs.sum(axis=0, keepdims=True) + eps)

    return probs


def load_evo_dataset(dataset_path=None, return_meteo=False):
    evo_ds = EvoTrainV2Dataset(
        dataset_path=dataset_path,
        locs_tag="locs_v3",
        filter_aux=True,
        filter_meteo=True,
        filter_osm=True,
    )

    return evo_ds


def get_train_val_locs(locs_scenario="base", n_val_locs=None):
    evo_ds = load_evo_dataset()

    v3_locs = evo_ds.locs
    v3_locs = v3_locs[v3_locs.aux]  # discard locs without aux tifs.
    v3_locs = v3_locs[v3_locs.osm_roads]  # discard locs without osm tifs.

    # We need to get n_val_locs as specified in the argument and the
    # rest is train_locs
    train_locs = v3_locs.location_id.values
    val_locs = []

    if n_val_locs is not None:
        val_locs = np.random.choice(train_locs, n_val_locs, replace=False)
        train_locs = np.setdiff1d(train_locs, val_locs)
    logger.debug(
        f"We have {len(train_locs)} train locations and {len(val_locs)} val locations"
    )
    return train_locs, val_locs

    # group0 = v3_locs[v3_locs.group == 0]
    # train_locs0 = group0[
    #     (group0.lab_50 > 0.05) | (group0.lab_70 > 0.05) | (group0.lab_20 > 0.72)
    # ].location_id.values

    # group1 = v3_locs[v3_locs.group == 1]
    # train_locs = group1.location_id.values
    # train_locs = np.concatenate([train_locs0, train_locs])

    # # group2 = v3_locs[v3_locs.group == 2].sample(n=n_val_locs, random_state=42)
    # # val_locs = group2.location_id.values

    # group2 = v3_locs[v3_locs.group == 2]
    # lab_cols = [col for col in group2.columns if "lab" in col]

    # # sample a bit more balanced val dataset
    # val_locs = []
    # for lab in lab_cols:
    #     if lab in ["lab_10", "lab_30"]:
    #         continue
    #     g = group2[group2[lab] > 0.30]
    #     val_locs += g.sample(
    #         min(1000, len(g)), random_state=42
    #     ).location_id.values.tolist()
    # val_locs = list(set(val_locs))
    # # -> 7330
    # max_val_samples = len(val_locs)
    # if n_val_locs is None:
    #     n_val_locs = max_val_samples

    # elif n_val_locs > max_val_samples:
    #     n_val_locs = max_val_samples
    #     logger.warning(
    #         f"n_val_locs is greater than the maximum number of samples available. "
    #         f"Setting n_val_locs to {max_val_samples}"
    #     )
    # val_locs_group = group2[group2.location_id.isin(val_locs)]
    # logger.debug(f"val_locs_group.shape: {val_locs_group.shape}")
    # val_locs = val_locs_group.sample(n=n_val_locs, random_state=42).location_id.values

    # return train_locs, val_locs


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

    return (
        train_loader,
        val_loader,
        train_dataset,
        val_dataset,
    )
