import json
from pathlib import Path
import random
import numpy as np
import xarray as xr
from torch.utils.data import DataLoader, Dataset

from evotrain.models.lsc10 import day_of_year_cyclic_feats
from evotrain.models.transforms import EvoTransforms_v2
from evotrain.v2 import EvoTrainV2Dataset
from evotrain.v2.bands import BANDS_V2_AUX
from evotrain.v2tsm import EvoTrainV2TSMDataset
from evotrain.v2tsm.bands import BANDS_V2TSM_S2
from evotrain.v2tsm.bands import BANDS_V2TSM_S1_GAMMA0
from satio_pc.geotiff import compute_pixel_coordinates
import random

# from evotrain.v2.bands import BANDS_V2_S2_FEATS
from evotrain.models.lsc10.v16 import (
    DEFAULT_AUX_BANDS,
    DEFAULT_BANDS,
    DEFAULT_S2_BANDS
)


def load_evov2_dataset(dataset_path=None):
    evo_ds = EvoTrainV2Dataset(
        dataset_path=dataset_path, locs_tag="locs_v3"
    )  # , locs_tag="locs"

    return evo_ds


def load_evo_dataset(dataset_path=None, dataset_s1_path=None):
    evo_ds = EvoTrainV2TSMDataset(
        dataset_path=dataset_path,
        dataset_s1_path=dataset_s1_path
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


def get_train_val_locs(locs_scenario="iiasa_evo_v1", n_val_locs=None):
    evo_ds = load_evo_dataset()
    v3_locs = evo_ds.locs
    if locs_scenario == 'iiasa_evo_v1':
        v3_locs = v3_locs[v3_locs['iiasa_evo_v1']]
    train_quarter_ids = list(set(
        v3_locs[v3_locs["selection_2"] == "train"]["quarter_id"]
    )
    )
    val_quarter_ids = list(set(
        v3_locs[v3_locs["selection_2"] == "val"]["quarter_id"]
    )
    )

    return train_quarter_ids, val_quarter_ids



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

SCALING_MEAN = {
    "VV": -10.658076652551959,
    "VH": -18.46767765550017,
    "VHVVRATIO": -7.905974709371844 
}

SCALING_STD = {
    "VV": 4.49800009777231,
    "VH": 5.845149113081188,
    "VHVVRATIO": 3.0364314364125082
}

def _linear_scaler(darr, band):
    b_mean = SCALING_MEAN[band]
    b_std = SCALING_STD[band]
    
    return (darr - b_mean) / b_std

def linear_scaler(darr, bands):
    list_darrs = [_linear_scaler(darr.sel(band=b), b) for b in bands]
        
    if len(list_darrs) > 1:
        darr_scaled = xr.concat(list_darrs, dim="band")
    else:
        darr_scaled = list_darrs[0]

    return darr_scaled

def _apply_augmented_scaling(
    darr, k_noised_signal, k_noised_dem, lat_jitter, lon_jitter
):
    dem_scaling = 4000
    lat_scaling = 90
    lon_scaling = 180

    # distinguish on bands that require special scaling
    signal_bands = [b for b in darr.band.values if b in BANDS_V2TSM_S2]
    gamma_bands = [b for b in darr.band.values if b in BANDS_V2TSM_S1_GAMMA0]
    # we rescale the dem band by 4000 as upper limit for high altitudes
    # we then apply the logistic scaling to it as well
    dem_band = ["cop-DEM-alt"] if "cop-DEM-alt" in darr.band.values else None  # noqa: E501
    lat_band = ["lat"] if "lat" in darr.band.values else None
    lon_band = ["lon"] if "lon" in darr.band.values else None

    # we rescale lat lon bands between their ranges, no logistic scaling
    darr_signal = darr.sel(band=signal_bands)
    if k_noised_signal > 0:
        darr_signal = logistic(darr_signal, k=k_noised_signal)

    if len(gamma_bands) == 0:
        darr_gamma = None
    else:   
        darr_gamma =  (
            linear_scaler(darr.sel(band=gamma_bands), gamma_bands) if gamma_bands is not None else None
        )

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
        d for d in (darr_signal, darr_gamma, darr_dem, darr_lat, darr_lon) if d is not None
    ]

    if len(darrs) > 1:
        darr = xr.concat(darrs, dim="band")
    else:
        darr = darrs[0]

    return darr


class EvoNetV1Dataset(Dataset):
    def __init__(
        self,
        quarter_ids=None,
        locs_scenario=None,
        dataset_path=None,
        dataset_s1_path=None,
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
        evo_dataset = load_evo_dataset(dataset_path, dataset_s1_path)
        if locs_scenario == 'iiasa_evo_v1':
            df_locs = evo_dataset.locs
            evo_dataset._locs = df_locs[df_locs['iiasa_evo_v1']]

        self.evo_dataset = evo_dataset
        evov2_dataset = load_evov2_dataset(datasetv2_path)
        self.evov2_dataset = evov2_dataset
        self._reader = evo_dataset._reader(dataset_path, dataset_s1_path)
        self.locs_scenario=locs_scenario

        self.reference_year = 2020

        if quarter_ids is None:
            if shuffle_locs:
                self.ids = list(set(evo_dataset.locs.sample(
                    frac=1, random_state=42
                ).quarter_id.values))
            if sort_locs_by_latitude:
                evo_dataset.locs["abs_lat"] = evo_dataset.locs.lat.abs()
                self.ids = list(set(evo_dataset.locs.sort_values(
                    "abs_lat"
                ).quarter_id.values))
            else:
                self.ids = list(set(evo_dataset.locs.quarter_id.values))
        else:
            self.ids = list(set(quarter_ids))

        self.bands = bands if bands is not None else DEFAULT_BANDS
        self.aux_bands = DEFAULT_AUX_BANDS
        self.rgb_bands = rgb_bands

        self.transforms = EvoTransforms_v2(
            flip_augmentation=flip_augmentation,
            rotate_augmentation=rotate_augmentation,
            fill=-1
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
        quarter_id = self.ids[idx]
        # randomly sample an observation of the patch within the requested quarter 
        df_locs = self.evo_dataset.locs
        row = df_locs[df_locs['quarter_id'] == quarter_id].sample(n=1).iloc[0]
        sample_id = row['sample_id']

        # we take the IIASA annotations if available
        # otherwise the LCM-10 based annotations
        if row['iiasa_evo_v1']:
            lab_source = 'evo-v1'
        else:
            lab_source = 'lcm'
        # print(sample_id)
            
        feats = self.read_feats(
            sample_id,
            self.bands,
            augmented_scaling=self._augmented_scaling,
            augmented_scaling_params=self._augmented_scaling_params,
            fill_value=-1
        )
        if feats.shape[-2] != 128:
            from loguru import logger
            logger.info(f'{sample_id} has shape {feats.shape}')
            
        if feats.shape[-1] != 128:
            from loguru import logger
            logger.info(f'{sample_id} has shape {feats.shape}')

        feats = feats.fillna(-1)  # fill nans for safety
        
        # for one out of 100 observations we fill all S1 data with missing values
        feats_bands = feats.band.data.tolist()
        feats_bands_s1 = [b for b in BANDS_V2TSM_S1_GAMMA0 if b in feats_bands]
        if (random.randrange(0,100) == 1) & (len(feats_bands_s1) > 1):
            for b in feats_bands_s1:
                feats.loc[dict(band=b)] = -1
                    
        # remapping_labels = {}  # removed mapping from v10
        prob_cover, prob_occlusion, prob_attribute, weight_cover, weight_occlusion, weight_attribute = self.read_evov1_target(sample_id, lab_source) 

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

        transformed = self.transforms(feats.data, feats_head, prob_cover.data, prob_occlusion.data, prob_attribute.data, weight_cover.data, weight_occlusion.data, weight_attribute.data)
        
        feats = transformed[0]
        feats_head = transformed[1]
        probs = transformed[2:5]
        weights_trans = transformed[5:]
        weights = []
        for w in weights_trans:
            w[w == -1] = 0
            weights.append(w)
                
        transformed = [feats, feats_head, probs, weights]
        
        return transformed

    def read_feats(
        self,
        sample_id,
        bands,
        augmented_scaling=False,
        augmented_scaling_params=None,
        fill_value=-1,
        eps=10e-5
    ):
        s2_feats = aux_feats = s1_feats = None

        s2_bands = [b for b in bands if b in BANDS_V2TSM_S2]
        s1_bands = [b for b in bands if b in BANDS_V2TSM_S1_GAMMA0]
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
        if len(s1_bands) > 0:
            s1_feats = self.read_s1feats(
                sample_id,
                s1_bands,
                augmented_scaling,
                augmented_scaling_params,
                eps=eps
            )
            if (s1_feats is None) & (len(s2_bands) > 0):
                # fill
                bounds = s2_feats.satio.bounds
                attrs = {"bounds": bounds}#"epsg": epsg, 
                new_y, new_x = compute_pixel_coordinates(bounds, s2_feats.shape[-2:])
                s1_arr = np.ones((len(s1_bands), s2_feats.shape[-2], s2_feats.shape[-1])) * fill_value

                s1_feats = xr.DataArray(
                    s1_arr,
                    dims=["band", "y", "x"],
                    coords={"band": s1_bands, "y": new_y, "x": new_x},
                    attrs=attrs,
                )
                
        darr = xr.concat(
            [arr for arr in (s2_feats, s1_feats, aux_feats) if arr is not None],
            dim="band",
            compat="equals",
        )

        # darr = darr.astype(np.float32)
        return darr
    
    def read_s1feats(
        self, 
        sample_id,
        bands, 
        augmented_scaling=False,
        augmented_scaling_params=None,
        eps=10e-5
    ):
        feats = self.evo_dataset.read(sample_id, bands, add_target=False)
        
        # convert to dB scale
        if feats is not None:
            feats = feats + eps
            feats.where(feats != 0, np.nan)
            feats = 10*np.log10(feats)
        
        if augmented_scaling & (feats is not None):
            augmented_scaling_params = (
                augmented_scaling_params or self._augmented_scaling_params
            )
            feats = apply_augmented_scaling(feats, **augmented_scaling_params)
            
        return feats

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

    def read_evov1_target(self, sample_id, lab_source='evo-v1'):
        # year = 2020
        version = 'v3'
        prob_cover = self.evo_dataset.read_annotation(
            sample_id, annotation_name=f"lsc-{lab_source}-prob-cover-{version}"
        )
        prob_occlusion = self.evo_dataset.read_annotation(
            sample_id, annotation_name=f"lsc-{lab_source}-prob-occlusion-{version}"
        )
        prob_attribute = self.evo_dataset.read_annotation(
            sample_id, annotation_name=f"lsc-{lab_source}-prob-attribute-{version}"
        )
        
        weight_cover = self.evo_dataset.read_annotation(
            sample_id, annotation_name=f"lsc-{lab_source}-weight-cover-{version}"
        )
        weight_cover = xr.concat([weight_cover for it in np.arange(len(prob_cover.band))], dim='band')
        
        weight_occlusion = self.evo_dataset.read_annotation(
            sample_id, annotation_name=f"lsc-{lab_source}-weight-occlusion-{version}"
        )
        weight_occlusion = xr.concat([weight_occlusion for it in np.arange(len(prob_occlusion.band))], dim='band')
        
        weight_attribute = self.evo_dataset.read_annotation(
            sample_id, annotation_name=f"lsc-{lab_source}-weight-attribute-{version}"
        )
        weight_attribute = xr.concat([weight_attribute for it in np.arange(len(prob_attribute.band))], dim='band')

        return prob_cover, prob_occlusion, prob_attribute, weight_cover, weight_occlusion, weight_attribute


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
    locs_scenario = config_dataloader["locs_scenario"]

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
        quarter_ids=train_locs,
        locs_scenario=locs_scenario,
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
        quarter_ids=val_locs,
        locs_scenario=locs_scenario,
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
