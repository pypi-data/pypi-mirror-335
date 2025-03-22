import enum

class LabelsColorsLsc_v4(enum.Enum):

    NO_DATA = (255, 'nodata', 'Not sure', 'No Data', np.array([0, 0, 0]))
    TREE = (1, 'tree', 'tree', 'Trees covered area',
            np.array([0, 100, 0]) / 255)
    SHRUB = (2, 'shrub', 'shrub', 'Shrub cover area',
             np.array([255, 187, 34]) / 255)
    GRASS = (3, 'grass', 'grassland', 'Grassland',
             np.array([255, 255, 76]) / 255)
    BUILT = (5, 'built', 'urban/built-up',
             'Built-up', np.array([250, 0, 0]) / 255)
    BARE = (6, 'bare', 'bare', 'Bare areas', np.array([180, 180, 180]) / 255)
    SNOW_AND_ICE = (7, 'snow', 'snow and ice', 'Snow and/or ice cover',
                    np.array([240, 240, 240]) / 255)
    WATER = (8, 'water', 'water', 'Permanent water',
             np.array([0, 100, 200]) / 255)
    WETLAND = (9, 'wetland', 'wetland (herbaceous)', 'Herbaceous wetland',
               np.array([0, 150, 160]) / 255)
    MANGROVES = (4, 'mangroves', None, 'Mangroves',
                 np.array([0, 207, 117]) / 255)
    LICHENS = (10, 'lichens_mosses', 'Lichen and moss', 'Lichen and moss',
               np.array([250, 230, 160]) / 255)
    THICK_CLOUDS = (11, 'thick clouds', 'thick clouds', 'thick clouds',
               np.array([184, 2, 129]) / 255)
    THIN_CLOUDS = (12, 'thin clouds', 'thin clouds', 'thin clouds',
               np.array([166, 111, 250]) / 255)
    SHADOW = (13, 'shadow', 'shadow', 'shadow',
               np.array([213, 159, 253]) / 255)

    def __init__(self, val1, val2, val3, val4, val5):
        self.id = val1
        self.class_name = val2
        self.iiasa_name = val3
        self.esa_class_name = val4
        self.color = val5

lsc_colormap_v4_0 = {
    255: (0, 0, 0, 255), # clouds and shadows
    1: (0, 100, 0, 255), # woody
    2: (255, 187, 34, 255),# herbaceous
    3: (255, 255, 76, 255), # not vegetated 
    5: (250, 0, 0, 255),
    6: (180, 180, 180, 255),
    7: (240, 240, 240, 255),
    8: (0, 100, 200, 255),
    9: (0, 150, 160, 255),
    4: (0, 207, 117, 255),
    10: (250, 230, 160, 255),
    11: (184, 2, 129, 255),
    12: (166, 111, 250, 255),
    13: (213, 159, 253, 255),

}     

def label_to_rgb(lc_pred, colors_enum=None):
    colors_enum = LabelsColors if colors_enum is None else colors_enum

    colors = {lc.id: {'name': lc.class_name,
                      'color': lc.color}
              for lc in colors_enum}
    
    rgb_pred = np.zeros((lc_pred.shape[0],
                         lc_pred.shape[1],
                         3))

    for k, v in colors.items():
        for ch in range(3):
            im = rgb_pred[:, :, ch]
            im[lc_pred == k] = v['color'][ch]

    return rgb_pred