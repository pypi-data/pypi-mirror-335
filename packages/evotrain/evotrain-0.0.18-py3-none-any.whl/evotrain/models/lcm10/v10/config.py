import json
from pathlib import Path

NET_LABELS = [10, 20, 30, 40, 50, 60, 70, 80, 90]
DEFAULT_S2_BANDS = [
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

DEFAULT_AUX_BANDS = ["cop-DEM-alt"]
DEFAULT_BANDS = DEFAULT_S2_BANDS + DEFAULT_AUX_BANDS

if __name__ == "__main__":
    model_name = "lcm10-unet-base-v10g"

    run_id = "v1"

    debug = True if "debug" in model_name else False
    mep = True if "mep" in model_name else False

    if mep:
        outpath = "debug_models"
    else:
        if debug:
            outpath = f"/projects/TAP/vegteam/models_dz/lcm10/{run_id}_debug"  # noqa
        else:
            outpath = f"/projects/TAP/vegteam/models_dz/lcm10/{run_id}"

    accumulate_grad_batches = 1

    config_dict = dict(
        trainer=dict(
            output_path=outpath,
            model_name=model_name,
            max_epochs=200,
            resume=True,
            gpus=1,
            accumulate_grad_batches=accumulate_grad_batches,
            debug=debug,
        ),
        model=dict(
            architecture="LcmUnetV2",
            bands=DEFAULT_BANDS,
            bands_head=["latlon", "meteo"],
            backbone="mobilenet_v2",
            encoder_depth=5,
            activation="sigmoid",
            learning_rate=0.0011 * accumulate_grad_batches,
            scheduler_step_size=1,
            scheduler_gamma=0.975,
            classes_weights={50: 6, 20: 3, 70: 10},
            head_filters_settings={
                "kernel_size": (9, 7, 5, 3),
                "out_channels": (20, 20, 20, 20),
                "padding_mode": "reflect",
            },
            mlp_hidden_layers=(300, 200, 200, 100),
            dropout_prob=0.2,
        ),
        dataloader=dict(
            flip_augmentation=True,
            rotate_augmentation=True,
            shuffle_locs=True,
            sort_locs_by_latitude=False,
            shuffle_train=True,
            k_factor=5,
            k_factor_jitter=0,
            meteo_jitter=0.05,
            latlon_jitter=0.5,
            batch_size=32,
            workers=10,
            n_val_locs=10000,
            locs_scenario="base",
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
