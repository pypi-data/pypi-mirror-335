import json
from pathlib import Path
import random
import numpy as np
import xarray as xr
from torch.utils.data import DataLoader, Dataset

from evotrain.models.lsc10 import day_of_year_cyclic_feats
from evotrain.models.transforms import EvoTransforms
from evotrain.v2 import EvoTrainV2Dataset
from evotrain.v2.bands import BANDS_V2_AUX
from evotrain.v2tsm import EvoTrainV2TSMDataset
from evotrain.v2tsm.bands import BANDS_V2TSM_S2

# from evotrain.v2.bands import BANDS_V2_S2_FEATS
from evotrain.models.lsc10.v14 import (
    DEFAULT_AUX_BANDS,
    DEFAULT_BANDS,
    DEFAULT_S2_BANDS
    # LSC_CORE_LABELS,
    # LSC_ECO_LABELS,
    # LSC_ECO_LABELS_WOCO,
    # LSC_OCCLUSION_LABELS,
    # LSC_PERSISTENT_LABELS,
    # LSC_PERSISTENT_LABELS_WOCO,
    # NET_LABELS,
)


def load_evov2_dataset(dataset_path=None):
    evo_ds = EvoTrainV2Dataset(
        dataset_path=dataset_path, locs_tag="locs_v3"
    )  # , locs_tag="locs"

    return evo_ds


def load_evo_dataset(dataset_path=None):
    evo_ds = EvoTrainV2TSMDataset(
        dataset_path=dataset_path
    )  # , locs_tag="locs"
    
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
    train_sample_ids = list(
        v3_locs[v3_locs["selection_1"] == "train"]["sample_id"]
    )
    val_sample_ids = list(
        v3_locs[v3_locs["selection_1"] == "val"]["sample_id"]
    )

    return train_sample_ids, val_sample_ids



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
    signal_bands = [b for b in darr.band.values if b in BANDS_V2TSM_S2]

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


# def evo_target_to_probs(target_lsc, target_raw):
#     target_lsc = target_lsc.squeeze()

#     ## Ecosystem probs
#     target_eco_probs = np.zeros(
#         (len(LSC_ECO_LABELS), *target_raw.shape[-2:]), dtype=np.float32
#     )

#     prim_probs = target_eco_probs.copy()
#     sec_probs = target_eco_probs.copy()
#     ter_probs = target_eco_probs.copy()
#     nans = np.isnan(target_raw.data).sum(axis=0)

#     primary = nans == 2
#     primary_secondary = nans == 1
#     primary_secondary_tertiary = nans == 0

#     for i, label in enumerate(LSC_ECO_LABELS_WOCO):
#         mask = (target_raw.data[0] == label) & (primary)
#         prim_probs[i][mask] = 1

#         mask = (target_raw.data[0] == label) & (primary_secondary)
#         prim_probs[i][mask] = 0.7

#         mask = (target_raw.data[0] == label) & (primary_secondary_tertiary)
#         prim_probs[i][mask] = 0.5

#         mask = target_raw.data[1] == label
#         sec_probs[i][mask] = 0.3  # always 0.3

#         mask = target_raw.data[2] == label
#         ter_probs[i] = mask * 0.2  # always 0.2
#     target_eco_probs = prim_probs + sec_probs + ter_probs

#     # check occlusion
#     for i, label in enumerate(LSC_OCCLUSION_LABELS):
#         target_eco_probs[:, target_lsc == label] = 0

#     ### lsc core probs
#     target_core_probs = np.zeros(
#         (len(LSC_CORE_LABELS), *target_raw.shape[-2:]), dtype=np.float32
#     )
#     prim_probs = target_core_probs.copy()
#     sec_probs = target_core_probs.copy()
#     ter_probs = target_core_probs.copy()
#     nans = np.isnan(target_raw.data).sum(axis=0)

#     primary = nans == 2
#     primary_secondary = nans == 1
#     primary_secondary_tertiary = nans == 0

#     LSC_COVER_LABELS = [
#         lab for lab in LSC_CORE_LABELS if lab not in LSC_OCCLUSION_LABELS
#     ]
#     for i, label in enumerate(LSC_COVER_LABELS):
#         ind = LSC_CORE_LABELS.index(label)
#         mask = target_lsc.data.squeeze() == label
#         prim_probs[ind][mask] = 1
#         for label_sec, label_sec_woco in zip(
#             LSC_PERSISTENT_LABELS, LSC_PERSISTENT_LABELS_WOCO
#         ):
#             ind_sec = LSC_CORE_LABELS.index(label_sec)

#             mask = (target_raw.data[1] == label_sec_woco) & (
#                 target_lsc.data.squeeze() == label
#             )
#             sec_probs[ind_sec][mask] = 0.3  # always 0.3
#             mask = mask & (primary_secondary)
#             prim_probs[ind][mask] = 0.7
#             mask = mask & (primary_secondary_tertiary)
#             prim_probs[ind][mask] = 0.5

#             mask = (target_raw.data[2] == label_sec_woco) & (
#                 target_lsc.data.squeeze() == label
#             )
#             ter_probs[ind_sec] = mask * 0.2  # always 0.2
#             prim_probs[ind][mask] = 0.5

#     target_core_probs = prim_probs + sec_probs + ter_probs

#     # check occlusion
#     for i, label in enumerate(LSC_OCCLUSION_LABELS):
#         ind = LSC_CORE_LABELS.index(label)
#         mask = target_lsc.data.squeeze() == label
#         target_core_probs[:, mask] = 0
#         target_core_probs[ind][mask] = 1

#     return target_core_probs, target_eco_probs


class EvoNetV1Dataset(Dataset):
    def __init__(
        self,
        sample_ids=None,
        dataset_path=None,
        datasetv2_path=None,
        bands=None,
        bands_head=["latlon", "meteo", "doy"],
        rgb_bands=None,
        flip_augmentation=True,
        rotate_augmentation=True,
        augmented_scaling=True,
        k_factor=5,
        k_factor_jitter=2,
        meteo_jitter=0.05,
        latlon_jitter=0.5,
        season_jitter=15,
        doy_jitter=15,
        shuffle_locs=False,
        sort_locs_by_latitude=True,
    ):
        evo_dataset = load_evo_dataset(dataset_path)
    
        self.evo_dataset = evo_dataset
        evov2_dataset = load_evov2_dataset(datasetv2_path)
        self.evov2_dataset = evov2_dataset
        self._reader = evo_dataset._reader(dataset_path)

        self.reference_year = 2020

        if sample_ids is None:
            if shuffle_locs:
                self.ids = evo_dataset.locs.sample(
                    frac=1, random_state=42
                ).sample_id.values
            if sort_locs_by_latitude:
                evo_dataset.locs["abs_lat"] = evo_dataset.locs.lat.abs()
                self.ids = evo_dataset.locs.sort_values(
                    "abs_lat"
                ).sample_id.values
            else:
                self.ids = evo_dataset.locs.sample_id.values
        else:
            self.ids = sample_ids

        # self.labels = NET_LABELS

        self.bands = bands if bands is not None else DEFAULT_BANDS
        self.aux_bands = DEFAULT_AUX_BANDS
        self.rgb_bands = rgb_bands

        self.transforms = EvoTransforms(
            flip_augmentation=flip_augmentation,
            rotate_augmentation=rotate_augmentation,
        )

        self._augmented_scaling = augmented_scaling
        self._augmented_scaling_params = dict(
            k_factor=k_factor,
            k_factor_jitter=k_factor_jitter,
            lat_lon_jitter=latlon_jitter,
        )

        self._meteo_jitter = meteo_jitter
        self._latlon_jitter = latlon_jitter
        self._season_jitter = season_jitter
        self._doy_jitter = doy_jitter
        self._shuffle_locs = shuffle_locs
        self._sort_locs_by_latitude = sort_locs_by_latitude

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, idx):
        sample_id = self.ids[idx]

        feats = self.read_feats(
            sample_id,
            self.bands,
            augmented_scaling=self._augmented_scaling,
            augmented_scaling_params=self._augmented_scaling_params,
        )

        feats = feats.fillna(0)  # fill nans for safety
        remapping_labels = {}  # removed mapping from v10
        prob_cover, prob_occlusion, prob_eco, weight_cover, weight_occlusion, weight_eco = self.read_evov1_target(sample_id) 

        # target_probs_core, target_probs_eco = self.read_evov1_target(
        #     sample_id, remapping_labels
        # )

        # target_probs = np.vstack([target_probs_core, target_probs_eco])

        location_id = "_".join(sample_id.split("_")[:-1])
        feats_head = self.evov2_dataset.read_head_features(
            location_id,
            self.reference_year,
            meteo_jitter=self._meteo_jitter,
            latlon_jitter=self._latlon_jitter,
        )

        # season = get_season(sample_id, self._season_jitter)
        doy = day_of_year_cyclic_feats(sample_id, self._doy_jitter)
        feats_head = np.concatenate((feats_head, doy), axis=0).astype(
            np.float32
        )

        transformed = self.transforms(feats.data, feats_head, prob_cover.data, prob_occlusion.data, prob_eco.data, weight_cover.data, weight_occlusion.data, weight_eco.data)
        
        feats = transformed[0]
        feats_head = transformed[1]
        probs = transformed[2:5]
        weights = transformed[5:]        
                
        transformed = [feats, feats_head, probs, weights]
        
        return transformed

    def read_feats(
        self,
        sample_id,
        bands,
        augmented_scaling=False,
        augmented_scaling_params=None,
    ):
        s2_feats = aux_feats = None

        s2_bands = [b for b in bands if b in BANDS_V2TSM_S2]
        aux_bands = [b for b in bands if b in BANDS_V2_AUX]

        if len(s2_bands) > 0:
            s2_feats = self.read_s2feats(
                sample_id,
                s2_bands,
                augmented_scaling,
                augmented_scaling_params,
            )

        if len(aux_bands) > 0:
            # if len(aux_bands) == 1:
            #     aux_bands = [aux_bands[0], "s2-B02-p10"]
            aux_feats = self.read_auxfeats(
                sample_id,
                aux_bands,
                augmented_scaling,
                augmented_scaling_params,
            )
            # aux_feats = aux_feats.sel(band = aux_bands[0])

        darr = xr.concat(
            [arr for arr in (s2_feats, aux_feats) if arr is not None],
            dim="band",
            compat="equals",
        )

        # darr = darr.astype(np.float32)
        return darr

    # read sentinel features
    def read_s2feats(
        self,
        sample_id,
        bands,
        augmented_scaling=False,
        augmented_scaling_params=None,
    ):
        feats = self.evo_dataset.read(sample_id, bands, add_target=False)

        if augmented_scaling:
            augmented_scaling_params = (
                augmented_scaling_params or self._augmented_scaling_params
            )
            feats = apply_augmented_scaling(feats, **augmented_scaling_params)

        return feats

    # read auxiliary features
    def read_auxfeats(
        self,
        sample_id,
        bands,
        augmented_scaling=False,
        augmented_scaling_params=None,
    ):
        location_id = "_".join(sample_id.split("_")[:-1])
        year = int(sample_id.split("_")[-1][:4])
        feats = self.evov2_dataset.read(location_id, year, bands)

        if augmented_scaling:
            augmented_scaling_params = (
                augmented_scaling_params or self._augmented_scaling_params
            )
            feats = apply_augmented_scaling(feats, **augmented_scaling_params)

        return feats

    def read_evov1_target(self, sample_id):
        year = 2020
        prob_cover = self.evo_dataset.read_annotation(
            sample_id, annotation_name="lsc-evo-v1-prob-cover-v1"
        )
        prob_occlusion = self.evo_dataset.read_annotation(
            sample_id, annotation_name="lsc-evo-v1-prob-occlusion-v1"
        )
        prob_eco = self.evo_dataset.read_annotation(
            sample_id, annotation_name="lsc-evo-v1-prob-eco-v1"
        )
        
        weight_cover = self.evo_dataset.read_annotation(
            sample_id, annotation_name="lsc-evo-v1-weight-cover-v1"
        )
        weight_cover = xr.concat([weight_cover for it in np.arange(len(prob_cover.band))], dim='band')
        
        weight_occlusion = self.evo_dataset.read_annotation(
            sample_id, annotation_name="lsc-evo-v1-weight-occlusion-v1"
        )
        weight_occlusion = xr.concat([weight_occlusion for it in np.arange(len(prob_occlusion.band))], dim='band')
        
        weight_eco = self.evo_dataset.read_annotation(
            sample_id, annotation_name="lsc-evo-v1-weight-eco-v1"
        )
        weight_eco = xr.concat([weight_eco for it in np.arange(len(prob_eco.band))], dim='band')

        # location_id = "_".join(sample_id.split("_")[:-1])
        # target_raw = self.evov2_dataset.read_annotation(
        #     location_id, year, annotation_name="evo-v1"
        # )

        # if remapping_labels is not None:
        #     for k, v in remapping_labels.items():
        #         target.data[target.data == k] = v

        # target_probs = evo_target_to_probs(target, target_raw)
        return prob_cover, prob_occlusion, prob_eco, weight_cover, weight_occlusion, weight_eco


#     def read_worldcover2021_target(self, location_id, remapping_labels=None):
#         year = 2021
#         target = self.evo_dataset.read_annotation(
#             location_id, year, annotation_name="worldcover-v200"
#         )

#         if remapping_labels is not None:
#             for k, v in remapping_labels.items():
#                 target.data[target.data == k] = v

#         target_probs = label_to_probs(
#             target.data[0],
#             self.labels,
#             soft_labels_mapping=None,
#             soft_labels_weight=1,
#         )

#         return target_probs


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
    season_jitter = config_dataloader["season_jitter"]
    doy_jitter = config_dataloader["doy_jitter"]

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
        sample_ids=train_locs,
        bands=bands,
        flip_augmentation=flip_augmentation,
        rotate_augmentation=rotate_augmentation,
        k_factor=k_factor,
        k_factor_jitter=k_factor_jitter,
        meteo_jitter=meteo_jitter,
        season_jitter=season_jitter,
        doy_jitter=doy_jitter,
        latlon_jitter=latlon_jitter,
        shuffle_locs=shuffle_locs,
        sort_locs_by_latitude=sort_locs_by_latitude,
    )

    val_dataset = EvoNetV1Dataset(
        sample_ids=val_locs,
        bands=bands,
        flip_augmentation=False,
        rotate_augmentation=False,
        k_factor=k_factor,
        k_factor_jitter=0,
        meteo_jitter=0,
        season_jitter=0,
        doy_jitter=0,
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
