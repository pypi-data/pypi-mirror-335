import enum

import numpy as np
import torch

WORLDCOVER_LABELS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
WORLDCOVER_COLORS_MATPLOTLIB = [
    "forestgreen",
    "orange",
    "yellow",
    "violet",
    "red",
    "silver",
    "gray",
    "steelblue",
    "mediumaquamarine",
    "mediumspringgreen",
    "papayawhip",
]


class WorldCoverLabelsColors(enum.Enum):
    NO_DATA = (0, "nodata", "Not sure", "No Data", np.array([0, 0, 0]))  # Black
    TREE = (
        10,
        "tree",
        "tree",
        "Trees covered area",
        np.array([0, 100, 0]) / 255,  # Green
    )
    SHRUB = (
        20,
        "shrub",
        "shrub",
        "Shrub cover area",
        np.array([255, 187, 34]) / 255,  # Orange
    )
    GRASS = (
        30,
        "grass",
        "grassland",
        "Grassland",
        np.array([255, 255, 76]) / 255,  # Yellow
    )
    CROP = (40, "crop", "crops", "Cropland", np.array([240, 150, 255]) / 255)  # Violet
    BUILT = (
        50,
        "built",
        "urban/built-up",
        "Built-up",
        np.array([250, 0, 0]) / 255,  # Red
    )
    BARE = (60, "bare", "bare", "Bare areas", np.array([180, 180, 180]) / 255)  # Silver
    SNOW_AND_ICE = (
        70,
        "snow",
        "snow and ice",
        "Snow and/or ice cover",
        np.array([240, 240, 240]) / 255,  # White
    )
    WATER = (
        80,
        "water",
        "water",
        "Permanent water",
        np.array([0, 100, 200]) / 255,  # Steel Blue
    )
    WETLAND = (
        90,
        "wetland",
        "wetland (herbaceous)",
        "Herbaceous wetland",
        np.array([0, 150, 160]) / 255,  # Medium Aquamarine
    )
    MANGROVES = (
        95,
        "mangroves",
        None,
        "Mangroves",
        np.array([0, 207, 117]) / 255,  # Medium Spring Green
    )
    LICHENS = (
        100,
        "lichens_mosses",
        "Lichen and moss",
        "Lichen and moss",
        np.array([250, 230, 160]) / 255,  # Papaya Whip
    )

    def __init__(self, val1, val2, val3, val4, val5):
        self.id = val1
        self.class_name = val2
        self.iiasa_name = val3
        self.esa_class_name = val4
        self.color = val5

    @classmethod
    def id_to_class_name_mapping(cls):
        return {item.id: item.class_name for item in cls}


def get_labels_encodings():
    return [
        {
            "id": lc.id,
            "color": lc.color,
            "iiasa_name": lc.iiasa_name,
            "name": lc.class_name,
            "esa_name": lc.esa_class_name,
        }
        for lc in WorldCoverLabelsColors
    ]


ENCODINGS = get_labels_encodings()
ENCODINGS_DICT = {e["id"]: e for e in ENCODINGS}
WORLDCOVER_COLORMAP = {
    e["id"]: (e["color"] * 255).astype(int).tolist() + [255] for e in ENCODINGS
}
LABEL_NAMES = {k: ENCODINGS_DICT[k]["name"] for k in ENCODINGS_DICT.keys()}


def label_to_rgb(lc_pred, colors_enum=None, moveaxis=False):
    colors_enum = WorldCoverLabelsColors if colors_enum is None else colors_enum

    colors = {lc.id: {"name": lc.class_name, "color": lc.color} for lc in colors_enum}

    rgb_pred = np.zeros(
        (
            3,
            lc_pred.shape[0],
            lc_pred.shape[1],
        )
    )

    for k, v in colors.items():
        for ch in range(3):
            im = rgb_pred[ch, :, :]
            im[lc_pred == k] = v["color"][ch]

    if moveaxis:
        rgb_pred = np.moveaxis(rgb_pred, 0, -1)

    return rgb_pred


def binarize_probs(proba, labels, axis=0, nodata_value=0):
    """
    Returns classification of probabilities array.
    For each pixel the maximum probability class is selected
    and the appropriate label value from `classes_labels` is
    used.
    """
    # if isinstance(labels[0], str):
    #     labels = get_label_code(labels)
    labels = np.array(labels)
    smooth_labels = np.argmax(proba, axis=axis)

    k = np.arange(labels.size)
    v = labels

    out = np.zeros_like(smooth_labels, dtype=np.int8)
    for key, val in zip(k, v):
        out[smooth_labels == key] = val

    return out


def get_labeled_image(batch, labs: list, rgb=True):
    # check whether the labels are passed as class names or as values
    img_masks = []
    for i in range(len(batch)):
        if rgb:
            lab_rgb = label_to_rgb(binarize_probs(batch[i], labs))
            img_masks.append(torch.tensor(lab_rgb))
        else:
            img_masks.append(torch.tensor(binarize_probs(batch[i], labs)).unsqueeze(0))

    img_masks = torch.stack(img_masks, dim=0)
    if not rgb:
        img_masks = torch.cat([img_masks] * 3, dim=1)

    return img_masks


def probs_to_rgb(probs, labs):
    return label_to_rgb(binarize_probs(probs, labs))


def batch_probs_to_rgb(batch, labs):
    was_tensor = False
    if isinstance(batch, torch.Tensor):
        was_tensor = True
        batch = batch.numpy()

    new_batch = np.array([probs_to_rgb(b, labs) for b in batch])

    if was_tensor:
        new_batch = torch.Tensor(new_batch)
    return new_batch
