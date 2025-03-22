import enum

import numpy as np
import torch

LSC_COVER_LABELS = [1, 2, 3, 4, 5]
LSC_OCCLUSION_LABELS = [1, 2, 3, 4]
LSC_ECOSYSTEM_LABELS = [1, 2, 3, 4, 5, 6]

# LSC_COVER_COLORS_MATPLOTLIB = [
#     "forestgreen",
#     "orange",
#     "yellow",
#     "violet",
#     "red",
#     "silver",
#     "gray",
#     "steelblue",
#     "mediumaquamarine",
#     "mediumspringgreen",
#     "papayawhip",
# ]

# land cover / physical surface cover classes
# - 0: tree
# - 1: shrub
# - 2: herbaceous vegetation
# - 3: not vegetated
# - 4: water

class LSCCoverLabelsColors(enum.Enum):
    TREE = (
        1,
        "tree",
        "tree",
        "Trees covered area",
        np.array([0, 100, 0]) / 255,
    )
    SHRUB = (
        2,
        "shrub",
        "shrub",
        "Shrub cover area",
        np.array([255, 187, 34]) / 255,
    )
    HERBACEOUS = (
        3,
        "herbaceous",
        "herbaceous",
        "Herbaceous",
        np.array([255, 255, 76]) / 255,
    )
    NOT_VEGETATED = (
        4,
        "not vegetated",
        "not vegetated",
        "Not vegetated",
        np.array([180, 180, 180]) / 255)
    WATER = (
        5,
        "water",
        "water",
        "Permanent water",
        np.array([0, 100, 200]) / 255,
    )
    NO_DATA = (0, "nodata", "Not sure", "No Data", np.array([0, 0, 0]))
    
    def __init__(self, val1, val2, val3, val4, val5):
        self.id = val1
        self.class_name = val2
        self.iiasa_name = val3
        self.esa_class_name = val4
        self.color = val5
# surface occlusion
# - 0: snow
# - 1: thick clouds / thin clouds
# - 2: shadow
# - 3: surface
class LSCOcclusionLabelsColors(enum.Enum):
    SNOW_AND_ICE = (
        1,
        "snow",
        "snow and ice",
        "Snow and/or ice cover",
        np.array([240, 240, 240]) / 255,
    )
    CLOUDS = (
        2,
        "clouds",
        "clouds",
        "Clouds",
        np.array([240, 20, 200]) / 255)
    SHADOW = (
        3,
        "shadow",
        "shadow",
        "Shadow",
        np.array([220, 150, 250]) / 255,
    )
    SURFACE = (
        4,
        "surface",
        "surface",
        "Surface",
        np.array([70, 150, 100]) / 255,
    )
    NO_DATA = (0, "nodata", "Not sure", "No Data", np.array([0, 0, 0]))
    
    def __init__(self, val1, val2, val3, val4, val5):
        self.id = val1
        self.class_name = val2
        self.iiasa_name = val3
        self.esa_class_name = val4
        self.color = val5


# ecosystems
# - 0: cropland
# - 1: mangrove
# - 2: built-up
# - 3: herbaceous wetland
# - 4: lichens
# - 5: other/natural



class LSCEcosystemLabelsColors(enum.Enum):
    
    CROP = (1, "crop", "crops", "Cropland", np.array([240, 150, 255]) / 255)
    MANGROVES = (
        2,
        "mangroves",
        None,
        "Mangroves",
        np.array([0, 207, 117]) / 255,
    )
    BUILT = (
        3,
        "built",
        "urban/built-up",
        "Built-up",
        np.array([250, 0, 0]) / 255,
    )
    
    WETLAND = (
        4,
        "wetland",
        "wetland (herbaceous)",
        "Herbaceous wetland",
        np.array([0, 150, 160]) / 255,
    )
    LICHENS = (
        5,
        "lichens_mosses",
        "Lichen and moss",
        "Lichen and moss",
        np.array([250, 230, 160]) / 255,
    )
    OTHER = (
        6,
        "other",
        "other",
        "Other",
        np.array([0, 150, 0]) / 255,
    )

    NO_DATA = (0, "nodata", "Not sure", "No Data", np.array([0, 0, 0]))
    
    def __init__(self, val1, val2, val3, val4, val5):
        self.id = val1
        self.class_name = val2
        self.iiasa_name = val3
        self.esa_class_name = val4
        self.color = val5

DICT_LABELS_COLORS = {
    'cover' : LSCCoverLabelsColors,
    'occlusion' : LSCOcclusionLabelsColors, 
    'ecosystem' : LSCEcosystemLabelsColors,
}

def get_labels_encodings(component):
    return [
        {
            "id": lc.id,
            "color": lc.color,
            "iiasa_name": lc.iiasa_name,
            "name": lc.class_name,
            "esa_name": lc.esa_class_name,
        }
        for lc in DICT_LABELS_COLORS[component]
    ]


COVER_ENCODINGS = get_labels_encodings('cover')
OCCLUSION_ENCODINGS = get_labels_encodings('occlusion')
ECOSYSTEM_ENCODINGS = get_labels_encodings('ecosystem')

COVER_ENCODINGS_DICT = {e["id"]: e for e in COVER_ENCODINGS}
OCCLUSION_ENCODINGS_DICT = {e["id"]: e for e in OCCLUSION_ENCODINGS}
ECOSYSTEM_ENCODINGS_DICT = {e["id"]: e for e in ECOSYSTEM_ENCODINGS}

COVER_COLORMAP = {
    e["id"]: (e["color"] * 255).astype(int).tolist() + [255] for e in COVER_ENCODINGS
}
OCCLUSION_COLORMAP = {
    e["id"]: (e["color"] * 255).astype(int).tolist() + [255] for e in OCCLUSION_ENCODINGS
}
ECOSYSTEM_COLORMAP = {
    e["id"]: (e["color"] * 255).astype(int).tolist() + [255] for e in ECOSYSTEM_ENCODINGS
}

COVER_LABEL_NAMES = {k: COVER_ENCODINGS_DICT[k]["name"] for k in COVER_ENCODINGS_DICT.keys()}
OCCLUSION_LABEL_NAMES = {k: OCCLUSION_ENCODINGS_DICT[k]["name"] for k in OCCLUSION_ENCODINGS_DICT.keys()}
ECOSYSTEM_LABEL_NAMES = {k: ECOSYSTEM_ENCODINGS_DICT[k]["name"] for k in ECOSYSTEM_ENCODINGS_DICT.keys()}


def label_to_rgb(lc_pred, component, colors_enum=None, moveaxis=False):
    
    colors_enum = (
        DICT_LABELS_COLORS[component] if colors_enum is None else colors_enum
    )

    colors = {
        lc.id: {"name": lc.class_name, "color": lc.color} for lc in colors_enum
    }

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
            img_masks.append(
                torch.tensor(binarize_probs(batch[i], labs)).unsqueeze(0)
            )

    img_masks = torch.stack(img_masks, dim=0)
    if not rgb:
        img_masks = torch.cat([img_masks] * 3, dim=1)

    return img_masks


def probs_to_rgb(probs, labs, component):
    return label_to_rgb(binarize_probs(probs, labs), component)


def batch_probs_to_rgb(batch, labs, component):
    was_tensor = False
    if isinstance(batch, torch.Tensor):
        was_tensor = True
        batch = batch.numpy()

    new_batch = np.array([probs_to_rgb(b, labs, component) for b in batch])

    if was_tensor:
        new_batch = torch.Tensor(new_batch)
    return new_batch
