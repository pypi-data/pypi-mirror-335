import json
from pathlib import Path

from evotrain.models.lcm10.v12 import DEFAULT_BANDS, DEFAULT_HEAD_BANDS

MODEL_NAME = "lcm10-v12b"

if __name__ == "__main__":
    model_name = MODEL_NAME

    run_id = "v12"

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
            max_epochs=500,
            resume=True,
            gpus=1,
            accumulate_grad_batches=accumulate_grad_batches,
            debug=debug,
        ),
        model=dict(
            architecture="LcmUnetV2",
            bands=DEFAULT_BANDS,
            bands_head=DEFAULT_HEAD_BANDS,
            backbone="mobilenet_v2",
            encoder_depth=5,
            activation="sigmoid",
            activation_conv="sigmoid",
            learning_rate=0.001,
            scheduler_step_size=1,
            scheduler_gamma=0.985,
            classes_weights={
                10: 1,
                20: 1.73,
                30: 0.99,
                40: 1.77,
                50: 2.93,
                60: 2.53,
                70: 16.67,
                80: 1.59,
                90: 4.67,
                95: 11.94,
                100: 7.33,
            },
            head_filters_settings={
                "kernel_size": (9, 7, 5, 3),
                "out_channels": (20, 20, 20, 20),
                "padding_mode": "reflect",
            },
            mlp_hidden_layers=(400, 300, 200, 100, 50),
            dropout_prob=0.2,
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
            batch_size=32,
            workers=12,
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
