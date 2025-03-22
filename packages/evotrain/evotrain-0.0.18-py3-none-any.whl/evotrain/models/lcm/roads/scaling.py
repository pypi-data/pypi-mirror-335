import random
import numpy as np
import xarray as xr


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
    from evotrain.v2.bands import BANDS_V2_S2_FEATS

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

    darr_dem = darr.sel(band=dem_band) / dem_scaling if dem_band is not None else None
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

    darrs = [d for d in (darr_signal, darr_dem, darr_lat, darr_lon) if d is not None]

    if len(darrs) > 1:
        darr = xr.concat(darrs, dim="band")
    else:
        darr = darrs[0]

    return darr
