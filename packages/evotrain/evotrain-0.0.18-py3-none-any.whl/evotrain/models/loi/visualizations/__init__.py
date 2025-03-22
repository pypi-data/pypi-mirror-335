import matplotlib.pyplot as plt
import numpy as np
from loguru import logger

scl_mapping = {
    "NA": 0,
    "SATURATED_DEFECTIVE": 1,
    "DARK_FEATURES_SHADOWS": 2,
    "CLOUD_SHADOWS": 3,
    "VEGETATION": 4,
    "NOT_VEGETATED": 5,
    "WATER": 6,
    "UNCLASSIFIED": 7,
    "CLOUDS_MEDIUM_PROB": 8,
    "CLOUDS_HIGH_PROB": 9,
    "THIN_CIRRUS": 10,
    "SNOW_ICE": 11,
}

colors = dict(
    # Cloudsen12 colors
    SURFACE=[0, 255, 0],  # green
    CLOUDS=[255, 255, 255],  # white
    THIN_CLOUDS=[0, 255, 255],  # cyan
    SHADOWS=[105, 105, 105],  # darker gray
    SNOW=[255, 0, 255],  # magenta
    # Sentinel-2 L2A SCL colors
    NA=[0, 0, 0],  # black
    SATURATED_DEFECTIVE=[255, 0, 0],  # red
    DARK_FEATURES_SHADOWS=[205, 205, 205],  # gray
    CLOUD_SHADOWS=[105, 105, 105],  # darker gray
    VEGETATION=[0, 255, 0],  # green
    NOT_VEGETATED=[255, 255, 0],  # yellow
    WATER=[0, 0, 255],  # blue
    UNCLASSIFIED=[0, 0, 0],  # black
    CLOUDS_MEDIUM_PROB=[192, 192, 192],  # light gray
    CLOUDS_HIGH_PROB=[255, 255, 255],  # white
    THIN_CIRRUS=[0, 255, 255],  # cyan
    SNOW_ICE=[255, 0, 255],  # magenta
)
colors_scl_minimal = dict(
    # Sentinel-2 L2A SCL colors (ignoring some classes)
    NA=[0, 0, 0],  # black
    SATURATED_DEFECTIVE=[0, 0, 0],  # red
    DARK_FEATURES_SHADOWS=[0, 255, 0],  # green
    CLOUD_SHADOWS=[105, 105, 105],  # darker gray
    VEGETATION=[0, 255, 0],  # green
    NOT_VEGETATED=[0, 255, 0],  # green
    WATER=[0, 255, 0],  # blue
    UNCLASSIFIED=[0, 0, 0],  # black
    CLOUDS_MEDIUM_PROB=[255, 255, 255],  # light gray
    CLOUDS_HIGH_PROB=[255, 255, 255],  # white
    THIN_CIRRUS=[0, 255, 255],  # cyan
    SNOW_ICE=[255, 0, 255],  # magenta
)
colors_scl_minimal_mergedclouds_snow = dict(
    # Sentinel-2 L2A SCL colors (ignoring some classes)
    NA=[0, 0, 0],  # black
    SATURATED_DEFECTIVE=[0, 0, 0],  # red
    DARK_FEATURES_SHADOWS=[0, 255, 0],  # green
    CLOUD_SHADOWS=[105, 105, 105],  # darker gray
    VEGETATION=[0, 255, 0],  # green
    NOT_VEGETATED=[0, 255, 0],  # green
    WATER=[0, 255, 0],  # blue
    UNCLASSIFIED=[0, 0, 0],  # black
    CLOUDS_MEDIUM_PROB=[255, 255, 255],  # white
    CLOUDS_HIGH_PROB=[255, 255, 255],  # white
    THIN_CIRRUS=[255, 255, 255],  # white
    SNOW_ICE=[255, 0, 255],  # magenta
)
colors_scl_original = dict(
    # Sentinel-2 L2A SCL colors
    NA=[0, 0, 0],  # black
    SATURATED_DEFECTIVE=[255, 0, 0],  # red
    DARK_FEATURES_SHADOWS=[47, 47, 47],  # dark gray
    CLOUD_SHADOWS=[100, 50, 0],  # brown
    VEGETATION=[0, 160, 0],  # green
    NOT_VEGETATED=[255, 230, 90],  # yellow-orange
    WATER=[0, 0, 255],  # blue
    UNCLASSIFIED=[128, 128, 128],  # gray
    CLOUDS_MEDIUM_PROB=[192, 192, 192],  # medium gray
    CLOUDS_HIGH_PROB=[255, 255, 255],  # white
    THIN_CIRRUS=[100, 200, 255],  # light blue
    SNOW_ICE=[255, 150, 255],  # pastel magenta
)

# Define the colors for saving geotiff and plotting
cloudsen12_colors_rgb = {
    0: np.array(colors["SURFACE"]),
    1: np.array(colors["CLOUDS"]),
    2: np.array(colors["THIN_CLOUDS"]),
    3: np.array(colors["SHADOWS"]),
}

cloudsen12_colors_mergedclouds_snow_rgb = {
    0: np.array(colors["SURFACE"]),
    1: np.array(colors["CLOUDS"]),
    2: np.array(colors["SHADOWS"]),
    3: np.array(colors["SNOW"]),
}

# Mapping from the model output classes to the SCL ones
scl_like_mapping = {
    0: 4,  # Surface
    1: 8,  # Clouds
    2: 10,  # Thin clouds
    3: 3,  # Shadows
}

cloudsen12_like_mapping = {
    0: 0,  # Surface (NA)
    1: 0,  # Surface (SATURATED_DEFECTIVE)
    2: 0,  # Surface (DARK_FEATURES_SHADOWS)
    3: 3,  # Shadows (CLOUD_SHADOWS)
    4: 0,  # Surface (VEGETATION)
    5: 0,  # Surface (NOT_VEGETATED)
    6: 0,  # Surface (WATER)
    7: 0,  # Surface (UNCLASSIFIED)
    8: 1,  # Clouds (CLOUDS_MEDIUM_PROB)
    9: 1,  # Clouds (CLOUDS_HIGH_PROB)
    10: 2,  # Thin clouds (THIN_CIRRUS)
    11: 0,  # Surface (SNOW_ICE)
    -1: -1,  # Ignore
}



def np_hist(a, exclude_zeros=False, exclude_ones=False):
    """
    Plot a histogram of the array values.

    Parameters
    ----------
    a : np.ndarray
        Input array.
    exclude_zeros : bool, optional
        If True, exclude zeros from the histogram.
    exclude_ones : bool, optional
        If True, exclude ones from the histogram.
    """
    if exclude_zeros:
        a = a[a != 0.0]
    if exclude_ones:
        a = a[a != 1.0]
    _bins, _edges = np.histogram(a, np.arange(np.min(a), np.max(a), 0.0001))
    plt.plot(_edges[:-1], _bins)
    plt.xlabel("Probability")
    plt.ylabel("Count")


def np_hist_all_channels(a, titles=[], exclude_zeros=False, exclude_ones=False):
    """
    Plot histograms for all channels of the array.

    Parameters
    ----------
    a : np.ndarray
        Input array with multiple channels.
    titles : list of str, optional
        Titles for each subplot.
    exclude_zeros : bool, optional
        If True, exclude zeros from the histograms.
    exclude_ones : bool, optional
        If True, exclude ones from the histograms.
    """
    plt.figure(figsize=(25, 5))
    plt.subplot(1, 4, 1)
    np_hist(a[0].flatten(), exclude_zeros=exclude_zeros, exclude_ones=exclude_ones)
    plt.title(titles[0])
    plt.subplot(1, 4, 2)
    np_hist(a[1].flatten(), exclude_zeros=exclude_zeros, exclude_ones=exclude_ones)
    plt.title(titles[1])
    plt.subplot(1, 4, 3)
    np_hist(a[2].flatten(), exclude_zeros=exclude_zeros, exclude_ones=exclude_ones)
    plt.title(titles[2])
    plt.subplot(1, 4, 4)
    np_hist(a[3].flatten(), exclude_zeros=exclude_zeros, exclude_ones=exclude_ones)
    plt.title(titles[3])


def mask_to_rgb(mask, colors, normalize_colors=True):
    """
    Convert mask to RGB using the given colors (class labels to colors mapping).

    Parameters
    ----------
    mask : np.ndarray
        Mask to convert.
    colors : dict
        Dictionary containing the colors for each class.
    normalize_colors : bool, optional
        Normalize the colors i.e. divide by 255.

    Returns
    -------
    np.ndarray
        RGB mask.
    """
    if normalize_colors:
        colors = {k: np.array(v) / 255 for k, v in colors.items()}
    mask_rgb = np.zeros((mask.shape[0], mask.shape[1], 3))
    for i, color in colors.items():
        mask_rgb[mask == i] = color
    return mask_rgb


def model_validity_map(out_argmax, surface):
    """
    Create a validity map for the model predictions.

    Parameters
    ----------
    out_argmax : np.ndarray
        Model output array.
    surface : np.ndarray
        Surface array.

    Returns
    -------
    np.ndarray
        Validity map.
    """
    assert (
        out_argmax.shape == surface.shape
    ), f"Got shapes out_argmax:{out_argmax.shape} and surface:{surface.shape}"
    model_valid = np.zeros_like(surface)
    model_valid[out_argmax == 0] = 1
    model_valid[out_argmax == 1] = 0
    return model_valid


def scl_validity_map(scl):
    """
    Create a validity map for the SCL.

    Parameters
    ----------
    scl : np.ndarray
        SCL array.

    Returns
    -------
    np.ndarray
        Validity map.
    """
    scl_valid = np.zeros_like(scl)
    scl_valid[scl == 4] = 1
    scl_valid[scl == 5] = 1
    scl_valid[scl == 6] = 1
    scl_valid[(scl != 4) & (scl != 5) & (scl != 6)] = 0
    return scl_valid


def make_difference_img(
    model_valid,
    scl_valid,
    both_valid=[0, 255, 0],
    both_invalid=[128, 128, 128],
    model_invalid=[255, 0, 0],
    scl_invalid=[0, 0, 255],
):
    """
    Create an image where the pixels are colored according to the validity of the model and SCL.

    Parameters
    ----------
    model_valid : np.ndarray
        Model validity map.
    scl_valid : np.ndarray
        SCL validity map.
    both_valid : list of int, optional
        Color for both valid pixels.
    both_invalid : list of int, optional
        Color for both invalid pixels.
    model_invalid : list of int, optional
        Color for model invalid pixels.
    scl_invalid : list of int, optional
        Color for SCL invalid pixels.

    Returns
    -------
    np.ndarray
        Difference image.
    """
    diff_img = np.zeros((model_valid.shape[0], model_valid.shape[1], 3))
    diff_img[(model_valid == 1) & (scl_valid == 1)] = (
        np.array(both_valid) / 255
    )  # green for valid pixels
    diff_img[(model_valid == 0) & (scl_valid == 0)] = (
        np.array(both_invalid) / 255
    )  # gray for invalid pixels
    diff_img[(model_valid == 1) & (scl_valid == 0)] = (
        np.array(model_invalid) / 255
    )  # red for SCL invalid pixels
    diff_img[(model_valid == 0) & (scl_valid == 1)] = (
        np.array(scl_invalid) / 255
    )  # blue for model invalid pixels
    return diff_img

class PlotConfig:
    """
    Configuration object for plotting images.

    Attributes
    ----------
    s2_product_id : str 
        Identifier for the product being plotted.
    gridarr_{i}{j} : np.ndarray
        Image arrays to be plotted in the grid.
    save_dir : pathlib.Path
        Base directory where the plots will be saved.
    model_config : dict
        Dictionary containing model configuration, including meta_config.
    model_index : int
        Index of the model being used.
    titles : dict
        Dictionary mapping (i, j) tuples to titles for each subplot.
    cmaps : dict
        Dictionary mapping (i, j) tuples to colormaps for each subplot.
    """
    def __init__(
        self,
        s2_product_id,
        gridarr_00,
        gridarr_01,
        gridarr_02,
        gridarr_10,
        gridarr_11,
        gridarr_12,
        gridarr_20,
        gridarr_21,
        gridarr_22,
        save_dir,
        model_config,
        model_index,
        titles,
        cmaps,
    ):
        self.s2_product_id = s2_product_id
        self.gridarr_00 = gridarr_00
        self.gridarr_01 = gridarr_01
        self.gridarr_02 = gridarr_02
        self.gridarr_10 = gridarr_10
        self.gridarr_11 = gridarr_11
        self.gridarr_12 = gridarr_12
        self.gridarr_20 = gridarr_20
        self.gridarr_21 = gridarr_21
        self.gridarr_22 = gridarr_22
        self.save_dir = save_dir
        self.model_config = model_config
        self.model_index = model_index
        self.titles = titles
        self.cmaps = cmaps

def plot_images(config: PlotConfig):
    """
    Plots a grid of images and saves the plot to specified directories.

    Parameters
    ----------
    config : PlotConfig
        Configuration object containing the following attributes:
        - titles : dict
            Dictionary mapping (i, j) tuples to titles for each subplot.
        - gridarr_{i}{j} : np.ndarray
            Image arrays to be plotted in the grid.
        - save_dir : pathlib.Path
            Base directory where the plots will be saved.
        - s2_product_id : str
            Identifier for the product being plotted.
        - model_config : dict
            Dictionary containing model configuration, including meta_config.
        - model_index : int
            Index of the model being used.

    Raises
    ------
    KeyError
        If the model configuration does not contain the expected keys.

    Notes
    -----
    The function creates a 3x3 grid of images, sets titles for each subplot,
    and saves the resulting plot in two directories: one for products and one
    for models. The directories are created if they do not exist.
    """
    fig, axes = plt.subplots(3, 3, figsize=(10, 10))
    for (i, j), title in config.titles.items():
        axes[i, j].imshow(getattr(config, f'gridarr_{i}{j}'), cmap=config.cmaps[(i, j)])
        axes[i, j].set_title(title)
        axes[i, j].axis("off")

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.001, hspace=0.1)

    save_dir_products = config.save_dir / "products" / config.s2_product_id
    save_dir_products.mkdir(exist_ok=True, parents=True)

    try:
        pt_model_name = config.model_config["meta_config"]["pt_model_name"]
    except KeyError:
        logger.warning("Using older config format")
        pt_model_name = config.model_config["meta_config"]["model_name"]
    model_index = config.model_index

    save_fname_products = save_dir_products / f"{pt_model_name}.png"
    save_dir_models = (
        config.save_dir / "models" / pt_model_name / f"index_{model_index}"
    )

    save_dir_models.mkdir(exist_ok=True, parents=True)
    save_fname_models = save_dir_models / f"{config.s2_product_id}.png"

    plt.savefig(save_fname_products, bbox_inches="tight", pad_inches=0)
    plt.savefig(save_fname_models, bbox_inches="tight", pad_inches=0)

    logger.info(f"Saved the plot to: \n{save_fname_products}\n{save_fname_models}\n")
