import numpy as np
import xarray as xr
import rasterio
from loguru import logger


def read_band(
    band, filenames_dict, source_resolution=60, target_resolution=60, apply_offset=True
):
    """
    Read the band from the given filename and resolution.
    An S2 tile has dimensions 109800m x 109800m:
    - At 80m resolution, the tile has 109800 / 80 = 1372.5 pixels
    - At 60m resolution, the tile has 109800 / 60 = 1830 pixels
    - At 40m resolution, the tile has 109800 / 40 = 2745 pixels
    - At 20m resolution, the tile has 109800 / 20 = 5489 pixels
    - At 10m resolution, the tile has 109800 / 10 = 10978 pixels

    Parameters
    ----------
    band : str
        The band to read.
    filenames_dict : dict
        Dictionary containing filenames for each resolution and band.
    source_resolution : int, optional
        The resolution of the source band, by default 60.
    target_resolution : int, optional
        The resolution to resample the band to, by default 60.
    apply_offset : bool, optional
        Whether to apply an offset to the data, by default True.

    Returns
    -------
    numpy.ndarray
        The read and resampled band data.
    """
    filename = filenames_dict[source_resolution][band]
    resampling_factor = target_resolution // source_resolution

    with rasterio.open(filename) as src:
        if resampling_factor == 1:
            logger.debug(f"Reading band {band} without resampling.")
            data = src.read(1)
        else:
            logger.debug(
                f"Reading and resampling band {band} from shape {src.shape} to shape ({src.shape[0] // resampling_factor}, {src.shape[1] // resampling_factor})."
            )
            data = src.read(
                1,
                out_shape=(
                    src.shape[0] // resampling_factor,
                    src.shape[1] // resampling_factor,
                ),
            )

        data = data.astype(np.float32)
        if apply_offset and band != "SCL":
            logger.debug(f"Applying offset to band {band}.")
            data -= 1000.0

    logger.debug(f"Finished reading band {band}.")
    return data


def get_filenames_dict(product_collection, bands_list, source_resolution=60):
    """
    Retrieve the filenames for the specified bands in the bands_list.

    Parameters
    ----------
    product_collection : veg_workflows.collections.ProductCollection
        Collection of products.
    bands_list : list of str
        List of bands to retrieve.
    source_resolution : int, optional
        Resolution of the source bands, by default 60.

    Returns
    -------
    dict
        Dictionary containing the filenames for the bands in the bands_list
        at the specified resolution (source_resolution).

    Examples
    --------
    Example usage:

    >>> from veg_workflows.products import Loi10Product
    >>> from veg_workflows.collections import veg_collections
    >>> s2_pid = "S2A_MSIL2A_20200612T023601_N0500_R089_T50NKJ_20230327T190018"
    >>> loi10prod = Loi10Product(
    ...     s2_product_id=s2_pid,
    ...     project_name="LCFM",
    ...     version='v001',
    ...     products_base_path="/vitodata/vegteam_vol2/products/",
    ...     product_name="LOI-10",
    ... )
    >>> collection = getattr(veg_collections, 'lcfm_10percent')
    >>> s2grid = veg_collections.s2grid
    >>> product_collection = collection.__class__(
    ...     collection.df[collection.df.product_id == s2_pid],
    ...     s2grid
    ... )
    >>> filenames_dict = get_filenames_dict(
    ...     product_collection,
    ...     bands_list=["SCL"],
    ...     source_resolution=60
    ... )
    >>> filenames_dict
    {
        60: {
            'SCL': (
                '/data/MTDA/CGS_S2/CGS_S2_L2A/2020/06/12/'
                'S2A_MSIL2A_20200612T023601_N0500_R089_T50NKJ_20230327T190018/'
                'S2A_MSIL2A_20200612T023601_N0500_R089_T50NKJ_20230327T190018.SAFE/'
                'GRANULE/L2A_T50NKJ_A025969_20200612T025028/IMG_DATA/R60m/'
                'T50NKJ_20200612T023601_SCL_60m.jp2'
            )
        }
    }
    """
    logger.debug(
        f"Retrieving filenames for bands: {bands_list} at resolution: {source_resolution}m."
    )
    bands = {source_resolution: bands_list}
    filenames = {}
    for res in bands.keys():
        logger.debug(f"Processing resolution: {res}m.")
        filenames[res] = {}
        for b in bands[res]:
            logger.debug(f"Retrieving filename for band: {b} at resolution: {res}m.")
            filenames[res][b] = product_collection.get_band_filenames(b, res)[0]
            logger.debug(f"Retrieved filename: {filenames[res][b]}")
    logger.debug("Finished retrieving filenames.")
    return filenames


def build_bands_data_array(
    filenames_dict,
    bands_list,
    source_resolution=60,
    target_resolution=60,
    apply_offset=True,
):
    """
    Read and resample the bands in the bands_list from the filenames_dict.

    Parameters
    ----------
    filenames_dict : dict
        Dictionary containing filenames for each resolution and band.
    bands_list : list of str
        List of bands to read and resample.
    source_resolution : int, optional
        The resolution of the source bands, by default 60.
    target_resolution : int, optional
        The resolution to resample the bands to, by default 60.

    Returns
    -------
    xarray.DataArray
        DataArray containing the read and resampled bands.

    Examples
    --------
    Example filenames_dict:

    >>> filenames_dict = {
    ...     60: {
    ...         "B02": "path/to/B02.jp2",
    ...         "B03": "path/to/B03.jp2",
    ...         ...
    ...     },
    ...     20: {
    ...         "B02": "path/to/B02.jp2",
    ...         "B03": "path/to/B03.jp2",
    ...         ...
    ...     }
    ... }
    """
    logger.debug(
        f"Building DataArray for bands: {bands_list} with source resolution: {source_resolution}m and target resolution: {target_resolution}m."
    )

    data_all_bands = {
        band: read_band(
            band,
            filenames_dict,
            source_resolution,
            target_resolution,
            apply_offset=apply_offset,
        )
        for band in bands_list
    }

    logger.debug("All bands read and resampled successfully.")

    data_array = xr.DataArray(
        data=np.stack(list(data_all_bands.values()), axis=0),
        dims=["band", "y", "x"],
        coords={"band": bands_list},
    )

    logger.debug("Bands DataArray built successfully.")

    return data_array
