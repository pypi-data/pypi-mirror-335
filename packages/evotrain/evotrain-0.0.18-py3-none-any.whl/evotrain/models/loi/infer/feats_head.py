def get_feats_head(shape_X, epsg, bounds, date, model_config):
    """
    Generate the feature head for the model

    Args:
    - shape_X: shape of the input tensor
    - epsg: EPSG code of the input data
    - bounds: bounds of the input data
    - date: date of the input data
    - model_config: model configuration

    Returns:
    - feats_head: feature head for the model
    """
    import numpy as np
    from loguru import logger

    from evotrain.models.loi.data.seasonality import day_of_year_cyclic_feats
    from climatic_regions import (
        load_meteo_embeddings,
        load_latlon,
        lat_lon_to_unit_sphere,
    )

    resolution = model_config["data_config"]["resolution"]
    try:
        year = int(str(date)[:4])
    except Exception as e:
        logger.error(f"Error in extracting year from date: {date}, {e}")

    feats_head = []
    if "meteo" in model_config["dl_model_config"]["bands_head"]:
        logger.info("Loading meteo embeddings")
        meteo_emb = load_meteo_embeddings(
            bounds, epsg, year, bounds_buffer=3000, order=2, resolution=resolution
        )
        logger.debug(f"Meteo embeddings loaded with shape: {meteo_emb.shape}")

        meteo_emb /= 250
        logger.debug("Meteo embeddings scaled to 0-1 range")
        feats_head.append(meteo_emb)

    if "latlon" in model_config["dl_model_config"]["bands_head"]:
        logger.info("Loading latlon and converting to unit sphere (x,y,z)")
        lat, lon = load_latlon(bounds, epsg, resolution=resolution)
        xx, yy, zz = lat_lon_to_unit_sphere(lat, lon)
        logger.debug("Latlon converted to unit sphere")

        xx = np.full((1, shape_X[1], shape_X[2]), xx)
        yy = np.full((1, shape_X[1], shape_X[2]), yy)
        zz = np.full((1, shape_X[1], shape_X[2]), zz)
        logger.debug(
            f"Unit sphere arrays created with shapes: {xx.shape}, {yy.shape}, {zz.shape}"
        )
        feats_head.append(xx)
        feats_head.append(yy)
        feats_head.append(zz)

    if "seasonal" in model_config["dl_model_config"]["bands_head"]:
        logger.info("Generating seasonal features")
        sin_cos = day_of_year_cyclic_feats(
            str(date), doy_jitter=0, height=shape_X[1], width=shape_X[2]
        )
        # Let's scale the sin_cos features to the range [0, 1]
        sin_cos = (sin_cos + 1) / 2
        logger.debug(f"Seasonal features generated with shape: {sin_cos.shape}")
        feats_head.append(sin_cos)

    feats_head = np.concatenate(feats_head, axis=0).astype(np.float32)
    logger.info(f"Feature head generated with shape: {feats_head.shape}")

    return feats_head
