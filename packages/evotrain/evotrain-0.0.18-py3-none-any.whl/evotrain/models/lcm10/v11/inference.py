import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import torch
from loguru import logger
from rasterio.crs import CRS
from shapely.geometry import Point
from skimage.transform import resize

from evotrain.labels import binarize_probs
from evotrain.meteo import load_meteo_embeddings
from evotrain.models.lcm10.v11.dataset import (
    NET_LABELS,
    apply_augmented_scaling,
)
from evotrain.models.lcm10.v11.model import Net
from evotrain.v2 import lat_lon_to_unit_sphere

BASE_MODELS_PATH = Path("/vitodata/vegteam_vol2/models/lcm10/")

LCM10_BEST_VERSION = "v10b", 157


def load_latlon(bounds, epsg, resolution=10, steps=5):
    """
    Returns a lat, lon feature from the given bounds/epsg.

    This provide a coarse (but relatively fast) approximation to generate
    lat lon layers for each pixel.

    'steps' specifies how many points per axis should be use to perform
    the mesh approximation of the canvas
    """

    xmin, ymin, xmax, ymax = bounds
    out_shape = (
        int(np.floor((ymax - ymin) / resolution)),
        int(np.floor((xmax - xmin) / resolution)),
    )

    xx = np.linspace(xmin + resolution / 2, xmax - resolution / 2, steps)
    yy = np.linspace(ymax - resolution / 2, ymin + resolution / 2, steps)

    xx = np.broadcast_to(xx, [steps, steps]).reshape(-1)
    yy = np.broadcast_to(yy, [steps, steps]).T.reshape(-1)

    points = [Point(x0, y0) for x0, y0 in zip(xx, yy)]

    gs = gpd.GeoSeries(points, crs=CRS.from_epsg(epsg))
    gs = gs.to_crs(epsg=4326)

    lon_mesh = gs.apply(lambda p: p.x).values.reshape((steps, steps))
    lat_mesh = gs.apply(lambda p: p.y).values.reshape((steps, steps))

    lon = resize(lon_mesh, out_shape, order=1, mode="edge")
    lat = resize(lat_mesh, out_shape, order=1, mode="edge")

    return np.stack([lat, lon], axis=0).astype(np.float32)


def load_feats_head(bounds, epsg, year, resolution=10):
    meteo_emb = load_meteo_embeddings(
        bounds, epsg, year, bounds_buffer=3000, order=2
    )
    latlon = load_latlon(bounds, epsg, resolution=resolution)
    xyz = lat_lon_to_unit_sphere(latlon[0], latlon[1])

    feats_head = np.concatenate((xyz, meteo_emb), axis=0).astype(np.float32)
    return feats_head


def load_net_config(model_version, checkpoint_number):
    base_models_path = BASE_MODELS_PATH
    model_name = f"lcm10-{model_version}"
    model_path = base_models_path / model_name

    config_path = model_path / "config.json"
    with open(config_path, "r") as f:
        config = json.load(f)

    checkpoints = list(model_path.glob("**/*.ckpt"))
    checkpoint_path = [
        c for c in checkpoints if f"epoch={checkpoint_number}" in str(c)
    ][0]

    logger.info(f"Loading model from {checkpoint_path}")

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    net = Net(**config["model"]).load_from_checkpoint(
        checkpoint_path, map_location=device
    )
    _ = net.eval()
    net = net.to(device)
    return net, config


class Lcm10Inference:
    def __init__(self, model_version=None, checkpoint_number=None):
        if model_version is None:
            self.model_version, self.checkpoint_number = LCM10_BEST_VERSION
        else:
            self.model_version = model_version
            self.checkpoint_number = checkpoint_number

        self._net = None
        self._config = None
        self.labels = NET_LABELS

    @property
    def net(self):
        if self._net is None:
            self._net, self_config = load_net_config(
                self.model_version, self.checkpoint_number
            )
        return self._net

    @property
    def config(self):
        if self._config is None:
            self._net, self._config = load_net_config(
                self.model_version, self.checkpoint_number
            )
        return self._config

    @property
    def bands(self):
        return self.config["model"]["bands"]

    def scale_feats(self, feats):
        return apply_augmented_scaling(
            feats,
            k_factor=self.config["dataloader"]["k_factor"],
            k_factor_jitter=0,
        )

    def predict(self, feats, feats_head, return_conv=False):
        feats = self.scale_feats(feats)

        # check first feature. DEM could be NaN so we don't sum
        nodata_mask = np.isnan(feats.data[0])

        if np.isnan(feats.data).any():
            logger.warning("NaNs found in features. Returning NaNs in probs")
            feats = feats.fillna(0)

        if np.isnan(feats_head).any():
            logger.warning("NaNs found in head features. ")
            feats_head = feats_head.fillna(0)

        probs = self.net.model.predict(
            feats.data, feats_head, return_conv=return_conv
        )

        if return_conv:  # probs is a tuple of (probs, conv)
            probs, conv = probs
            probs[:, nodata_mask] = np.nan
            return probs, conv

        probs[:, nodata_mask] = np.nan
        return probs

    def load_feats_head(self, bounds, epsg, year):
        return load_feats_head(bounds, epsg, year)

    def prediction(self, probs, nodata_val=0):
        nodata_mask = np.isnan(probs).any(axis=0)
        pred = binarize_probs(probs, NET_LABELS)
        pred[nodata_mask] = nodata_val
        return pred
