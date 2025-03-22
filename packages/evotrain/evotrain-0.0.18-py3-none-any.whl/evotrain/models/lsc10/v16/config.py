import json
from pathlib import Path

from evotrain.models.lsc10.v16 import DEFAULT_BANDS, DEFAULT_HEAD_BANDS

MODEL_NAME = "lsc10-v16_d"

if __name__ == "__main__":
    model_name = MODEL_NAME

    run_id = "v16"

    debug = True if "debug" in model_name else False
    mep = True if "mep" in model_name else False

    if mep:
        outpath = "debug_models"
    else:
        if debug:
            outpath = f"/projects/TAP/vegteam/models_wdk/lsc10/{run_id}_debug"  # noqa
        else:
            outpath = f"/projects/TAP/vegteam/models_wdk/lsc10/{run_id}"

    accumulate_grad_batches = 1

    config_dict = dict(
        trainer=dict(
            output_path=outpath,
            model_name=model_name,
            max_epochs=500,
            resume=True,
            gpus=1,
            accumulate_grad_batches=accumulate_grad_batches,
            debug=debug,
        ),
        model=dict(
            loss_weight_cover=1,
            loss_weight_occlusion=1,
            loss_weight_attribute=1,
            classes_components=dict(
                cover={
                    0:'tree',
                    1:'shrub',
                    2:'herbaceous vegetation',
                    3:'not vegetated',
                    4:'water',
                },
                occlusion={
                    0:'snow',
                    1:'thick clouds / thin clouds',
                    2:'shadow',
                    3:'surface',
                },
                attribute={
                    0:'cropland',
                    1:'mangrove',
                    2:'built-up',
                    3:'herbaceous wetland',
                    4:'lichens',
                    5:'road',
                },
            ),
            classes={
                0:'tree',
                1:'shrub',
                2:'herbaceous vegetation',
                3:'not vegetated',
                4:'water',
                5:'snow',
                6:'thick clouds / thin clouds',
                7:'shadow',
                8:'surface',
                9:'cropland',
                10:'mangrove',
                11:'built-up',
                12:'herbaceous wetland',
                13:'lichens',
                14:'road',
            },
            architecture="LcmUnetV2",
            bands=[
                "B02",
                "B03",
                "B04",
                "B08",
                "B05",
                "B06",
                "B07",
                "B8A",
                "B11",
                "B12",
                "cop-DEM-alt",
                "VV",
                "VH",
                "VHVVRATIO"
                # "VV",
                # "VH",
                # "VHVVRATIO"
],#DEFAULT_BANDS,
            bands_head=DEFAULT_HEAD_BANDS,
            encoder_name="mobilenet_v2",
            encoder_depth=5,
            activation_mlp="identity",
            activation_spatial="sigmoid",
            learning_rate=0.001,
            scheduler='StepLR',#'CosineAnnealingWarmRestarts',
            scheduler_T_0=5,
            scheduler_T_mult=2,
            scheduler_eta_min=6e-05,
            scheduler_last_epoch=-1,
            scheduler_step_size=1,
            scheduler_gamma=0.985,
            classes_weights_components=dict(
                cover={
                    0:0.60,
                    1:0.75,
                    2:0.61,
                    3:0.57,
                    4:0.84,
                },
                occlusion={
                    0:0.82,
                    1:1.30,
                    2:6.79,
                    3:0.13,
                },
                attribute={
                    0:0.82,
                    1:6.10,
                    2:1.34,
                    3:2.54,
                    4:7.11,
                    5:4,#2.78,
                },
            ),
            classes_weights={   
                0: 0.60, # tree
                1: 0.75, # shrub
                2: 0.61, # herbaceous vegetation
                3: 0.57, # not vegetated
                4: 0.84, # water
                5: 0.82, # snow
                6: 1.30, # thick clouds / thin clouds
                7: 6.79, # shadow
                8: 0.13, # surface
                9: 0.82, # cropland
                10: 6.10, # mangrove
                11: 1.34, # built-up
                12: 2.54, # herbaceous wetland
                13: 7.11, # lichens
                14: 4,#2.78, # road 2.78
            },            spatial_filters_settings={
                "kernel_size": (9, 7, 5, 3),
                "out_channels": (15, 15, 15, 15),
                "padding_mode": "reflect",
            },
            mlp_hidden_layers=(400, 300, 200, 100, 50),
            dropout_prob=0.2,
            adaptive_scaling_spatial_params=None,
            adaptive_scaling_mlp_params=None,
            
        ),
        dataloader=dict(
            flip_augmentation=True,
            rotate_augmentation=True,
            shuffle_locs=True,
            sort_locs_by_latitude=False,
            shuffle_train=True,
            k_factor=0,
            k_factor_jitter=0,
            meteo_jitter=0.02,
            latlon_jitter=0.25,
            season_jitter=15,
            doy_jitter=15,
            batch_size=32,
            workers=12,
            n_val_locs=10000,
            locs_scenario="all",
        ),
    )

    fns = [
        Path(f"configs/{model_name}.json"),
        Path(outpath) / model_name / "config.json",
    ]

    for fn in fns:
        fn.parent.mkdir(parents=True, exist_ok=True)
        with open(fn, "w") as f:
            json.dump(config_dict, f, indent=4)
        print(f"Config written to {fn}")
