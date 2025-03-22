import random
from importlib.resources import files
from pathlib import Path

import pandas as pd

from evotrain.reader import ReaderV2TS
from evotrain.v2.bands import BANDS_V2_AUX, BANDS_V2_RGB

# try to read from disk, as package data can cause issues on cluster
_DATASET_PATH_MEP = Path(
    "/vitodata/vegteam_vol2/training/evotrain_v2ts")
_DATASET_PATH_HPC = Path("/vitodata/vegteam_vol2/training/evotrain_v2ts")

if _DATASET_PATH_MEP.is_dir():
    DATASET_PATH = _DATASET_PATH_MEP
elif _DATASET_PATH_HPC.is_dir():
    DATASET_PATH = _DATASET_PATH_HPC
else:
    DATASET_PATH = None

# _SUPPORTED_DATA = ('locs', 'hists', 'norm')
_SUPPORTED_DATA = ('locs',)
_base_paths = {k: f"{k}.parquet" for k in _SUPPORTED_DATA}

if DATASET_PATH:
    METADATA_PATH = DATASET_PATH / 'metadata' / 'raw'
    _data_paths = {k: METADATA_PATH / _base_paths[k]
                   for k in _SUPPORTED_DATA}
else:
    METADATA_PATH = None
    _data_paths = {k: files("evotrain.v2ts.metadata").joinpath(
        _base_paths[k]) for k in _SUPPORTED_DATA}


def _load(key: str, columns=None):
    """_summary_

    Args:
        key (str): one of 'locs', 'hists', 'norm'
    """
    if key not in _SUPPORTED_DATA:
        raise ValueError(f"Unrecognized metadata table key {key}. "
                         f"Should be one of {_SUPPORTED_DATA}")

    return pd.read_parquet(_data_paths[key], columns=columns)


BANDS_L2A = {10: ['B02', 'B03', 'B04', 'B08'],
             20: ['B05', 'B06', 'B07', 'B8A', 'B11', 'B12'],
             60: ['B01', 'B09']}


class EvoTrainV2TSDataset:

    def __init__(self, dataset_path=None) -> None:
        self._hists = None
        self._norm = None
        self._locs = None
        self._locs_gdf = None
        self._bands = None
        self._location_ids = None
        self.years = [2020]
        self.bands_s2 = BANDS_L2A
        self.bands_aux = BANDS_V2_AUX
        self.bands_rgb = BANDS_V2_RGB
        self.bands = BANDS_L2A

        if dataset_path is None:
            dataset_path = DATASET_PATH
        self.dataset_path = dataset_path

    @property
    def hists(self):
        if self._hists is not None:
            self._hists = _load('hists')
        return self._hists

    @property
    def norm(self):
        if self._norm is None:
            self._norm = _load('norm')
        return self._norm

    @property
    def locs(self):
        if self._locs is None:
            self._locs = _load('locs')
            self._location_ids = self._locs.location_id.astype(
                "string[pyarrow]")
        return self._locs

    @property
    def locs_gdf(self):
        if self._locs_gdf is None:
            import geopandas as gpd
            from shapely.geometry import Point
            locs = self.locs.copy()
            locs['geometry'] = locs.apply(lambda row: Point(row.lon, row.lat),
                                          axis=1)
            locs = gpd.GeoDataFrame(locs, crs=4326)
            self._locs_gdf = locs
        return self._locs_gdf

    @property
    def location_ids(self):
        if self._location_ids is None:
            self._location_ids = _load('locs', columns=['location_id'])[
                'location_id'].astype("string[pyarrow]")
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
            raise TypeError("`dataset_path` could not be found automatically."
                            " Please provide it explicitly.")
        return ReaderV2TS(dataset_path)

    def read(self, location_id, year, bands=None, dataset_path=None):
        return self._reader(dataset_path).read(location_id, year, bands)

    def patch_ids(self, location_ids=None, years=None,
                  fraction=1, shuffle_random_state=None):

        if location_ids is None:
            location_ids = self.location_ids

        if years is None:
            years = self.years

        patch_ids = [(loc_id, year)
                     for loc_id in location_ids
                     for year in years]

        if shuffle_random_state is not None:
            random.seed(shuffle_random_state)
            random.shuffle(patch_ids)

        # Select a fraction of the list
        num_elements = int(fraction * len(patch_ids))
        patch_ids_fraction = patch_ids[:num_elements]

        return patch_ids_fraction


dataset = EvoTrainV2TSDataset()
