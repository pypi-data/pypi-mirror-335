from pathlib import Path
from typing import List, Union

import joblib
import numpy as np
import pandas as pd
import xarray as xr
from loguru import logger
from satio_pc.extension import SatioTimeSeries  # noqa: F401

from evotrain import BANDS_L2A, BANDS_L2A_ALL
from evotrain.geotiff import load_features_geotiff
from evotrain.v2.bands import BANDS_V2_AUX, BANDS_V2_S2
from evotrain.v2tsm.bands import BANDS_V2TSM_S2, BANDS_V2TSM_S1_GAMMA0


def _v1_band_to_v2_band(band: str):
    if "0m" in band:
        band = band.replace("-10m", "")
        band = band.replace("-20m", "")

        if band.startswith("B") or band.startswith("ndvi"):
            band = "s2-" + band
        elif band.startswith("V") or band.startswith("vh"):
            band = "s1-" + band
        elif band.startswith("DEM"):
            band = "cop-" + band

    return band


def _v1_jlib_to_xarray(fn, v2_names=True):
    # Load data
    arr, bands, attr = joblib.load(fn)
    if v2_names:
        bands = [_v1_band_to_v2_band(b) for b in bands]

    # Derive pixel dimensions
    x_pixel_size = (attr["bounds"][2] - attr["bounds"][0]) / arr.shape[2]
    y_pixel_size = (attr["bounds"][3] - attr["bounds"][1]) / arr.shape[1]

    # Compute coordinates, shifting by half a pixel to get the center coords
    x_coords = np.arange(
        attr["bounds"][0] + x_pixel_size / 2, attr["bounds"][2], x_pixel_size
    )
    y_coords = np.arange(
        attr["bounds"][3] - y_pixel_size / 2, attr["bounds"][1], -y_pixel_size
    )

    # Create the DataArray
    data_array = xr.DataArray(
        arr,
        coords={"band": bands, "y": y_coords, "x": x_coords},
        dims=["band", "y", "x"],
    )

    data_array.attrs = attr

    return data_array


def slash_tile(tile: str):
    if len(tile) != 5:
        raise ValueError(f"tile should be a str of len 5, not {tile}")

    return f"{tile[:2]}/{tile[2]}/{tile[3:]}"


class BaseReader:
    def __init__(self, root_path) -> None:
        self._root_path = root_path

    def _patch_path(self, location_id: str, year: int) -> Path:
        tile = location_id.split("_")[0]
        basename = self._patch_basename(location_id, year)
        return self._root_path / "features" / f"{year}" / slash_tile(tile) / basename


class ReaderV1(BaseReader):
    def _patch_basename(self, location_id: str, year=None) -> str:
        return f"evoland_v1_{location_id}.jlib"

    def read(
        self, location_id: str, bands: List = None, v2_band_names=True
    ) -> xr.DataArray:
        year = 2021
        path = self._patch_path(location_id, year)
        da = _v1_jlib_to_xarray(path, v2_names=v2_band_names)
        if bands is not None:
            da = da.sel(band=bands)
        return da


class ReaderV2(BaseReader):
    def _patch_basename(self, location_id: str, year: int) -> str:
        return f"evotrain_v2_{year}_{location_id}.tif"

    def _aux_patch_path(self, location_id: str) -> Path:
        tile = location_id.split("_")[0]
        basename = f"evotrain_v2_{location_id}_aux.tif"
        return self._root_path / "aux" / slash_tile(tile) / basename

    def _annotation_patch_path(self, location_id: str, year: int, annotation_name: str):
        tile = location_id.split("_")[0]
        basename = f"evotrain_v2_{annotation_name}_{year}_{location_id}.tif"
        return self._root_path / "annotations" / f"{year}" / slash_tile(tile) / basename

    def _read(self, path: Union[str, Path], bands: List = None) -> xr.DataArray:
        da = load_features_geotiff(path, bands)
        if bands is not None:
            da = da.sel(band=bands)
        return da

    def _read_aux(self, location_id: str, bands: List = None):
        path = self._aux_patch_path(location_id)
        return self._read(path, bands)

    def _read_s2(self, location_id: str, year: int, bands: List = None) -> xr.DataArray:
        path = self._patch_path(location_id, year)
        return self._read(path, bands)

    def read_annotation(
        self, location_id: str, year: int, annotation_name: str
    ) -> xr.DataArray:
        path = self._annotation_patch_path(location_id, year, annotation_name)
        return self._read(path)

    def read(self, location_id: str, year: int, bands: List = None) -> xr.DataArray:
        # Split bands into categories
        bands_s2, bands_aux = _split_bands_v2(bands, year)

        # Read data for each category
        s2 = (
            self._read_s2(location_id, year, bands_s2) if bands_s2 is not None else None
        )
        aux = self._read_aux(location_id, bands_aux) if bands_aux is not None else None

        # Concatenate the data arrays
        darr = xr.concat(
            [arr for arr in (s2, aux) if arr is not None],
            dim="band",
            compat="equals",
        )

        darr = darr.astype(np.float32)
        return darr

    def _patch_path_gamm0(self, location_id: str, year: int) -> Path:
        tile = location_id.split("_")[0]
        basename = f"evotrain_v2_GAMMA0_{year}_{location_id}_GAMMA0.tif"
        return (
            self._root_path
            / "features_gamma0"
            / f"{year}"
            / slash_tile(tile)
            / basename
        )

    def read_gamma0(
        self,
        location_id: str,
        year: int,
        bands: List = None,
        resolution: int = 20,
    ) -> xr.DataArray:
        path = self._patch_path_gamm0(location_id, year)
        darr = self._read(path, bands)

        if resolution != 20:
            darr = darr.satio.superscale(
                scale=(20 / resolution),
                model_name="fsrcnn",
                progress_bar=False,
            )

    def _patch_path_osmroads(self, location_id: str) -> Path:
        tile = location_id.split("_")[0]
        basename = f"osm_roads_{location_id}.tif"
        return self._root_path / "osm" / slash_tile(tile) / basename

    def read_osmroads(self, location_id: str) -> xr.DataArray:
        path = self._patch_path_osmroads(location_id)

        darr = self._read(path)
        return darr


def _split_bands_v2(bands = None):
    if bands is None:
        return BANDS_V2_S2, BANDS_V2_AUX

    bands_s2 = [b for b in bands if b in BANDS_V2_S2]
    bands_aux = [b for b in bands if b in BANDS_V2_AUX]

    if len(bands_s2 + bands_aux) != len(bands):
        set_all = set(BANDS_V2_S2 + BANDS_V2_AUX)
        raise ValueError(
            f"The following bands could are not in the dataset: {set_all - set(bands)}"
        )

    if len(bands_s2) == 0:
        bands_s2 = None
    if len(bands_aux) == 0:
        bands_aux = None

    if (bands_s2 is None) and (bands_aux is None):
        # should not get here
        raise ValueError(f"No valid bands: {bands}")

    return bands_s2, bands_aux


class ReaderV2TS(BaseReader):
    def _patch_basename(self, location_id: str, year: int, resolution: int) -> str:
        # raw/2020/31/U/FS/10m/evotrain_v2ts_2020_31UFS_106_24_10m.nc
        return f"evotrain_v2ts_{year}_{location_id}_{resolution}m.nc"

    def _patch_path(self, location_id: str, year: int, resolution: int) -> Path:
        tile = location_id.split("_")[0]
        basename = self._patch_basename(location_id, year, resolution)
        return (
            self._root_path
            / "raw"
            / f"{year}"
            / slash_tile(tile)
            / f"{resolution}m"
            / basename
        )

    def read(
        self,
        location_id: str,
        year: int = 2020,
        bands: List = None,
        superres_20m_to_10m_model: bool = "fsrcnn",
        superres_60m_to_10m_model: bool = "fsrcnn",
    ) -> xr.DataArray:
        """
        Reads evotrain v2ts location data for a given location_id and year, and
        returns a xarray Dataset object. The data is optionally upscaled from
        20m and 60m to 10m resolution using the specified models.

        Args:
            location_id (str): The ID of the location to read data for.
            year (int, optional): The year to read data for. Defaults to 2020.
            bands (List, optional): A list of bands to read. Defaults to None.
            superres_20m_to_10m_model (bool, optional): The model to use for
                upscaling 20m bands to 10m resolution. Defaults to 'fsrcnn'.
            superres_60m_to_10m_model (bool, optional): The model to use for
                upscaling 60m bands to 10m resolution. Defaults to 'fsrcnn'.

        Returns:
            xr.Dataarray: Data at 10m resolution.
        """

        da = self.read_raw(location_id, year, bands)

        da10 = da.get(10)
        da20 = da.get(20)
        da60 = da.get(60)

        if da20 is not None:
            logger.info("Upscaling 20m bands to 10m")

            scl = False
            if "SCL" in da20.band.values:
                scl = True
                da20_scl = da20.sel(band=["SCL"])
                da20_scl = da20_scl.satio.rescale(
                    scale=2,  # scl uses nearest
                    order=0,
                )

            if (da20.band.values.size == 1) and scl:  # only SCL
                da20 = da20_scl
            else:
                da20 = da20.sel(band=[b for b in da20.band.values if b != "SCL"])
                da20 = da20.satio.superscale(
                    scale=2,
                    model_name=superres_20m_to_10m_model,
                    progress_bar=False,
                )
                if scl:
                    da20_scl = da20_scl.assign_coords(
                        title=("band", ["SCL - Scene Classification Layer"])
                    )
                    da20_scl = da20_scl.assign_coords(common_name=("band", ["SCL"]))
                    da20_scl = da20_scl.assign_coords(
                        center_wavelength=("band", [np.nan])
                    )
                    da20_scl = da20_scl.assign_coords(
                        full_width_half_max=("band", [np.nan])
                    )

                    da20 = xr.concat([da20, da20_scl], dim="band")

        if da60 is not None:
            logger.info("Upscaling 60m bands to 10m")
            da60 = da60.satio.superscale(
                scale=3,
                model_name=superres_60m_to_10m_model,
                progress_bar=False,
            )
            # they are now 66 x 66 pixels
            da60 = da60.isel(x=slice(1, -1), y=slice(1, -1))  # 64 x 64

            da60 = da60.satio.superscale(
                scale=2,
                model_name=superres_60m_to_10m_model,
                progress_bar=False,
            )

        # fix the x and y coords of the 60m rescaled array if necessary
        if (da10 is not None or da20 is not None) and (da60 is not None):
            da_ref = da10 if da10 is not None else da20
            da60 = da60.assign_coords(x=da_ref.x.values, y=da_ref.y.values)

        darrs = [d for d in [da10, da20, da60] if d is not None]
        da = xr.concat(darrs, dim="band", compat="equals")
        return da

    def read_raw(
        self,
        location_id: str,
        year: int = 2020,
        bands: List = None,
        resolution: int = None,
        view_angles: pd.DataFrame = None,
        **kwargs,
    ) -> xr.DataArray:
        if view_angles is None:
            view_angles = self._read_view_angles(location_id)

        if bands is not None and len(bands) == 0:
            return None

        if bands is None:
            bands = BANDS_L2A_ALL

        bands_dict = BANDS_L2A.copy()
        if ("SCL" in bands) and ("SCL" not in bands_dict[20]):
            bands_dict[20].append("SCL")

        bands_res = {r: [b for b in bands_dict[r] if b in bands] for r in (10, 20, 60)}

        if resolution is None:
            da = {
                res: self.read_raw(
                    location_id,
                    year,
                    bands_res[res],
                    res,
                    view_angles,
                    **kwargs,
                )
                for res in (10, 20, 60)
            }
            return da

        path = self._patch_path(location_id, year, resolution)
        with xr.open_dataarray(path, **kwargs) as da:
            if bands is not None:
                da = da.sel(band=bands)
            da = da.load()
            view_angles = view_angles.loc[da.id.values]

            # add angles
            da = da.assign_coords(
                {
                    "s2:mean_view_azimuth": (
                        "time",
                        view_angles["s2:mean_view_azimuth"],
                    ),
                    "s2:mean_view_zenith": (
                        "time",
                        view_angles["s2:mean_view_zenith"],
                    ),
                }
            )
            return da

    def _read_view_angles(
        self,
        location_id: str,
    ):
        """Reads the view angles for a given location_id, as they were
        not extracted originally.
        """
        tile = location_id.split("_")[0]
        view_angles_path = (
            self._root_path / "view_angles_2020" / f"{tile}_2020_coords.parquet"
        )

        angles = pd.read_parquet(view_angles_path)
        angles = angles.set_index("id")
        # angles = angles.loc[da10.id.values]
        return angles


def _split_bands_v2tsm(bands):
    if bands is None:
        return BANDS_V2TSM_S2, BANDS_V2TSM_S1_GAMMA0

    bands_s2 = [b for b in bands if b in BANDS_V2TSM_S2]
    bands_s1 = [b for b in bands if b in BANDS_V2TSM_S1_GAMMA0]

    if len(bands_s2 + bands_s1) != len(bands):
        set_all = set(BANDS_V2TSM_S2 + BANDS_V2TSM_S1_GAMMA0)
        raise ValueError(
            f"The following bands could are not in the dataset: {set_all - set(bands)}"
        )

    if len(bands_s2) == 0:
        bands_s2 = None
    if len(bands_s1) == 0:
        bands_s1 = None

    if (bands_s2 is None) and (bands_s1 is None):
        # should not get here
        raise ValueError(f"No valid bands: {bands}")

    return bands_s2, bands_s1


class ReaderV2TSM:
    def __init__(self, root_path_s2, root_path_s1=None) -> None:
        self._root_path_s2 = root_path_s2
        self._root_path_s1 = root_path_s1

    def _patch_path(self, sample_id: str) -> Path:
        tile = sample_id.split("_")[0]
        date = sample_id.split("_")[-1]
        year, month, day = date[:4], date[4:6], date[6:]
        basename = self._patch_basename(sample_id)
        return (
            self._root_path_s2
            / "data"
            / f"{year}"
            / f"{month}"
            / slash_tile(tile)
            / basename
        )

    def _patch_basename(self, sample_id: str) -> str:
        return f"evotrain_v2tsm_{sample_id}.tif"

    def _annotation_patch_path(self, sample_id: str, annotation_name: str):
        tile = sample_id.split("_")[0]
        date = sample_id.split("_")[-1]
        year, month, day = date[:4], date[4:6], date[6:]
        basename = f"evotrain_v2tsm_{annotation_name}_{sample_id}.tif"
        return (
            self._root_path_s2
            / "annotations"
            / f"{year}"
            / f"{month}"
            / slash_tile(tile)
            / basename
        )

    def _read(self, path: Union[str, Path], bands: List = None) -> xr.DataArray:
        da = load_features_geotiff(path, bands)
        if bands is not None:
            da = da.sel(band=bands)
        return da

    def _read_s2(self, sample_id: str, bands: List = None) -> xr.DataArray:
        path = self._patch_path(sample_id)
        return self._read(path, bands)

    def _s1_patch_path(self, sample_id: str) -> Path:
        location_id = "_".join(sample_id.split("_")[:-1])
        tile = sample_id.split("_")[0]
        date = sample_id.split("_")[-1]
        year, month, day = date[:4], date[4:6], date[6:]
        basename = f"LCFM_GAMMA0-RAW_{year}_{location_id}_V001.nc"
        return self._root_path_s1 / "patches" / slash_tile(tile) / str(year) / basename

    def _read_s1(self, sample_id: str, bands: List = None) -> xr.DataArray:
        date_str = sample_id.split("_")[-1]
        year, month, day = date_str[:4], date_str[4:6], date_str[6:]
        date = np.datetime64(f"{year}-{month}-01")

        path = self._s1_patch_path(sample_id)
        if path.exists():
            darr = xr.open_dataset(path)

            list_darrs = []
            for band in bands:
                darr_b = darr[band]
                darr_b = darr_b.rename({"t": "time"})
                darr_b = darr_b.expand_dims({"band": 1}, axis=1)
                darr_b = darr_b.assign_coords(band=[band])
                list_darrs.append(darr_b)
            darr_s1 = xr.concat(
                list_darrs,
                dim="band",
                compat="equals",
            )
            darr_s1 = darr_s1.satio.rescale(scale=2, order=0)
            if date in list(darr_s1.time.data):
                return darr_s1.sel(time=date)
            else:
                return None
        else:
            return None

    def read_annotation(self, sample_id: str, annotation_name: str) -> xr.DataArray:
        path = self._annotation_patch_path(sample_id, annotation_name)
        return self._read(path)

    def read(
        self, sample_id: str, bands: List = None, add_target=True, annotation_name=None
    ) -> xr.DataArray:
        bands_s2, bands_s1 = _split_bands_v2tsm(bands)

        s2 = annotation = s1 = None

        if bands_s2 is not None:
            s2 = self._read_s2(sample_id, bands_s2)

        if add_target:
            if annotation_name is None:
                raise TypeError(
                    "`annotation_name` is not set. Please provide it explicitly."
                )
            annotation = self.read_annotation(sample_id, annotation_name)

        if bands_s1 is not None:
            s1 = self._read_s1(sample_id, bands_s1)

        if (s2 is None) & (s1 is None) & (annotation is None):
            return None

        else:
            darr = xr.concat(
                [arr for arr in (s2, s1, annotation) if arr is not None],
                dim="band",
                compat="equals",
            )

            darr = darr.astype(np.float32)
            return darr
