BANDS_V2_S2_FEATS = [
    "s2-B02-p10",
    "s2-B02-p25",
    "s2-B02-p50",
    "s2-B02-p75",
    "s2-B02-p90",
    "s2-B03-p10",
    "s2-B03-p25",
    "s2-B03-p50",
    "s2-B03-p75",
    "s2-B03-p90",
    "s2-B04-p10",
    "s2-B04-p25",
    "s2-B04-p50",
    "s2-B04-p75",
    "s2-B04-p90",
    "s2-B08-p10",
    "s2-B08-p25",
    "s2-B08-p50",
    "s2-B08-p75",
    "s2-B08-p90",
    "s2-B11-p10",
    "s2-B11-p25",
    "s2-B11-p50",
    "s2-B11-p75",
    "s2-B11-p90",
    "s2-B12-p10",
    "s2-B12-p25",
    "s2-B12-p50",
    "s2-B12-p75",
    "s2-B12-p90",
    "s2-ndvi-p10",
    "s2-ndvi-p25",
    "s2-ndvi-p50",
    "s2-ndvi-p75",
    "s2-ndvi-p90",
]

BANDS_V2_S2_STATS = [
    "obs_l2a",
    "scl_invalid_before",
    "scl_invalid_after",
    "scl_snow_cover",
    "scl_dark_cover",
    "scl_water_cover",
    "scl_veg_cover",
    "scl_notveg_cover",
]

BANDS_V2_AUX = ["cop-DEM-alt", "worldcover_2021", "lat", "lon"]

BANDS_V2_S2 = BANDS_V2_S2_FEATS + BANDS_V2_S2_STATS

BANDS_V2 = BANDS_V2_S2 + BANDS_V2_AUX

BANDS_V2_RGB = [f"s2-B0{b}-p50" for b in (4, 3, 2)]

BANDS_NDVI_RGB = [f"s2-ndvi-p{n}" for n in (90, 50, 10)]
BANDS_V2_UNET = [f"s2-B{b:02d}-p50" for b in (2, 3, 4, 8, 11, 12)] + BANDS_NDVI_RGB

BANDS_SEN4LDN_ANNOTATIONS = [
    "sen4ldn-v1_prob10",
    "sen4ldn-v1_prob20",
    "sen4ldn-v1_prob30",
    "sen4ldn-v1_prob40",
    "sen4ldn-v1_prob50",
    "sen4ldn-v1_prob60",
    "sen4ldn-v1_prob70",
    "sen4ldn-v1_prob80",
    "sen4ldn-v1_prob90",
    "sen4ldn-v1_prob95",
    "sen4ldn-v1_prob100",
    "sen4ldn-v1_pred",
    "sen4ldn-v1_cs2020",
    "sen4ldn-v1_cs2021",
]

V2_ANNOTATIONS = {year: ["sen4ldn-v1"] for year in range(2018, 2023)}

V2_ANNOTATIONS[2020] = V2_ANNOTATIONS[2020] + ["evo-v1"]
V2_ANNOTATIONS[2021] = V2_ANNOTATIONS[2021] + ["worldcover-v200"]
