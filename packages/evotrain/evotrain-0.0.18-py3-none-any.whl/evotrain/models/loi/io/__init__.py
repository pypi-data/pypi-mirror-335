from loguru import logger

try:
    from satio.satio_pc.geotiff import get_rasterio_profile_shape, write_geotiff_tags
except Exception as e:
    logger.error(
        f"Failed to import satio.satio_pc.geotiff: {e}. Using fallback implementation."
    )
    from satio_pc.geotiff import get_rasterio_profile_shape, write_geotiff_tags


def save_geotiff(
    arr,
    bounds,
    epsg,
    filename,
    colormap=None,
    scales=None,
    nodata_value=None,
    bands_names=None,
    bands_tags=None,
    offsets=None,
    tags=None,
):
    """
    Given a numpy array, bounds, epsg, and filename, this function
    will save the array as a GeoTIFF with the specified bounds and epsg.

    Args:
    arr (np.ndarray): The numpy array
    bounds (tuple): The bounds of the GeoTIFF
    epsg (int): The EPSG code
    filename (str): The filename to save the GeoTIFF
    colormap (dict): The colormap to use for the GeoTIFF

    Returns:
    None
    """
    logger.debug("Starting save_geotiff function")
    logger.debug(
        f"Array shape: {arr.shape}, bounds: {bounds}, EPSG: {epsg}, filename: {filename}"
    )

    # First let's get the rasterio profile shape using function: get_rasterio_profile_shape
    rasterio_profile_shape = get_rasterio_profile_shape(
        list(arr.shape), bounds, epsg, arr.dtype
    )
    logger.debug(f"Rasterio profile shape: {rasterio_profile_shape}")

    # Now we can write the geotiff tags using the write_geotiff_tags function
    if colormap is not None:
        logger.debug("Colormap provided, modifying colormap values")
        # Append a 255 at the end of each value in the colormap dictionary
        # each value is a numpy array like so: np.array([155,255,0])
        colormap = {k: tuple(v.tolist() + [255]) for k, v in colormap.items()}
        logger.debug(f"Modified colormap: {colormap}")

    logger.debug("Writing GeoTIFF tags")
    write_geotiff_tags(
        arr=arr,
        profile=rasterio_profile_shape,
        filename=filename,
        colormap=colormap,
        scales=scales,
        nodata=nodata_value,
        bands_names=bands_names,
        bands_tags=bands_tags,
        offsets=offsets,
        tags=tags,
    )
    logger.debug("GeoTIFF saved successfully")
