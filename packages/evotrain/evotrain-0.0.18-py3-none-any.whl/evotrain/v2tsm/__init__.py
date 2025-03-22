import random
from importlib.resources import files
from pathlib import Path

import pandas as pd
from loguru import logger


# Function to find the first existing path from a list of paths
def find_existing_path(paths):
    for path in paths:
        if path.is_dir():
            return path
    return None


# Define possible dataset paths for different environments
DATASET_PATHS = [
    Path("/vitodata/vegteam_vol2/training/evotrain_v2tsm"),
    Path("/local/TAP/vegteam/training_data/evotrain_v2tsm"),
    Path("/projects/TAP/vegteam/training_data/evotrain_v2tsm"),
]

# Define possible Sentinel-1 dataset paths for different environments
DATASET_S1_PATHS = [
    Path("/vitodata/vegteam_vol2/training/LCFM/GAMMA0-RAW/v001/"),
    Path("/local/TAP/vegteam/training_data/GAMMA0-RAW/v001/"),
    Path("/projects/TAP/vegteam/training_data/GAMMA0-RAW/v001/"),
]


# Set DATASET_PATH and DATASET_S1_PATH
DATASET_PATH = find_existing_path(DATASET_PATHS)
DATASET_S1_PATH = find_existing_path(DATASET_S1_PATHS)

# Log the status of the dataset paths
logger.info(
    f"Found dataset at {DATASET_PATH}"
    if DATASET_PATH
    else "Could not find dataset. Please provide it explicitly."
)
logger.info(
    f"Found S1 dataset at {DATASET_S1_PATH}"
    if DATASET_S1_PATH
    else "Could not find S1 dataset. Please provide it explicitly."
)

# Supported metadata tables
_SUPPORTED_DATA = ("locs",)
# Base paths for the supported metadata tables
_base_paths = {k: f"{k}.parquet" for k in _SUPPORTED_DATA}

# Set metadata paths based on the dataset path
if DATASET_PATH:
    METADATA_PATH = DATASET_PATH / "metadata"
    _data_paths = {k: METADATA_PATH / _base_paths[k] for k in _SUPPORTED_DATA}
else:
    METADATA_PATH = None
    _data_paths = {
        k: files("evotrain.v2tsm.metadata").joinpath(_base_paths[k])
        for k in _SUPPORTED_DATA
    }


def _load(key: str, columns=None):
    """_summary_

    Args:
        key (str): one of 'locs', 'hists', 'norm'
    """
    if key not in _SUPPORTED_DATA:
        raise ValueError(
            f"Unrecognized metadata table key {key}. Should be one of {_SUPPORTED_DATA}"
        )

    return pd.read_parquet(_data_paths[key], columns=columns)


class EvoTrainV2TSMDataset:
    def __init__(self, dataset_path=None, dataset_s1_path=None) -> None:
        self._locs = None
        self._locs_gdf = None
        self._bands = None
        self._location_ids = None
        self._sample_ids = None
        self._quarter_ids = None
        self.years = [2020]

        if dataset_path is None:
            dataset_path = DATASET_PATH
        if dataset_s1_path is None:
            dataset_s1_path = DATASET_S1_PATH
        self.dataset_path = dataset_path
        self.dataset_s1_path = dataset_s1_path

    @property
    def locs(self):
        if self._locs is None:
            self._locs = _load("locs")
            self._location_ids = self._locs.location_id.astype("string[pyarrow]")
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
    def quarter_ids(self):
        if self._quarter_ids is None:
            self._quarter_ids = self.locs["quarter_id"].astype("string[pyarrow]")
            # self._quarter_ids = _load("locs", columns=["quarter_id"])[
            #     "location_id"
            # ].astype("string[pyarrow]")
        return self._quarter_ids

    @property
    def location_ids(self):
        if self._location_ids is None:
            self._location_ids = self.locs["location_id"].astype("string[pyarrow]")
            # self._location_ids = _load("locs", columns=["location_id"])[
            #     "location_id"
            # ].astype("string[pyarrow]")
        return self._location_ids

    @property
    def sample_ids(self):
        if self._sample_ids is None:
            self._sample_ids = self.locs["sample_id"].astype("string[pyarrow]")
            # self._sample_ids = _load("locs", columns=["sample_id"])[
            #     "sample_id"
            # ].astype("string[pyarrow]")
        return self._sample_ids

    def _reader(self, dataset_path: str = None, dataset_s1_path: str = None):
        from evotrain.reader import ReaderV2TSM

        if dataset_path is None:
            dataset_path = self.dataset_path
        if dataset_s1_path is None:
            dataset_s1_path = self.dataset_s1_path

        if dataset_path is None:
            raise TypeError(
                "`dataset_s2_path` could not be found automatically."
                " Please provide it explicitly."
            )
        return ReaderV2TSM(dataset_path, dataset_s1_path)

    def read_annotation(self, sample_id, annotation_name=None, dataset_path=None):
        return self._reader(dataset_path).read_annotation(sample_id, annotation_name)

    def read(
        self,
        sample_id,
        bands=None,
        add_target=True,
        annotation_name=None,
        dataset_path=None,
        dataset_s1_path=None,
    ):
        return self._reader(dataset_path, dataset_s1_path).read(
            sample_id, bands, add_target, annotation_name
        )


dataset = EvoTrainV2TSMDataset()
