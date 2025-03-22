from dataclasses import dataclass
from pathlib import Path

import contextily as cx
import geopandas as gpd
import hvplot.pandas  # noqa
import hvplot.xarray  # noqa
import joblib
import numpy as np
import pandas as pd
import panel as pn  # noqa
import skimage
import xarray as xr
import xyzservices.providers as xyz
from loguru import logger
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.transform import from_bounds
from rasterio.warp import reproject
from satio_pc.geotiff import get_rasterio_profile_shape, write_geotiff_tags
from satio_pc.grid import slash_tile
# from satio_pc.superres import SuperRes
from satio_pc.superres.super_image import SuperImage
from shapely.geometry import Polygon
from skimage import color
from sklearn.cluster import KMeans
from sklearn.neural_network import MLPClassifier, MLPRegressor
from umap import UMAP

from evotrain.labels import label_to_rgb
from evotrain.v2 import dataset
from evotrain.v2.dataloaders import apply_k_scaling_bands_ndvi


def plot_rgb(darr, title=None, width=450, **kwargs):

    defaults = dict(x='x',
                    y='y',
                    bands='band',
                    data_aspect=1,
                    xaxis=None,
                    yaxis=None,
                    width=width,
                    title=title)

    defaults.update(**kwargs)
    plot = darr.hvplot.rgb(**defaults)
    return plot


def plot_image(darr, title=None, width=450, **kwargs):

    defaults = dict(x='x',
                    y='y',
                    data_aspect=1,
                    xaxis=None,
                    yaxis=None,
                    width=width,
                    title=title,
                    cmap='magma')

    defaults.update(**kwargs)
    plot = darr.hvplot.image(**defaults)
    return plot


def to_dataarray(arr, bounds=None, epsg=None, bands=None, attrs=None):

    if bounds is None:
        bounds = [0, 0, 1, 1]
    if bands is None and arr.ndim == 3:
        bands = [str(i) for i in range(arr.shape[0])]

    xmin, ymin, xmax, ymax = bounds
    resolution_x = (xmax - xmin) / arr.shape[-1]
    resolution_y = (ymax - ymin) / arr.shape[-2]
    y = np.linspace(ymax - resolution_y / 2,
                    ymin + resolution_y / 2,
                    arr.shape[-2])
    x = np.linspace(xmin + resolution_x / 2,
                    xmax - resolution_x / 2,
                    arr.shape[-1])

    if arr.ndim == 3:
        darr = xr.DataArray(arr,
                            dims=['band', 'y', 'x'],
                            coords={'y': y,
                                    'x': x,
                                    'band': bands})
    elif arr.ndim == 2:
        darr = xr.DataArray(arr,
                            dims=['y', 'x'],
                            coords={'y': y,
                                    'x': x})
    else:
        raise ValueError("Array must be 2D or 3D")
    new_attrs = dict(bounds=bounds,
                     epsg=epsg)
    if attrs is None:
        attrs = new_attrs
    else:
        attrs.update(new_attrs)

    darr.attrs = attrs

    return darr


def norm_diff(darr, band1, band2, p=50):
    b1 = darr.sel(band=f's2-B{band1:02d}-p{p}')
    b2 = darr.sel(band=f's2-B{band2:02d}-p{p}')
    d = (b1 - b2) / (b1 + b2)
    return d


def colormap_from_rgb(labels, im_rgb, method='first'):
    """
    Generates a colormap from RGB values.

    Args:
        labels (numpy.ndarray): Array of labels.
        im_rgb (numpy.ndarray): Array of RGB values.

    Returns:
        dict: A dictionary containing the label as the key and a list
        of RGBA values as the value.
    """
    colormap = {}
    for label in np.unique(labels):
        mask = labels == label
        row, col = np.where(mask)
        if method == 'first':
            r, g, b = im_rgb[:, row[0], col[0]]
        elif method == 'avg':
            r, g, b = im_rgb[:, row, col].mean(axis=1)
        else:
            raise ValueError(f"Unknown method {method}, "
                             "should be 'first' or 'avg'")
        colormap[label] = list(map(int,
                                   [r * 255, g * 255, b * 255, 255]))
    return colormap


feats_bands_10m = ['s2-B02-p10', 's2-B02-p25', 's2-B02-p50', 's2-B02-p75', 's2-B02-p90',  # noqa E501
                   's2-B03-p10', 's2-B03-p25', 's2-B03-p50', 's2-B03-p75', 's2-B03-p90',  # noqa E501
                   's2-B04-p10', 's2-B04-p25', 's2-B04-p50', 's2-B04-p75', 's2-B04-p90',  # noqa E501
                   's2-B08-p10', 's2-B08-p25', 's2-B08-p50', 's2-B08-p75', 's2-B08-p90',  # noqa E501
                   's2-ndvi-p10', 's2-ndvi-p25', 's2-ndvi-p50', 's2-ndvi-p75', 's2-ndvi-p90']  # noqa E501

feats_bands_20m = ['s2-B11-p10', 's2-B11-p25', 's2-B11-p50', 's2-B11-p75', 's2-B11-p90',  # noqa E501
                   's2-B12-p10', 's2-B12-p25', 's2-B12-p50', 's2-B12-p75', 's2-B12-p90']  # noqa E501

feats_bands = feats_bands_10m + feats_bands_20m
# feats_bands = [f for f in feats_bands if 'p10' not in f]
# feats_bands = [f for f in feats_bands if 'p90' not in f]
# feats_bands = [f for f in feats_bands if 'p50' in f]


class EvoExplorer:

    def __init__(self,
                 loc_id,
                 year=2021,
                 bands=None,
                 overwrite_cache=False,
                 bands_k_scaling=None,
                 ndvi_k_scaling=None,
                 superres_model='edsr-base',
                 superres_models_dir=None,
                 plots_width=450) -> None:
        """
        Initializes an instance of the Explorer class.

        Args:
            loc_id (int): The ID of the location to explore.
            year (int, optional): The year of the data to explore.
                Defaults to 2021.
            bands (list, optional): The list of bands to use. Defaults to None.
            superres_model (str, optional): The name of the super-resolution
                model to use.
                See satio_pc.superres.super_image.SuperImage for a list of 
                available models ('drln', 'drln-bam', 'mdsr', 'edsr-base',
                'edsr', 'msrn', 'a2n', 'pan'). Defaults to 'edsr-base'. 
            superres_models_dir (str, optional): The directory where the 
                super-resolution models are stored. Defaults to 
                XDG_CACHE_DIR env var or Path.home / '.cache' when None.
            plots_width (int, optional): The width of the plots to generate.
                Defaults to 450.
        """
        if bands is None:
            bands = feats_bands
        self.bands = bands
        self.year = year

        locs_gdf = dataset.locs_gdf
        self.locs_gdf = locs_gdf
        self.loc_id = loc_id

        loc_gdf = locs_gdf[locs_gdf.location_id == loc_id]
        row = loc_gdf.iloc[0]
        self.row = row
        self.bounds = (row.xmin,
                       row.ymin,
                       row.xmax,
                       row.ymax)
        self.epsg = row.epsg
        self.bbox = self._get_bbox(row)

        self.bands_k_scaling = bands_k_scaling
        self.ndvi_k_scaling = ndvi_k_scaling
        self.overwrite_cache = overwrite_cache

        self._feats = None
        self._feats_hr = None
        self._sres = SuperImage(superres_model,
                                cache_dir=superres_models_dir)
        self.plots_width = 450

        self._im_rgb = None
        self._im_ndvi = None
        self._im_lc = None
        self._im_fc = None

        self._im_umap = None
        self._im_umap_hr = None
        self._umap_mlp = None

        self._wc_rgb = None
        self._wc_lab = None
        self._wc_mlp = None
        self._wc_lab_hr = None
        self._wc_rgb_hr = None

        self._im_vhres = None

        self._seg_masks = None

    def to_dataarray(self, arr, bands=None):
        return to_dataarray(arr, self.bounds, self.epsg, bands)

    def to_geotiff(self, arr, fn,
                   bands=None,
                   colormap=None,
                   nodata=None,
                   tags=None
                   ):
        if isinstance(arr, xr.DataArray):
            arr = arr.data

        profile = get_rasterio_profile_shape(arr.shape,
                                             self.bounds,
                                             self.epsg,
                                             dtype=arr.dtype)
        write_geotiff_tags(arr,
                           profile,
                           fn,
                           bands_names=bands,
                           colormap=colormap,
                           nodata=nodata,
                           tags=tags)

    def _get_bbox(self, row):
        bbox = gpd.GeoSeries([Polygon.from_bounds(*self.bounds)],
                             crs=f'EPSG:{row.epsg}').to_crs(epsg=4326)
        bbox = gpd.GeoDataFrame(bbox, columns=['geometry'])
        return bbox

    @property
    def feats(self):
        if self._feats is None:
            self._feats = dataset.read(self.loc_id, self.year, self.bands)
            self._feats.name = self.loc_id
            if self.bands_k_scaling is not None:
                self._feats = apply_k_scaling_bands_ndvi(self._feats,
                                                         self.bands_k_scaling,
                                                         self.ndvi_k_scaling)
        return self._feats

    def feats_multiple_years(self, years=(2018, 2019, 2020, 2021, 2022)):
        feats = [dataset.read(self.loc_id,
                              year,
                              self.bands).expand_dims(
                                  time=[pd.Timestamp(f"{year}-01-01")])
                 for year in years]
        if self.bands_k_scaling is not None:
            feats = [apply_k_scaling_bands_ndvi(f,
                                                self.bands_k_scaling,
                                                self.ndvi_k_scaling)
                     for f in feats]
        feats = xr.concat(feats, dim='time', compat='equals')
        return feats

    @property
    def feats_hr(self):
        if self._feats_hr is None:
            feats_hr = self._sres.upscale(self.feats.data,
                                          scale=4)
            self._feats_hr = self.to_dataarray(feats_hr,
                                               bands=self.feats.band.values)
            self._feats_hr.name = self.loc_id
        return self._feats_hr

    def get_rgb_im(self, vmin=None, vmax=None, hr=False, bands=None):
        if bands is None:
            bands = ['s2-B04-p50',
                     's2-B03-p50',
                     's2-B02-p50']

        feats = self.feats_hr if hr else self.feats

        im_rgb = feats.sel(band=bands)
        vmin = im_rgb.min() if vmin is None else vmin
        vmax = im_rgb.max() if vmax is None else vmax
        eps = 1e-7
        im_rgb = (im_rgb.clip(vmin, vmax) - vmin) / (vmax - vmin + eps)
        return im_rgb

    @property
    def im_rgb(self):
        if self._im_rgb is None:
            rgb_bands = ['s2-B04-p50',
                         's2-B03-p50',
                         's2-B02-p50']

            self._im_rgb = self.get_rgb_im(hr=True,
                                           bands=rgb_bands)

        return self._im_rgb

    @property
    def im_fc(self):
        if self._im_fc is None:
            fc_bands = ['s2-B08-p50',
                        's2-B04-p50',
                        's2-B03-p50']

            self._im_fc = self.get_rgb_im(hr=True,
                                          bands=fc_bands)

        return self._im_fc

    @property
    def im_ndvi(self):
        if self._im_ndvi is None:
            ndvi_bands = ['s2-ndvi-p90',
                          's2-ndvi-p50',
                          's2-ndvi-p10']
            ndvi_vmin = 0
            ndvi_vmax = 0.8

            self._im_ndvi = self.get_rgb_im(ndvi_vmin, ndvi_vmax,
                                            hr=True,
                                            bands=ndvi_bands)
        return self._im_ndvi

    @property
    def im_lc(self):
        if self._im_lc is None:
            p = 50

            b12_min = 0.0
            b12_max = 0.2

            bndvi_min = 0
            bndvi_max = 0.9

            bndvi = self.feats_hr.sel(band=f's2-ndvi-p{p}').data.copy()
            b12 = self.feats_hr.sel(band=f's2-B12-p{p}').data.copy()
            b12[b12 < b12_min] = b12_min
            b12[b12 > b12_max] = b12_max
            bndvi[bndvi < bndvi_min] = bndvi_min
            bndvi[bndvi > bndvi_max] = bndvi_max

            b12 = (b12 - b12_min) / (b12_max - b12_min)
            bndvi = (bndvi - bndvi_min) / (bndvi_max - bndvi_min)

            # landcover water index
            lcwi = ((-bndvi + 1) * (-b12 + 1))

            comp = np.array([b12, bndvi, lcwi])

            comp = self.to_dataarray(comp, bands=['b12', 'bndvi', 'lcwi'])
            self._im_lc = comp
        return self._im_lc

    def plot(self,
             im=None,
             title=None,
             width=None,
             band_id=None,
             values_range=None,
             **kwargs):

        if isinstance(im, np.ndarray):
            im = self.to_dataarray(im)

        if width is None:
            width = self.plots_width

        if im is None:
            return self._plot_esri()

        if values_range is not None:
            vmin, vmax = values_range
            im = im.copy().clip(vmin, vmax)
            eps = 1e-7
            im = (im - vmin) / (vmax - vmin + eps)

        if im.ndim == 2:
            return plot_image(im,
                              title=title,
                              width=width,
                              **kwargs)

        if band_id is not None:
            return plot_image(im.isel(band=band_id),
                              title=title,
                              width=width,
                              **kwargs)
        else:
            return plot_rgb(im,
                            title=title,
                            width=width,
                            **kwargs)

    def _plot_esri(self):

        xmin, ymin, xmax, ymax = self.bbox.iloc[0].geometry.bounds
        xlim = (xmin, xmax)
        ylim = (ymin, ymax)

        plot_esri = self.bbox.hvplot(
            frame_height=self.plots_width,
            tiles='ESRI',
            fill_color='none',
            line_color='orange',
            line_width=3,
            xlim=xlim,
            ylim=ylim,
            title=f"VHRES - {self.loc_id}",
            xaxis=None, yaxis=None)

        return plot_esri

    def get_umap_feats(self,
                       n_neighbors=100,
                       min_dist=0.25,
                       n_components=3):

        umap_nn_path = (dataset.dataset_path /
                        f'dev/umap_nn_{self.year}/{slash_tile(self.row.tile)}/'
                        f'umap_nn_{self.loc_id}.jlib')

        if umap_nn_path.is_file() and not self.overwrite_cache:
            logger.info("Loading UMAP Transformer")
            umap_mlp = joblib.load(umap_nn_path)
            umap_wrap_mlp = FeatsModel(umap_mlp)
            im_umap = umap_wrap_mlp.predict(self.feats)
            im_umap[im_umap < 0] = 0
            im_umap[im_umap > 1] = 1

        else:
            logger.info("Running UMAP")
            u = UMAP(
                n_neighbors=n_neighbors,
                min_dist=min_dist,
                n_components=n_components,
                random_state=None,
            )
            umap_wrap = FeatsModel(u)
            im_umap = umap_wrap.fit_transform(self.feats,
                                              normalize=True)

            logger.info("Training UMAP mlp and expanding to 2.5m")
            umap_wrap_mlp = FeatsModel(MLPRegressor())
            umap_wrap_mlp = umap_wrap_mlp.fit(self.feats, im_umap)

            umap_nn_path.parent.mkdir(exist_ok=True, parents=True)
            joblib.dump(umap_wrap_mlp.model, umap_nn_path)

        im_umap_hr = umap_wrap_mlp.predict(self.feats_hr)
        im_umap_hr[im_umap_hr < 0] = 0
        im_umap_hr[im_umap_hr > 1] = 1

        im_umap = self.to_dataarray(im_umap,
                                    bands=['umap1', 'umap2', 'umap3'])
        im_umap_hr = self.to_dataarray(im_umap_hr,
                                       bands=['umap1', 'umap2', 'umap3'])

        return im_umap, im_umap_hr, umap_wrap_mlp

    @property
    def im_umap(self):
        if self._im_umap is None:
            (self._im_umap,
             self._im_umap_hr,
             self._umap_mlp) = self.get_umap_feats()
        return self._im_umap

    @property
    def im_umap_hr(self):
        if self._im_umap_hr is None:
            (self._im_umap,
             self._im_umap_hr,
             self._umap_mlp) = self.get_umap_feats()
        return self._im_umap_hr

    @property
    def umap_mlp(self):
        if self._umap_mlp is None:
            (self._im_umap,
             self._im_umap_hr,
             self._umap_mlp) = self.get_umap_feats()
        return self._umap_mlp

    @property
    def wc_mlp(self):
        if self._wc_mlp is None:
            logger.info("Training WorldCover MLP")
            wc_mlp = FeatsModel(MLPClassifier()).fit(self.im_umap,
                                                     self.wc_lab)
            self._wc_mlp = wc_mlp
        return self._wc_mlp

    @property
    def wc_lab(self):
        if self._wc_lab is None:

            year = 2021  # only year in the dataset to load...
            wc_lab = dataset.read(self.loc_id,
                                  year,
                                  [f'worldcover_{year}']).isel(band=0
                                                               ).data.round()

            self._wc_lab = wc_lab
        return self._wc_lab

    @property
    def wc_rgb(self):
        if self._wc_rgb is None:
            wc_rgb = label_to_rgb(self.wc_lab)
            self._wc_rgb = self.to_dataarray(wc_rgb, bands=['r', 'g', 'b'])
        return self._wc_rgb

    @property
    def wc_lab_hr(self):
        if self._wc_lab_hr is None:
            wc_lab_hr = self.wc_mlp.predict(self.im_umap_hr)
            self._wc_lab_hr = np.squeeze(wc_lab_hr)
        return self._wc_lab_hr

    @property
    def wc_rgb_hr(self):
        if self._wc_rgb_hr is None:
            wc_rgb_hr = label_to_rgb(self.wc_lab_hr)
            self._wc_rgb_hr = self.to_dataarray(wc_rgb_hr,
                                                bands=['r', 'g', 'b'])
        return self._wc_rgb_hr

    def extract_vhres(self, source=None, zoom=16,
                      height=1024, width=1024):
        """
        Extracts a high-resolution (VHRES) image from a given source and
        reprojects it to match the bounding box of the current row.

        Args:
            source (TileProvider, optional): The tile provider to use for
                downloading the image. Defaults to xyz.Esri.WorldImagery.
            zoom (int, optional): The zoom level to use for downloading the
                image. Defaults to 16.
            height (int, optional): The height of the output image in pixels.
                Defaults to 1024.
            width (int, optional): The width of the output image in pixels.
                Defaults to 1024.

        Returns:
            np.ndarray: A 3D numpy array representing the extracted VHRES
            image, with shape (channels, height, width) and dtype np.float32.
            The pixel values are normalized to the range [0, 1].
        """
        if source is None:
            source = xyz.Esri.WorldImagery

        logger.info("Extracting VHRES imagery at 1m")
        row = self.row

        # Extract bounding box in Web Mercator
        w, s, e, n = self.bbox.to_crs(epsg=3857).total_bounds
        # Download image
        img, ext = cx.bounds2img(w, s, e, n,
                                 source=source,
                                 zoom=zoom)

        img = img[..., :3]  # get rid of alpha
        img = np.moveaxis(img, 2, 0)

        src_crs = CRS.from_epsg(3857)
        src_bounds = (ext[0], ext[2], ext[1], ext[3])
        src_ch, src_h, src_w = img.shape
        src_transform = from_bounds(*src_bounds, src_w, src_h)

        dst_crs = CRS.from_epsg(row.epsg)
        dst_bounds = row.xmin, row.ymin, row.xmax, row.ymax
        dst_h, dst_w = height, width
        dst_transform = from_bounds(*dst_bounds, dst_w, dst_h)

        vhres = np.zeros((src_ch, dst_h, dst_w), dtype=np.float32)

        for ch in range(src_ch):
            _ = reproject(
                source=img[ch],
                destination=vhres[ch],
                src_transform=src_transform,
                src_crs=src_crs,
                dst_transform=dst_transform,
                dst_crs=dst_crs,
                resampling=Resampling.cubic
            )
        vhres = vhres / 255.
        vhres = vhres - vhres.min()
        vhres = vhres / vhres.max()
        vhres = self.to_dataarray(vhres, bands=['r', 'g', 'b'])

        return vhres

    @property
    def im_vhres(self):
        if self._im_vhres is None:
            self._im_vhres = self.extract_vhres()
        return self._im_vhres

    def get_segmentation_masks(self,
                               quickshift_params=None,
                               n_clusters=16,
                               ):

        logger.info("Running quickshift segmentation on UMAP hr")
        if quickshift_params is None:
            quickshift_params = dict(ratio=1,
                                     kernel_size=3,
                                     max_dist=10)

        quick_seg = skimage.segmentation.quickshift(self.im_umap_hr.data,
                                                    channel_axis=0,
                                                    convert2lab=True,
                                                    **quickshift_params)

        quick_seg_umap = color.label2rgb(quick_seg,
                                         self.im_umap_hr.data,
                                         kind='avg',
                                         bg_label=None,
                                         channel_axis=0)

        logger.info("KMeans Clustering avg UMAP on quickshift super pixels")
        km = FeatsModel(KMeans(n_clusters=n_clusters))
        _ = km.fit_transform(quick_seg_umap)
        klabs = km.model.labels_.reshape(quick_seg.shape)

        klabs_umap = color.label2rgb(klabs, self.im_umap_hr.data,
                                     kind='avg', bg_label=None,
                                     channel_axis=0)
        klabs_rgb = color.label2rgb(klabs, self.im_rgb.data,
                                    kind='avg', bg_label=None,
                                    channel_axis=0)
        klabs_ndvi = color.label2rgb(klabs, self.im_ndvi.data,
                                     kind='avg', bg_label=None,
                                     channel_axis=0)
        klabs_lc = color.label2rgb(klabs, self.im_lc.data,
                                   kind='avg', bg_label=None,
                                   channel_axis=0)

        masks = (quick_seg, quick_seg_umap,
                 klabs, klabs_umap,
                 klabs_rgb, klabs_ndvi, klabs_lc)

        masks_names = ('quick_seg', 'quick_seg_umap',
                       'klabs', 'klabs_umap',
                       'klabs_rgb', 'klabs_ndvi', 'klabs_lc')
        masks = {name: self.to_dataarray(m)
                 for name, m in zip(masks_names, masks)}

        return SegMasks(**masks)

    @property
    def seg_masks(self):
        if self._seg_masks is None:
            self._seg_masks = self.get_segmentation_masks()
        return self._seg_masks

    def plot_all(self, output_folder=None):
        plot_vhres = self.plot(self.im_vhres, title='VHRES 1m')
        plot_wc = self.plot(self.wc_rgb, title='WorldCover 2021 10m')

        plot_s2_ndvi = self.plot(self.im_ndvi, title='S2 NDVI 2.5m')
        plot_s2_rgb = self.plot(self.im_rgb, title='S2 RGB 2.5m')
        plot_lc = self.plot(self.im_lc, title='LandCover Composite 2.5m')
        plot_wc_hr = self.plot(
            self.wc_rgb_hr, title='WorldCover 2021 2.5m')
        plot_umap = self.plot(self.im_umap_hr, title='UMAP')
        plot_quick = self.plot(self.seg_masks.quick_seg_umap,
                               title='QuickSeg')

        seg_masks: SegMasks = self.seg_masks
        plot_klabs_ndvi = self.plot(
            seg_masks.klabs_ndvi, title='Segments (NDVI avg)')
        plot_klabs_rgb = self.plot(
            seg_masks.klabs_rgb, title='Segments (RGB avg)')
        plot_klabs_umap = self.plot(seg_masks.klabs_umap,
                                    title='Segments')
        plot_klabs_lc = self.plot(seg_masks.klabs_lc,
                                  title='Segments')

        plot = (plot_vhres + plot_wc + plot_wc_hr +
                plot_s2_rgb + plot_s2_ndvi + plot_lc +
                plot_klabs_rgb + plot_klabs_ndvi + plot_klabs_lc +
                plot_umap + plot_quick + plot_klabs_umap).cols(3)

        if output_folder is not None:
            logger.info("Saving...")
            fn = Path(output_folder) / f'explore_segments_{self.loc_id}.html'
            hvplot.save(plot, fn)
        return plot


@dataclass
class SegMasks:
    quick_seg: xr.DataArray
    quick_seg_umap: xr.DataArray
    klabs: xr.DataArray
    klabs_umap: xr.DataArray
    klabs_rgb: xr.DataArray
    klabs_ndvi: xr.DataArray
    klabs_lc: xr.DataArray


class FeatsModel:

    def __init__(self, model=None):

        if model is None:
            model = MLPRegressor()
        self.model = model

    def _to_vec(self, feats):
        if isinstance(feats, xr.DataArray):
            feats = feats.data
        if feats.ndim == 2:
            feats = feats[np.newaxis, ...]
        nbands, ny, nx = feats.shape
        X = feats.reshape(nbands, -1).T
        X = np.squeeze(X)
        return X

    def _from_vec(self, X, shape):
        feats = X.T.reshape(*shape)
        return feats

    def fit(self, feats_x, feats_y):
        X = self._to_vec(feats_x)
        y = self._to_vec(feats_y)
        self.model.fit(X, y)
        return self

    def fit_transform(self, feats_x, normalize=True):
        X = self._to_vec(feats_x)
        preds = self.model.fit_transform(X)

        if normalize:
            # normalize on each channel
            preds = preds - preds.min(axis=0)
            preds = preds / preds.max(axis=0)

        _, ny, nx = feats_x.shape
        nbands = int(preds.size / (ny * nx))
        preds = self._from_vec(preds,
                               (nbands, ny, nx))
        return preds

    def predict(self, feats_x):
        X = self._to_vec(feats_x)
        if hasattr(self.model, 'transform'):
            preds = self.model.transform(X)
        elif hasattr(self.model, 'predict'):
            preds = self.model.predict(X)
        else:
            raise ValueError("Model has no transform"
                             " or predict method.")

        _, ny, nx = feats_x.shape
        nbands = int(preds.size / (ny * nx))
        preds = self._from_vec(preds,
                               (nbands, ny, nx))
        return preds
