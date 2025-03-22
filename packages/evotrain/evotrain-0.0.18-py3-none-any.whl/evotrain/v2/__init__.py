import random
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger

from evotrain._version import __version__
from evotrain.v2.bands import BANDS_V2_AUX, BANDS_V2_RGB, BANDS_V2_S2
from climatic_regions import lat_lon_to_unit_sphere

__all__ = ["__version__"]

# try to read from disk, as package data can cause issues on cluster
_DATASET_PATH_MEP = Path("/vitodata/vegteam_vol2/training/evotrain_v2")
_DATASET_PATH_HPC_NODE5 = Path("/local/TAP/vegteam/training_data/evotrain_v2")
_DATASET_PATH_HPC = Path("/projects/TAP/vegteam/training_data/evotrain_v2")

if _DATASET_PATH_MEP.is_dir():
    DATASET_PATH = _DATASET_PATH_MEP
elif _DATASET_PATH_HPC_NODE5.is_dir():
    DATASET_PATH = _DATASET_PATH_HPC_NODE5
elif _DATASET_PATH_HPC.is_dir():
    DATASET_PATH = _DATASET_PATH_HPC
else:
    DATASET_PATH = None

if DATASET_PATH is not None:
    logger.info(f"Found dataset at {DATASET_PATH}")
else:
    logger.warning("Could not find dataset. Please provide it explicitly.")

_SUPPORTED_DATA = (
    "locs",
    "hists",
    "norm",
    "locs_h3",
    "locs_v3",
    "locs_evo-v1",
    "meteo_biome_features_v1",
)
_base_paths = {k: f"{k}.parquet" for k in _SUPPORTED_DATA}

if DATASET_PATH is not None:
    METADATA_PATH = DATASET_PATH / "metadata"
    _data_paths = {k: METADATA_PATH / _base_paths[k] for k in _SUPPORTED_DATA}
else:
    try:
        from importlib.resources import files

        _data_paths = {
            k: files("evotrain.v2.metadata").joinpath(_base_paths[k])
            for k in _SUPPORTED_DATA
        }
    except ImportError:
        # python 3.8 compatibility
        _data_paths = {}
        import importlib.resources as pkg_resources

        for k in _SUPPORTED_DATA:
            with pkg_resources.path(
                "evotrain.v2.metadata", _base_paths[k]
            ) as resource_path:
                _data_paths[k] = resource_path


def _load(key: str, columns=None):
    """_summary_

    Args:
        key (str): one of 'locs', 'hists', 'norm'
    """
    if key not in _SUPPORTED_DATA:
        raise ValueError(
            f"Unrecognized metadata table key {key}. Should be one of {_SUPPORTED_DATA}"
        )
    logger.debug(f"Loading {key} from {_data_paths[key]}")
    return pd.read_parquet(_data_paths[key], columns=columns)


class EvoTrainV2Dataset:
    def __init__(
        self,
        dataset_path=None,
        locs_tag="locs_v3",
        locs_groups=(0, 1, 2),
        filter_aux=True,
        filter_meteo=True,
        filter_osm=True,
    ) -> None:
        """
        locs_tag can be 'locs', 'locs_h3', 'locs_v3', 'locs_evo-v1'
        """
        self._hists = None
        self._norm = None
        self._locs = None
        self._locs_gdf = None
        self._locs_tag = locs_tag  # can be 'locs', 'locs_h3' or 'locs_v3'
        self._locs_groups = locs_groups
        self._filter_aux = filter_aux  # filter out locations that do not have aux data
        self._filter_meteo = (
            filter_meteo  # filter out locations that do not have meteo data
        )
        self._filter_osm = filter_osm  # filter out locations that do not have osm data
        self._meteo_features = None
        self._meteo_features_names = ["meteo_" + str(i) for i in range(6)]
        self._bands = None
        self._location_ids = None
        self.years = (2018, 2019, 2020, 2021, 2022)
        self.bands_s2 = BANDS_V2_S2
        self.bands_aux = BANDS_V2_AUX
        self.bands_rgb = BANDS_V2_RGB
        self.bands = BANDS_V2_S2 + BANDS_V2_AUX

        if dataset_path is None:
            dataset_path = DATASET_PATH
            logger.debug(f"Using dataset path {dataset_path}")
        self.dataset_path = dataset_path

    @property
    def hists(self):
        if self._hists is not None:
            self._hists = _load("hists")
        return self._hists

    @property
    def norm(self):
        if self._norm is None:
            self._norm = _load("norm")
        return self._norm

    @property
    def locs(self):
        if self._locs is None:
            self._locs = _load(self._locs_tag)
            self._location_ids = self._locs.location_id.astype("string[pyarrow]")
            if "group" in self._locs.columns:
                logger.debug(f"Getting only locations in groups {self._locs_groups}")
                self._locs = self._locs[self._locs.group.isin(self._locs_groups)]

            if ("aux" in self._locs.columns) & self._filter_aux:
                logger.debug("Filtering out locations without aux data")
                self._locs = self._locs[self._locs.aux]
            elif self._filter_aux and "aux" not in self._locs.columns:
                raise ValueError("No aux column found! Cannot filter aux data.")

            if ("meteo" in self._locs.columns) & self._filter_meteo:
                logger.debug("Filtering out locations without meteo data")
                self._locs = self._locs[self._locs.meteo]
            elif self._filter_meteo and "meteo" not in self._locs.columns:
                raise ValueError("No meteo column found! Cannot filter meteo data.")

            if ("osm_roads" in self._locs.columns) & self._filter_osm:
                before = len(self._locs)
                logger.debug("Filtering out locations without osm data")
                self._locs = self._locs[self._locs.osm_roads]
                logger.debug(f"Filtered out {before - len(self._locs)} locations")
            elif self._filter_osm and "osm_roads" not in self._locs.columns:
                raise ValueError("No osm_roads column found! Cannot filter osm data.")

        return self._locs

    @property
    def locs_gdf(self):
        if self._locs_gdf is None:
            import geopandas as gpd
            from shapely.geometry import Point

            locs = self.locs.copy()
            locs["geometry"] = locs.apply(lambda row: Point(row.lon, row.lat), axis=1)
            locs = gpd.GeoDataFrame(locs, crs=4326)
            self._locs_gdf = locs
        return self._locs_gdf

    @property
    def location_ids(self):
        if self._location_ids is None:
            self._location_ids = _load("locs", columns=["location_id"])[
                "location_id"
            ].astype("string[pyarrow]")
        return self._location_ids

    @property
    def meteo_features(self):
        if self._meteo_features is None:
            self._meteo_features = _load("meteo_biome_features_v1")
        return self._meteo_features

    def band_stats(self, band: str, stats_index: str):
        """Return stats value for band.

        Args:
            stats_index (str): stats should be a str among
            {self.norm.index.values.tolist()}

            band (str): stat should be a str among
            {self.norm.columns.values.tolist()}

        Returns:
            float: value of the request statistic
        """
        if isinstance(stats_index, float):
            stats_index = str(stats_index)
        return self.norm.loc[stats_index, band]

    def _reader(self, dataset_path: str = None):
        from evotrain.reader import ReaderV2

        if dataset_path is None:
            dataset_path = self.dataset_path
        if dataset_path is None:
            raise TypeError(
                "`dataset_path` could not be found automatically."
                " Please provide it explicitly."
            )
        return ReaderV2(dataset_path)

    def read(self, location_id, year, bands=None, dataset_path=None):
        return self._reader(dataset_path).read(location_id, year, bands)

    def read_annotation(self, location_id, year, annotation_name):
        return self._reader().read_annotation(location_id, year, annotation_name)

    def read_osmroads(self, location_id):
        return self._reader().read_osmroads(location_id)

    def read_meteo_features_vec(self, location_id, year):
        feats = self.meteo_features.loc[
            (self.meteo_features.location_id == location_id)
            & (self.meteo_features.year == year),
            self._meteo_features_names,
        ]
        assert len(feats), f"No meteo features found for {location_id}, {year}"
        return feats.iloc[0].values

    def read_head_features_xyz(self, location_id, latlon_jitter=1):
        locs = self.locs
        try:
            loc = locs[locs.location_id == location_id].iloc[0]
        except IndexError:
            raise ValueError(f"Location {location_id} not found in locs")
        lat, lon = loc.lat, loc.lon
        feats = np.ones((2, 128, 128))
        feats[0] = feats[0] * lat
        feats[1] = feats[1] * lon

        if latlon_jitter:
            feats += np.random.uniform(
                -latlon_jitter, latlon_jitter, feats.size
            ).reshape(feats.shape)

        feats = np.array(lat_lon_to_unit_sphere(feats[0], feats[1]))

        return feats

    def read_head_features_meteo(self, location_id, year, meteo_jitter=0.1):
        meteo = self.read_meteo_features_vec(location_id, year)
        feats = np.ones((meteo.shape[0], 128, 128))
        feats = feats * meteo[:, None, None]

        if meteo_jitter:
            feats += np.random.uniform(-meteo_jitter, meteo_jitter, feats.size).reshape(
                feats.shape
            )
            feats = np.clip(feats, 0, 1)

        return feats

    def read_head_features(
        self,
        location_id,
        year,
        meteo_jitter=0.1,
        latlon_jitter=1,
    ):
        # logger.debug(f"Reading head features for {location_id}, {year}")
        xyz = self.read_head_features_xyz(location_id, latlon_jitter)
        meteo = self.read_head_features_meteo(location_id, year, meteo_jitter)
        return np.concatenate((xyz, meteo), axis=0).astype(np.float32)

    def patch_ids(
        self,
        location_ids=None,
        years=None,
        fraction=1,
        shuffle_random_state=None,
    ):
        if location_ids is None:
            location_ids = self.location_ids

        if years is None:
            years = self.years

        patch_ids = [(loc_id, year) for loc_id in location_ids for year in years]

        if shuffle_random_state is not None:
            random.seed(shuffle_random_state)
            random.shuffle(patch_ids)

        # Select a fraction of the list
        num_elements = int(fraction * len(patch_ids))
        patch_ids_fraction = patch_ids[:num_elements]

        return patch_ids_fraction


dataset = EvoTrainV2Dataset()
