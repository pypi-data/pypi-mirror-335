# Folder structure

"""
V3 Dataset folder structure


evotrain_v3/
    data/
        timeseries/
            v1/
                2018/31/U/FS/31UFS_048_01_{year}_{layer}_{version}.tif
                ...
                2022/
        features/
            v1/
                2018/31/U/FS/31UFS_048_01_{year}_{layer}_{version}.tif
                ...
                2022/
        annotations/
            worldcover-2021/
                2018/31/U/FS/31UFS_048_01_{year}_{layer}.tif
                ...
                2022/
            builtup-v1/
                2018/
                ...
                2022/
            ...
    models/
        model_name/
            model_files
        README.md
    locations/
        locations_files

"""

import random
from pathlib import Path

import pandas as pd
from loguru import logger

from evotrain._version import __version__
from evotrain.v2.bands import BANDS_V2_AUX, BANDS_V2_RGB, BANDS_V2_S2

__all__ = ["__version__"]

# try to read from disk, as package data can cause issues on cluster
_DATASET_PATH_MEP = Path("/vitodata/vegteam_vol2/training/evotrain_v3")
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
    logger.warning("Could not find dataset. " "Please provide it explicitly.")

_SUPPORTED_DATA = ["evotrain_v3_locations"]
LOCS_BASENAME = f"{_SUPPORTED_DATA[0]}.parquet"

if DATASET_PATH:
    LOCS_PATH = DATASET_PATH / "locations" / LOCS_BASENAME
else:
    try:
        from importlib.resources import files

        LOCS_PATH = files("evotrain.v3.metadata").joinpath(LOCS_BASENAME)

    except ImportError:
        # python 3.8 compatibility
        _data_paths = {}
        import importlib.resources as pkg_resources

        with pkg_resources.path(
            "evotrain.v3.metadata", LOCS_BASENAME
        ) as resource_path:
            LOCS_PATH = resource_path

_data_paths = {}
_data_paths["locs"] = LOCS_PATH


def _load(key: str, columns=None):
    """_summary_

    Args:
        key (str): one of 'locs', 'hists', 'norm'
    """
    if key not in _SUPPORTED_DATA:
        raise ValueError(
            f"Unrecognized metadata table key {key}. "
            f"Should be one of {_SUPPORTED_DATA}"
        )

    return pd.read_parquet(_data_paths[key], columns=columns)


class EvoTrainV2Dataset:
    def __init__(self, dataset_path=None, group=1) -> None:
        """EvoTrainV2Dataset

        Args:
            dataset_path ([type], optional): path to dataset folder.
                Defaults to None.
            group (int, optional): Should be 0, 1 or 2. Group 0 are all
                locations not in group 1 and 2. Group 1 is 30k training set.
                Group 2 is 33k test set selected in similar manner to group 1.
                Defaults to 1.
        """
        if group not in (0, 1, 2):
            raise ValueError("group should be 0, 1 or 2")

        self._hists = None
        self._norm = None
        self._locs = None
        self._locs_gdf = None
        self._group = group  # can be 'locs' or 'locs_h3'
        self._bands = None
        self._location_ids = None
        self.years = (2018, 2019, 2020, 2021, 2022)
        self.bands_s2 = BANDS_V2_S2
        self.bands_aux = BANDS_V2_AUX
        self.bands_rgb = BANDS_V2_RGB
        self.bands = BANDS_V2_S2 + BANDS_V2_AUX

        if dataset_path is None:
            dataset_path = DATASET_PATH
        self.dataset_path = dataset_path

    @property
    def locs(self):
        if self._locs is None:
            self._locs = _load(self._locs_tag)
            self._location_ids = self._locs.location_id.astype(
                "string[pyarrow]"
            )
        return self._locs

    @property
    def locs_gdf(self):
        if self._locs_gdf is None:
            import geopandas as gpd
            from shapely.geometry import Point

            locs = self.locs.copy()
            locs["geometry"] = locs.apply(
                lambda row: Point(row.lon, row.lat), axis=1
            )
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

        patch_ids = [
            (loc_id, year) for loc_id in location_ids for year in years
        ]

        if shuffle_random_state is not None:
            random.seed(shuffle_random_state)
            random.shuffle(patch_ids)

        # Select a fraction of the list
        num_elements = int(fraction * len(patch_ids))
        patch_ids_fraction = patch_ids[:num_elements]

        return patch_ids_fraction


dataset = EvoTrainV2Dataset()
