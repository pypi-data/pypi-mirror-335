import getpass
import random
import socket
from pathlib import Path

import lightning as L
import numpy as np
import pandas as pd
import torch
import xarray as xr
from dotenv import load_dotenv
from loguru import logger
import datetime
from datetime import timedelta

from .transforms import EvoTransforms

torch.manual_seed(42)
np.random.seed(42)

HOSTNAME = socket.gethostname()

if HOSTNAME.startswith("sasds"):
    logger.info("Running on HPC...")
    wandb_env_path = f"/home/vito/{getpass.getuser()}/configs"
else:
    logger.info("Running on Terrascope...")
    wandb_env_path = f"/data/users/Public/{getpass.getuser()}/configs"

Path(wandb_env_path).mkdir(exist_ok=True, parents=True)
WANDB_FN = Path(wandb_env_path) / "wandb.env"
if WANDB_FN.exists():
    load_dotenv(WANDB_FN)
else:
    logger.warning(f"wandb.env not found in {wandb_env_path}")


class CloudsenDataset(L.LightningDataModule):
    """
    This is the dataset class for the Cloudsen12 dataset.

    Args:
        dataset (pd.DataFrame): metadata dataframe
        config (dict): configuration dictionary
        augmentation (bool): whether to apply augmentation

    Attributes:
        dataset (pd.DataFrame): metadata dataframe
        augmentation (bool): whether to apply augmentation
        config (dict): configuration dictionary
        input_bands (list): list of bands to use as input
        transforms_compose (torchvision.transforms.Compose): transforms
        labels (list): list of labels
        bands (list): list of bands
    """

    def __init__(
        self,
        dataset,
        config,
        augmentation=False,
    ):
        self.dataset = dataset
        self.augmentation = augmentation
        self.config = config

        self.input_bands = [
            b
            for b in config["bands_config"]["s2_bands"]
            if not b.startswith("label") and isinstance(b, str)
        ]

        self.labels = list(
            self.config["labels_config"][config["data_config"]["dataset"]].values()
        )

        self.transforms_compose = EvoTransforms(
            flip_augmentation=self.config["training_config"]["augmentations"][
                "flip_augmentation"
            ],
            rotate_augmentation=self.config["training_config"]["augmentations"][
                "rotate_augmentation"
            ],
        )

        self.bands = self.input_bands

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, index: int):
        """
        This function reads the data for a given index, applies the augmentation pipeline,
        and returns the features and target.

        We also return two boolean arrays:
        - one that indicates if a sample is 'high' quality or not
        - one that is True for all pixels in the target that are positive for the surface class

        Args:
            index (int): index of the sample

        Returns:
            np.array: features
            np.array: target
            bool: high quality
            np.array: surface positives
        """
        row = self.dataset.loc[index]
        # Load the bands for the given row into a data array
        darr = load_bands(row, self.config)

        # Determine the target band
        darr, y = self.get_target_array(darr, row)

        # Select the input bands and the target band
        X = darr.sel(band=self.input_bands)
        # Apply scaling to the data
        X = self.scaling(X, input_bands=self.input_bands)
        # Get the x_head tensor (scaled, jittered lat/lon and meteo data)
        x_head = self.get_x_head(X.shape, row)
        # Check for NaNs in the features and target
        X = np.nan_to_num(X, nan=0)
        y = np.nan_to_num(y, nan=-1)
        x_head = np.nan_to_num(x_head, nan=0)

        if self.augmentation:
            X, y, x_head = self.transforms_compose(X, y, x_head)
        else:
            if not isinstance(X, torch.Tensor):
                X = torch.tensor(X, dtype=torch.float32)
            if not isinstance(y, torch.Tensor):
                y = torch.tensor(y, dtype=torch.float32)
            if not isinstance(x_head, torch.Tensor):
                x_head = torch.tensor(x_head, dtype=torch.float32)

        return X, y, x_head

    def get_target_array(self, darr, row):
        label_type = row.label_type

        if label_type == "high":
            darr, target_array = preprocess_high_quality_labels(darr, self.config)
        elif label_type == "scribble":
            darr, target_array = preprocess_scribble_labels(darr, self.config)
        elif label_type == "nolabel":
            darr, target_array = preprocess_nolabel_labels(darr, self.config)
        else:
            raise ValueError(f"Invalid label type: {label_type}")

        return darr, target_array

    def get_x_head(self, shape_X, row):
        from evotrain.v2 import lat_lon_to_unit_sphere

        x_head_components = []

        if "latlon" in self.config["dl_model_config"]["bands_head"]:
            # handling lat/lon data
            lat, lon = row.lat, row.lon
            latlon_jitter = self.config["scaling_config"]["latlon_jitter"]
            lat += np.random.uniform(-latlon_jitter, latlon_jitter)
            lon += np.random.uniform(-latlon_jitter, latlon_jitter)

            xx, yy, zz = lat_lon_to_unit_sphere(lat, lon)

            xx = np.full((1, shape_X[1], shape_X[2]), xx)
            yy = np.full((1, shape_X[1], shape_X[2]), yy)
            zz = np.full((1, shape_X[1], shape_X[2]), zz)

            # Clip the values to the range [0, 1]
            xx = np.clip(xx, 0, 1)
            yy = np.clip(yy, 0, 1)
            zz = np.clip(zz, 0, 1)

            # Stack the xx, yy, zz arrays along a new dimension
            lat_lon = np.concatenate([xx, yy, zz], axis=0)
            x_head_components.append(lat_lon)

        if "meteo" in self.config["dl_model_config"]["bands_head"]:
            # handling meteo data
            meteo_vars = [
                row.meteo_value1 / 250,
                row.meteo_value2 / 250,
                row.meteo_value3 / 250,
                row.meteo_value4 / 250,
                row.meteo_value5 / 250,
                row.meteo_value6 / 250,
            ]
            meteo_arrays = [
                np.full((1, shape_X[1], shape_X[2]), meteo_value)
                for meteo_value in meteo_vars
            ]

            # Stack the meteo arrays along a new dimension
            meteo = np.concatenate(meteo_arrays, axis=0)
            # Add jitter to the meteo values
            meteo_jitter = self.config["scaling_config"]["meteo_jitter"]
            meteo += np.random.uniform(-meteo_jitter, meteo_jitter, meteo.shape)

            # Clip the values to the range [0, 1]
            meteo = np.clip(meteo, 0, 1)
            x_head_components.append(meteo)

        if "seasonal" in self.config["dl_model_config"]["bands_head"]:
            # Get seasonal features
            sin_cos = day_of_year_cyclic_feats(row.s2_date, doy_jitter=15)
            # Let's scale the sin_cos features to the range [0, 1]
            sin_cos = (sin_cos + 1) / 2
            x_head_components.append(sin_cos)

        x_head = np.concatenate(x_head_components, axis=0)

        return x_head

    def prepare_data(self):
        pass

    def setup(self, stage=None):
        data_config = self.config["data_config"]
        train_config = self.config["training_config"]

        # Get train and validation dataframes
        train_df, val_df, test_df = split_dataframes(config=self.config)
        logger.debug(
            f"Data) train_df:{train_df.shape[0]}, val_df:{val_df.shape[0]}, test_df:{test_df.shape[0]}"
        )

        if data_config["extra_other_samples"] > 0:
            # Add extra fmask labels to the training data
            train_df = sample_additional_training_data(
                train_df,
                self.config,
                other_samples=data_config["extra_other_samples"],
            )
            logger.debug(
                f"+Extra) train_df:{train_df.shape[0]}, val_df:{val_df.shape[0]}, test_df:{test_df.shape[0]}"
            )
            logger.info("Extra samples added to the training data: ✓")

            if train_config["debug"]:
                logger.info("⚠️ Debug mode: ON ⚠️")
                train_df = train_df.sample(n=2560, random_state=42).reset_index(
                    drop=True
                )
                val_df = val_df.sample(n=256, random_state=42).reset_index(drop=True)
            logger.debug(
                f"Final) train_df:{train_df.shape[0]}, val_df:{val_df.shape[0]}, test_df:{test_df.shape[0]}"
            )

        # Get dataframes for the train, validation, and test datasets
        self.train_df = train_df
        self.val_df = val_df
        self.test_df = test_df

        # Get datasets
        self.train_dataset, self.val_dataset, self.test_dataset = get_datasets(
            config=self.config, train_df=train_df, val_df=val_df, test_df=test_df
        )

        # Get dataloaders
        self.train_loader, self.val_loader, self.test_loader = get_dataloaders(
            config=self.config,
            train_dataset=self.train_dataset,
            val_dataset=self.val_dataset,
            test_dataset=self.test_dataset,
        )

    def train_dataloader(self):
        return self.train_loader

    def val_dataloader(self):
        return self.val_loader

    def test_dataloader(self):
        return self.test_loader

    def scaling(self, X, input_bands):
        """
        Apply scaling to the data. See apply_augmented_scaling for more details.
        """

        return apply_augmented_scaling(
            X, self.augmentation, self.config, self.input_bands
        )

    def get_class_counts(self, dataset):
        """
        Get the class counts for a given dataset.
        """
        counts = {label: 0 for label in self.labels}
        for i in range(len(dataset)):
            _, target, _ = dataset[i]
            for label in self.labels:
                counts[label] += target[label].sum().item()
        return counts


def preprocess_high_quality_labels(darr, config):
    target_array = darr.sel(band="label_cm1plus").values
    target_array = categorical_to_probability(target_array, classes=[0, 1, 2, 3])
    # Our target array is now probability layers for each class (from 0 to 1)
    if config["data_config"]["classify_snow"]:
        target_array = preprocess_class_probability_layers(
            darr, config, target_array, snow_source="scl"
        )

        return darr, target_array
    else:
        raise NotImplementedError(
            "high quality preprocessing not implemented for non-snow classification"
        )


def preprocess_scribble_labels(darr, config):
    # Using SCL for scribble because label_cm2plus has a weird mapping
    if config["data_config"]["classify_snow"]:
        target_array = get_scl_layer(darr, config)
        return darr, target_array
    else:
        raise NotImplementedError(
            "scribble preprocessing not implemented for non-snow classification"
        )


def preprocess_nolabel_labels(darr, config):
    target_array = darr.sel(band="label_cm2plus").values
    target_array = categorical_to_probability(target_array, classes=[0, 1, 2, 3])
    if config["data_config"]["classify_snow"]:
        target_array = preprocess_class_probability_layers(
            darr, config, target_array, snow_source="scl"
        )

        return darr, target_array
    else:
        raise NotImplementedError(
            "nolabel preprocessing not implemented for non-snow classification"
        )


def preprocess_class_probability_layers(darr, config, target_array, snow_source="scl"):
    # We have 4 classes: surface (0), clouds (1), thin clouds (2), shadows (3)
    # We want to have: surface (0), clouds (1), shadows (2), snow (3)
    target_array[0] += target_array[2] * 0.3  # 30% of thin clouds to surface
    target_array[1] += target_array[2] * 0.7  # 70% of thin clouds to clouds
    target_array[2] = target_array[3]  # shadows replaces thin clouds
    target_array[0] += target_array[2] * 0.1  # add 10% of shadows to surface
    target_array[2] -= target_array[2] * 0.1  # remove 10% from shadows
    target_array[3] = 0  # zero out the shadows to make space for snow

    # get the snow layer
    target_array_with_snow = get_snow_layer(darr, config, source=snow_source)
    target_array[3] = target_array_with_snow[3]  # snow to shadows place
    target_array[0] *= 1 - target_array_with_snow[3]  # replace surface with snow

    return target_array


def get_snow_layer(darr, config, source="scl"):
    if source == "fmask":
        raise NotImplementedError(
            "fmask preprocessing not implemented for snow classification"
        )
    elif source == "scl":
        return get_scl_layer(darr, config)
    else:
        raise ValueError(f"Unknown source: {source}")


def get_fmask_layer(darr, config):
    classify_snow = config["data_config"]["classify_snow"]
    if classify_snow:
        cloudsen12_mapping = config["labels_config"][
            "cloudsen12_mergedclouds_extrasnow"
        ]
        fmask_to_cloudsen12 = {
            0: cloudsen12_mapping["SURFACE"],  # fmask surface
            1: cloudsen12_mapping["SURFACE"],  # fmask water
            2: cloudsen12_mapping["SHADOWS"],  # fmask shadows
            3: cloudsen12_mapping["SNOW"],  # fmask snow
            4: cloudsen12_mapping["CLOUDS"],  # fmask clouds
        }

        label_array_mapped = np.vectorize(fmask_to_cloudsen12.get)(
            darr.sel(band="label_fmask").values
        )
        index_none = np.where(label_array_mapped == None)  # noqa
        label_array_mapped[index_none] = 0
        label_array_mapped = categorical_to_probability(
            label_array_mapped, classes=[0, 1, 2, 3]
        )

        return label_array_mapped
    else:
        raise NotImplementedError(
            "fmask preprocessing not implemented for non-snow classification"
        )


def get_scl_layer(darr, config):
    classify_snow = config["data_config"]["classify_snow"]
    if classify_snow:
        # NOTE: we use cloudsen12_extrasnow which contains thin clouds
        cloudsen12_mapping = config["labels_config"]["cloudsen12_extrasnow"]

        scl_to_cloudsen12 = {
            -1: -1,
            0: -1,  # scl no data
            1: -1,  # scl saturated/defective
            2: -1,  # scl dark area pixels
            3: cloudsen12_mapping["SHADOWS"],  # scl cloud shadows
            4: cloudsen12_mapping["SURFACE"],  # scl vegetation
            5: cloudsen12_mapping["SURFACE"],  # scl bare soils
            6: cloudsen12_mapping["SURFACE"],  # scl water
            7: -1,  # scl clouds-low-probability/Unclassified
            8: cloudsen12_mapping["CLOUDS"],  # scl clouds-medium-probability
            9: cloudsen12_mapping["CLOUDS"],  # scl clouds-high-probability
            10: cloudsen12_mapping["THIN_CLOUDS"],  # scl thin cirrus
            11: cloudsen12_mapping["SNOW"],  # scl snow
        }

        # Apply the mapping to the label_scl band
        label_array_mapped = np.vectorize(scl_to_cloudsen12.get)(
            darr.sel(band="label_sen2cor").values
        )

        # We now have classes surface (0), clouds (1), thin clouds (2), shadows (3), snow (4)
        label_array_mapped = categorical_to_probability(
            label_array_mapped, classes=[0, 1, 2, 3, 4]
        )

        # Like in preprocessing_high_quality_labels, we set 30% of thin clouds to surface and 70% to clouds
        label_array_mapped[0] += label_array_mapped[2] * 0.3
        label_array_mapped[1] += label_array_mapped[2] * 0.7
        # We set the thin clouds to shadows
        label_array_mapped[2] = label_array_mapped[3]
        # We set the shadows to snow
        label_array_mapped[3] = label_array_mapped[4]
        # We delete the last class (snow) because it's already in the shadows
        label_array_mapped = label_array_mapped[:-1]

        return label_array_mapped


def load_nc(path, bands, **kwargs):
    """
    Load a netcdf file and return a xarray DataArray with the specified bands.
    """
    try:
        with xr.open_dataarray(path, engine="netcdf4", **kwargs) as da:
            if bands is not None:
                try:
                    # logger.info(f"All available bands: {da.band.values}")
                    da = da.sel(band=bands)
                except Exception as e:
                    logger.error(f"Error: {e}")
                    logger.info(
                        f"Bands requested but not found: {set(bands) - set(da.band.values)}"
                    )
                    logger.info(f"Path: {path}")
            da = da.load()
            return da
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.error(f"Path: {path}")
        return None


def load_bands(row, config):
    """
    Load the bands for a given row and configuration.
    """

    path = Path(config["data_config"]["dataset_path"]) / row.path

    bands = config["bands_config"]["s2_bands"]

    for label_layer in config["data_config"]["label_layers"]:
        bands.append(label_layer)

    # Remove duplicates
    bands = list(set(bands))

    try:
        darr = load_nc(path, bands=bands)
        assert darr is not None, f"Data array is None for {row.s2_id_gee}, path: {path}"
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.error(f"Path: {path}")
        return None
    darr.attrs["epsg"] = row.proj_epsg

    return darr


def apply_augmented_scaling(darr, apply_jitter, config, input_bands):
    """
    Applies scaling to the Sentinel-2 bands, DEM, lat, lon, and meteo variables.
    """
    assert "band" in darr.dims, "band dimension not found in the data array"

    # Convert to float32
    darr = darr.astype(np.float32)

    # Scale the Sentinel-2 bands and apply logistic scaling.
    darr_s2 = _scale_sentinel2_bands(
        darr=darr,
        s2_bands=input_bands,
        s2_scaling=config["scaling_config"]["s2_scaling"],
        k_factor=config["scaling_config"]["k_factor"],
        apply_jitter=apply_jitter,
        k_factor_jitter=config["scaling_config"]["k_factor_jitter"],
    )

    # Scale the DEM band and apply logistic scaling.
    darr_dem = None

    # Concatenate the data arrays for Sentinel-2 bands, DEM, latitude, longitude, and meteo variables.
    darrs = [d for d in (darr_s2, darr_dem) if d is not None]

    # If there are more than one data arrays, concatenate them along the band dimension.
    if len(darrs) > 1:
        darr = xr.concat(darrs, dim="band")
    else:
        # Otherwise, just select the first data array.
        darr = darrs[0]

    return darr


def _scale_sentinel2_bands(
    darr=None,
    s2_bands=["l2a-B01", "l2a-B02", "l2a-B03"],
    s2_scaling=10_000,
    k_factor=5,
    apply_jitter=False,
    k_factor_jitter=2,
):
    """
    Scale the Sentinel-2 bands and apply logistic scaling.
    """

    # select the Sentinel-2 bands
    darr_s2 = darr.sel(band=s2_bands)
    # divide the Sentinel-2 bands by the scaling factor
    darr_s2 = darr_s2 / s2_scaling
    # apply logistic scaling to the Sentinel-2 bands if k_factor > 0
    if k_factor > 0:
        k_noised_signal = k_factor + _random_jitter(k_factor_jitter, apply_jitter)
        darr_s2 = logistic(darr_s2, k=k_noised_signal)
    return darr_s2


def _scale_dem_band(
    darr=None,
    dem_band=None,
    dem_scaling=4000,
    k_factor=5,
    apply_jitter=False,
    k_factor_jitter=2,
):
    """
    Scale the DEM band and apply logistic scaling.
    Upper limit for high altitudes is 4000.
    """
    # Check if the DEM band is present in the data array.
    dem_band = [dem_band] if dem_band in darr.band.values else None
    if dem_band is None:
        return None
    # select the DEM band
    darr_dem = darr.sel(band=dem_band)
    # divide the DEM band by the scaling factor
    darr_dem = darr_dem / dem_scaling
    # apply logistic scaling to the DEM band if k_factor > 0
    if k_factor > 0:
        k_noised_dem = k_factor + _random_jitter(k_factor_jitter, apply_jitter)
        darr_dem = logistic(darr_dem, k=k_noised_dem)
    return darr_dem


def logistic(x, L=1, k=3.60, x0=0, y0=-0.5, s=2):
    """
    Logistic function. It's used to scale the Sentinel-2 bands and DEM.
    """
    return (L / (1 + np.exp(-k * (x - x0))) + y0) * s


def random_jitter(n):
    """
    Add random jitter to a number.
    """
    return random.uniform(-n, n)


def _random_jitter(x, apply_jitter=True):
    """
    Applies random jitter to a value if jitter is enabled.
    """
    return random_jitter(x) if apply_jitter else 0


def categorical_to_probability(label, classes, cross_labels_mapping=None):
    """
    Transform a 2-D label array in a 3D target probs array
    """

    probs = np.zeros((len(classes), label.shape[0], label.shape[1]), dtype=np.float32)

    classes_idx = {ind: lab for ind, lab in enumerate(classes)}

    for ind, lab in classes_idx.items():
        probs[ind, :, :] = label == lab
        if cross_labels_mapping is not None:
            for cross_lab, cross_prob in cross_labels_mapping.get(lab, {}).items():  # noqa: E501
                cross_lab = int(cross_lab)  # it's a str from json config
                probs[classes_idx[cross_lab], :, :] = cross_prob
    return probs


def buffer_and_blur(image, buffer_size=2, sigma=0.5, add_noise=False):
    """
    Buffers a binary image and then applies a Gaussian blur to it.
    """
    from scipy.ndimage import gaussian_filter
    from skimage.morphology import binary_dilation, disk

    # Buffer the image with a disk of radius buffer_size
    buffered_layer = binary_dilation(image, disk(buffer_size))
    # Apply a Gaussian blur to the buffered layer
    blurred_layer = gaussian_filter(
        buffered_layer.astype(np.float32), sigma=sigma, truncate=3.0
    )

    if add_noise:
        # Add noise only to the newly created edges (i.e. the buffered area)
        edge = buffered_layer - image
        noise = np.random.normal(0, 0.025, size=edge.shape)  # 2.5% noise
        edge += noise
        edge = np.clip(edge, 0, 1)
        blurred_layer = image + edge

    return blurred_layer


def read_metadata(metadata_file=None, config=None):
    """
    Read the metadata file.
    """
    metadata_file = Path(config["data_config"]["metadata_path"])

    if config["data_config"]["dataset"] == "cloudsen12":
        dataset_metadata = pd.read_parquet(metadata_file)
    elif config["data_config"]["dataset"] == "cloudsen12plus":
        dataset_metadata = pd.read_parquet(metadata_file)
        dataset_metadata = preprocess_metadata(dataset_metadata, config)
    else:
        raise ValueError(f"Invalid dataset: {config['data_config']['dataset']}")
    return dataset_metadata


def preprocess_metadata(df, config):
    tmp_s2_id_gee = (
        df["s2_id_gee"].str.split("_").str[1]
        + "_"
        + df["s2_id_gee"].str.split("_").str[2]
    )
    df["path"] = (
        config["data_config"]["dataset_path"]
        + "/"
        + df["roi_id"]
        + "/cloudsen12_"
        + df["roi_id"]
        + "_"
        + tmp_s2_id_gee
        + f"_{config['data_config']['resolution']}m.nc"
    )

    # Let's see how many files exist
    df["file_exists"] = df["path"].apply(lambda x: Path(x).exists())
    logger.info(f"Checking files: {df['file_exists'].sum()}/{len(df)} files exist")

    # Filter out the files that do not exist
    df = df[df["file_exists"]]

    # Check if 'label_cm2plus' exists in the dataframe
    if "label_cm2plus" in df.columns:
        df = df[df["label_cm2plus"]]
    if "label_cm1plus" in df.columns:
        df = df[df["label_cm1plus"]]
    if "verified" in df.columns:
        logger.info(
            f"Filtering out unverified samples: {len(df) - df['verified'].sum()}/{len(df)} samples"
        )
        df = df[df["verified"]]

    return df


def get_train_test_val_dfs_random(
    train_test_frac=0.99, train_val_frac=0.9, config=None
):
    """
    Get the train, test, and validation dataframes (random splitting).
    """

    dataset_metadata = read_metadata(config=config)

    # load the dataset
    dataset_metadata = dataset_metadata[dataset_metadata["label_type"] == "high"]

    np.random.seed(128)
    test_idx = np.random.rand(10_000) > train_test_frac
    dataset_metadata["test"] = test_idx

    # train/val/test split
    train_val_db = dataset_metadata[dataset_metadata["test"] == 0]
    train_val_db.reset_index(drop=True, inplace=True)

    # train dataset
    train_db = train_val_db.sample(frac=train_val_frac, random_state=42)
    train_db.reset_index(drop=True, inplace=True)

    # val dataset
    val_db = train_val_db.drop(train_db.index)
    val_db.reset_index(drop=True, inplace=True)

    # test dataset
    test_db = dataset_metadata[dataset_metadata["test"] == 1]
    test_db.reset_index(drop=True, inplace=True)

    return train_db, val_db, test_db


def get_train_test_val_dfs_roi_based(
    train_test_frac=0.99, train_val_frac=0.9, label_types=["high"], config=None
):
    """
    Get the train, test, and validation dataframes based on roi_id.
    """

    # load the metadata
    dataset_metadata = read_metadata(config=config)

    # load the dataset
    dataset_metadata = dataset_metadata[
        dataset_metadata["label_type"].isin(label_types)
    ]

    # get a list of all roi_id
    roi_ids = dataset_metadata.roi_id.unique().tolist()
    random.seed(42)
    # shuffle the roi_ids
    random.shuffle(roi_ids)
    # split the roi_ids into train and test
    train_rois, test_rois = np.split(roi_ids, [int(train_test_frac * len(roi_ids))])
    # split the train rois into train and validation
    train_rois, val_rois = np.split(train_rois, [int(train_val_frac * len(train_rois))])

    # get the train, validation, and test dataframes
    train_db = dataset_metadata[dataset_metadata.roi_id.isin(train_rois)]
    train_db.reset_index(drop=True, inplace=True)
    val_db = dataset_metadata[dataset_metadata.roi_id.isin(val_rois)]
    val_db.reset_index(drop=True, inplace=True)
    test_db = dataset_metadata[dataset_metadata.roi_id.isin(test_rois)]
    test_db.reset_index(drop=True, inplace=True)

    return train_db, val_db, test_db


def add_uniq_key(df):
    """
    Add a unique key to the dataframe. This helps merge the dataframes from different sources.
    """
    assert "roi_id" in df.columns, "roi_id not found in the dataframe"
    assert "s2_id_gee" in df.columns, "s2_id_gee not found in the dataframe"
    assert "s2_date" in df.columns, "s2_date not found in the dataframe"

    df["uniq_key"] = df["roi_id"] + "_" + df["s2_id_gee"] + "_" + df["s2_date"]
    return df


def get_train_test_val_dfs_cloudsen12(config):
    """
    Get the train, validation, and test dataframes based on the original Cloudsen12 dataset splits.
    """

    dataset_metadata = read_metadata(config=config)

    # load the dataset
    dataset_metadata = dataset_metadata[dataset_metadata["label_type"] == "high"]

    if config["data_config"]["dataset"] == "cloudsen12":
        train_df = pd.read_parquet(
            Path(config["data_config"]["metadata_path"]).parent
            / "cloudsen12_train.parquet"
        )
        val_df = pd.read_parquet(
            Path(config["data_config"]["metadata_path"]).parent
            / "cloudsen12_val.parquet"
        )
        test_df = pd.read_parquet(
            Path(config["data_config"]["metadata_path"]).parent
            / "cloudsen12_test.parquet"
        )
        dataset_metadata = add_uniq_key(dataset_metadata)
        train_df = add_uniq_key(train_df)
        val_df = add_uniq_key(val_df)
        test_df = add_uniq_key(test_df)

        train_df = train_df.merge(
            dataset_metadata[["uniq_key", "path"]], on="uniq_key", how="left"
        )
        val_df = val_df.merge(
            dataset_metadata[["uniq_key", "path"]], on="uniq_key", how="left"
        )
        test_df = test_df.merge(
            dataset_metadata[["uniq_key", "path"]], on="uniq_key", how="left"
        )
    elif config["data_config"]["dataset"] == "cloudsen12plus":
        train_df = dataset_metadata[dataset_metadata["split"] == "train"].reset_index(
            drop=True
        )
        val_df = dataset_metadata[dataset_metadata["split"] == "val"].reset_index(
            drop=True
        )
        test_df = dataset_metadata[dataset_metadata["split"] == "test"].reset_index(
            drop=True
        )

    return train_df, val_df, test_df


def split_dataframes(config: dict = None):
    """
    Split the dataframes based on the specified method.
    """
    how = config["data_config"]["splitting_method"]

    if how == "cloudsen12":
        train_df, val_df, test_df = get_train_test_val_dfs_cloudsen12(config)
    elif how == "cloudsen12plus":
        raise NotImplementedError(f"{how} split is using same split as cloudsen12")
    else:
        raise ValueError(f"Unknown split method {how}")

    return train_df, val_df, test_df


def sample_additional_training_data(train_df, config, other_samples=0):
    """
    Add some training data to the training dataframe by sampling
    a given number of datapoints from the "nolabel" and "scribble"
    label types in dataset_metadata.
    """
    if other_samples > 0:
        logger.debug(
            f"Adding {other_samples} extra samples from nolabel and scribble label types"
        )

    # load the metadata file
    dataset_metadata = read_metadata(config=config)

    # select the "nolabel" and "scribble" label types from the metadata (or not "high" label types)
    # there's no data leakage here because we always use "high" label type for training/validation/testing
    extra_df = dataset_metadata[~dataset_metadata.label_type.isin(["high"])]

    # for 'other' samples we randomly sample from the 'nolabel' and 'scribble' label types
    if other_samples > 0:
        total_available_other_samples = len(extra_df)
        assert total_available_other_samples >= other_samples, (
            f"total_available_other_samples ({total_available_other_samples}) < other_samples ({other_samples})"
        )
        other_df = extra_df.sample(other_samples)
    else:
        other_df = pd.DataFrame()

    # concatenate all the dataframes
    train_df = pd.concat([train_df, other_df], ignore_index=True)
    # shuffle the train_df
    train_df = train_df.sample(frac=1).reset_index(drop=True)
    return train_df


def get_datasets(
    config: dict = None,
    train_df: pd.DataFrame = None,
    val_df: pd.DataFrame = None,
    test_df: pd.DataFrame = None,
):
    """
    Get the datasets for training, validation, and testing.
    """
    assert config is not None, "config is required"
    assert len(train_df) > 0 and len(val_df) > 0, "train_df or val_df is empty"

    augment = config["training_config"]["enable_augmentations"]

    if config["data_config"]["train_samples_into_val"] > 0:
        n_samples = config["data_config"]["train_samples_into_val"]

        # Check if n_samples is divisible by 5
        if n_samples % 5 != 0:
            raise ValueError(
                "train_samples_into_val must be divisible by 5 (5 samples per roi)"
            )

        # We should get n_samples by selecting rois (each has 5 samples) randomly
        # We will select n_samples // 5 rois randomly
        rois = train_df.roi_id.unique()
        rois = np.random.choice(rois, n_samples // 5, replace=False)
        # Select the samples from the rois
        val_df = pd.concat([val_df, train_df[train_df.roi_id.isin(rois)]])
        train_df = train_df[~train_df.roi_id.isin(rois)]
        val_df.reset_index(drop=True, inplace=True)
        train_df.reset_index(drop=True, inplace=True)
        logger.info(f"Added {n_samples} samples from train to val based on rois")

        # Check for overlap between val_df and train_df using the .path column
        overlap = set(val_df["path"]).intersection(set(train_df["path"]))
        assert len(overlap) == 0, "Overlap found between val_df and train_df"
        logger.info("No overlap found between val_df and train_df")

        train_dataset = CloudsenDataset(
            train_df,
            config,
            augmentation=augment["train"],
        )
    else:
        train_dataset = CloudsenDataset(
            train_df,
            config,
            augmentation=augment["train"],
        )

    if config["data_config"]["merge_test_into_val"]:
        val_df = pd.concat([val_df, test_df], ignore_index=True)
        val_df.reset_index(drop=True, inplace=True)
        del test_df

        val_dataset = CloudsenDataset(
            val_df,
            config,
            augmentation=augment["val"],
        )
        logger.info("Merged test dataset into validation dataset 🚨")

        return train_dataset, val_dataset, None

    else:
        val_dataset = CloudsenDataset(
            val_df,
            config,
            augmentation=augment["val"],
        )

        test_dataset = CloudsenDataset(
            test_df,
            config,
            augmentation=augment["test"],
        )

        return train_dataset, val_dataset, test_dataset


def get_dataloaders(
    config: dict = None,
    train_dataset: CloudsenDataset = None,
    val_dataset: CloudsenDataset = None,
    test_dataset: CloudsenDataset = None,
):
    """
    Get the dataloaders for training, validation, and testing.
    """
    assert config is not None, "config is required"
    assert len(train_dataset) > 0, "train_dataset is empty"
    assert len(val_dataset) > 0, "val_dataset is empty"
    if config["data_config"]["merge_test_into_val"]:
        assert test_dataset is None, "test_dataset should be None"
    else:
        assert len(test_dataset) > 0, "test_dataset is empty"

    dataloaders_config = config["dataloaders_config"]

    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=dataloaders_config["train"]["batch_size"],
        num_workers=dataloaders_config["train"]["num_workers"],
        shuffle=dataloaders_config["train"]["shuffle"],
        pin_memory=dataloaders_config["train"]["pin_memory"],
        # prefetch_factor=2,
    )

    if config["data_config"]["merge_test_into_val"]:
        val_loader = torch.utils.data.DataLoader(
            val_dataset,
            batch_size=dataloaders_config["val"]["batch_size"],
            num_workers=dataloaders_config["val"]["num_workers"],
            shuffle=dataloaders_config["val"]["shuffle"],
            pin_memory=dataloaders_config["val"]["pin_memory"],
        )
        return train_loader, val_loader, None
    else:
        val_loader = torch.utils.data.DataLoader(
            val_dataset,
            batch_size=dataloaders_config["val"]["batch_size"],
            num_workers=dataloaders_config["val"]["num_workers"],
            shuffle=dataloaders_config["val"]["shuffle"],
            pin_memory=dataloaders_config["val"]["pin_memory"],
        )
        test_loader = torch.utils.data.DataLoader(
            test_dataset,
            batch_size=dataloaders_config["test"]["batch_size"],
            num_workers=dataloaders_config["test"]["num_workers"],
            shuffle=dataloaders_config["test"]["shuffle"],
            pin_memory=dataloaders_config["test"]["pin_memory"],
        )

        return train_loader, val_loader, test_loader


def day_of_year(date):
    start_of_year = datetime.datetime(date.year, 1, 1)
    return (date - start_of_year).days + 1


def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def day_of_year_cyclic_feats(date_str, doy_jitter=15, height=96, width=96):
    # Parse the date
    date_obj = datetime.datetime.strptime(date_str[:10], "%Y-%m-%d")

    # Apply jitter to the date
    jittered_dates = [
        date_obj + timedelta(days=random_jitter(doy_jitter))
        for _ in range(height * width)
    ]

    # Calculate the day of the year (1-365 or 366 for leap years)
    day_of_year = (
        np.array(
            [jittered_date.timetuple().tm_yday for jittered_date in jittered_dates]
        )
        .reshape(height, width)
        .astype(np.float32)
    )

    # Total number of days in the year
    total_days = 366 if is_leap_year(date_obj.year) else 365

    # Encode as sine and cosine using numpy
    day_of_year_sin = np.sin(2 * np.pi * day_of_year / total_days)
    day_of_year_cos = np.cos(2 * np.pi * day_of_year / total_days)

    return np.array([day_of_year_sin, day_of_year_cos])
