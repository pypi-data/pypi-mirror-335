import enum
import numpy as np


class LabelsColors(enum.Enum):
    # 10,0,100,0,255,Trees covered area
    # 11,88,72,31,255,Trees needle-leaved evergreen
    # 12,112,102,62,255,Trees needle-leaved deciduous
    # 13,0,153,0,255,Trees broadleaved evergreen
    # 14,0,204,0,255,Trees broadleaved deciduous
    # 20,255,187,34,255,Shrub covered area
    # 30,255,255,76,255,Grassland
    # 40,240,150,255,255,Cropland
    # 50,250,0,0,255,Built-up
    # 60,180,180,180,255,Bare areas
    # 70,240,240,240,255,Snow and/or ice cover
    # 80,0,100,200,255,Open water
    # 81,0,0,221,255,Permanent water
    # 82,153,217,234,255,Seasonal water
    # 90,0,150,160,255,Herbaceous wetland
    # 95,0,207,117,255,Mangroves
    # 100,250,230,160,255,Lichens and mosses

    NO_DATA = (0, "nodata", "Not sure", "No Data", np.array([0, 0, 0]))
    TREE = (10, "tree", "tree", "Trees covered area", np.array([0, 100, 0]) / 255)
    TREE_NEEDLE_EV = (
        11,
        "needle_evg",
        None,
        "Trees needle-leaved evergreen",
        np.array([88, 72, 31]) / 255,
    )
    TREE_NEEDLE_DE = (
        12,
        "needle_dec",
        None,
        "Trees needle-leaved deciduous",
        np.array([112, 102, 62]) / 255,
    )
    TREE_BROAD_EV = (
        13,
        "broad_evg",
        None,
        "Trees broad-leaved evergreen",
        np.array([0, 153, 0]) / 255,
    )
    TREE_BROAD_DE = (
        14,
        "broad_dec",
        None,
        "Trees broad-leaved deciduous",
        np.array([0, 204, 0]) / 255,
    )
    SHRUB = (20, "shrub", "shrub", "Shrub cover area", np.array([255, 187, 34]) / 255)
    GRASS = (30, "grass", "grassland", "Grassland", np.array([255, 255, 76]) / 255)
    CROP = (40, "crop", "crops", "Cropland", np.array([240, 150, 255]) / 255)
    BUILT = (50, "built", "urban/built-up", "Built-up", np.array([250, 0, 0]) / 255)
    BARE = (60, "bare", "bare", "Bare areas", np.array([180, 180, 180]) / 255)
    SNOW_AND_ICE = (
        70,
        "snow",
        "snow and ice",
        "Snow and/or ice cover",
        np.array([240, 240, 240]) / 255,
    )
    WATER = (80, "water", "water", "Permanent water", np.array([0, 100, 200]) / 255)
    SEASONAL_WATER = (
        82,
        "seasonal_water",
        None,
        "Seasonal water",
        np.array([153, 217, 234]) / 255,
    )
    SEASONAL_WATER_CROPS = (
        84,
        "sw_crops",
        None,
        "Seasonal water/Crops",
        np.array([245, 233, 245]) / 255,
    )
    SEASONAL_WATER_BARE = (
        86,
        "sw_bare",
        None,
        "Seasonal water/Bare",
        np.array([199, 213, 214]) / 255,
    )
    SEASONAL_WATER_WL = (
        89,
        "sw_wetland",
        None,
        "Seasonal water/Wetland",
        np.array([113, 194, 199]) / 255,
    )
    WETLAND = (
        90,
        "wetland",
        "wetland (herbaceous)",
        "Herbaceous wetland",
        np.array([0, 150, 160]) / 255,
    )
    MANGROVES = (95, "mangroves", None, "Mangroves", np.array([0, 207, 117]) / 255)
    LICHENS = (
        100,
        "lichens_mosses",
        "Lichen and moss",
        "Lichen and moss",
        np.array([250, 230, 160]) / 255,
    )

    def __init__(self, val1, val2, val3, val4, val5):
        self.id = val1
        self.class_name = val2
        self.iiasa_name = val3
        self.esa_class_name = val4
        self.color = val5


def label_to_rgb(lc_pred, colors_enum=None):
    colors_enum = LabelsColors if colors_enum is None else colors_enum

    colors = {lc.id: {"name": lc.class_name, "color": lc.color} for lc in colors_enum}

    # add missing labels from OSM and GSW
    colors[51] = colors[50]
    colors[81] = colors[80]
    colors[61] = colors[60]
    colors[91] = colors[0]
    colors[92] = colors[20]
    colors[93] = colors[95]
    colors[94] = colors[0]

    rgb_pred = np.zeros((lc_pred.shape[0], lc_pred.shape[1], 3))

    for k, v in colors.items():
        for ch in range(3):
            im = rgb_pred[:, :, ch]
            im[lc_pred == k] = v["color"][ch]

    # add alpha channel
    mask = rgb_pred.sum(axis=2) == 0  # all channels are 0
    alpha = np.zeros_like(mask)
    alpha[~mask] = 255
    alpha = np.expand_dims(alpha, axis=2)

    rgb_pred = np.concatenate([rgb_pred, alpha], axis=2)

    return rgb_pred
