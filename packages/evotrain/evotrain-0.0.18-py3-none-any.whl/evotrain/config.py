import json
from pathlib import Path
from pydantic import BaseModel, field_validator
from typing import Dict, List, Union
import getpass
from datetime import datetime
from loguru import logger
import subprocess

date_now_str = datetime.now().strftime("%y%m%d%H%M")  # Format: yymmddHHMM


class MetaConfig(BaseModel):
    date: str = date_now_str
    author: str = getpass.getuser()
    hostname: str = "sasdsnode01.vito.local"
    pt_model_name: str
    node_name: str = "sasdsnode01"
    email: str = "yannis.kalfas@vito.be"
    gpus: str = "rtx2080:1"
    memory: str = "16gb"
    cpus_per_task: int = 4
    ntasks: int = 1
    walltime: str = "96:00:00"
    venv_path: str = "/projects/TAP/vegteam/environments/evotrain_env/.venv"

    @field_validator("pt_model_name")
    def generate_pt_model_name(cls, v):
        return f"{v}"


class TrainerConfig(BaseModel):
    output_path: str
    model_name: str
    max_epochs: int = 500
    resume: bool = True
    gpus: int = 1
    accumulate_grad_batches: int = 1
    debug: bool = False


class ModelConfig(BaseModel):
    architecture: str = "LcmUnetV2"
    bands: List[str] = [
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
    bands_head: List[str] = ["latlon", "meteo"]
    bands_aux: List[str] = ["cop-DEM-alt"]
    backbone: str = "mobilenet_v2"
    encoder_depth: int = 5
    loss: str = "mse"
    activation: str = "sigmoid"
    activation_conv: str = "sigmoid"
    learning_rate: float = 0.001
    optimizer: str = "adam"  # "adam", "adamw", "sgd"
    optimizer_weight_decay: float = 0.01
    scheduler: str = "cosinewarm"  # "steplr", "cosine", "cosinewarm", "plateau", "cyclic", "" (empty and sgd optimizer for fixed lr)
    scheduler_params: dict[str, Union[float, str]] = {
        "steplr_step_size": 1,
        "steplr_gamma": 0.985,
        "cosine_T_max": 10.0,
        "cosine_eta_min": 0.0,
        "cosinewarm_T_0": 10.0,
        "cosinewarm_T_mult": 2.0,
        "cosinewarm_eta_min": 0.0,
        "plateau_patience": 5.0,
        "plateau_factor": 0.1,
        "plateau_min_lr": 1e-6,
        "cyclic_cycle_momentum": False,
        "cyclic_base_lr": 1e-4,
        "cyclic_max_lr": 1e-3,
        "cyclic_step_size_up": 2000.0,
        "cyclic_mode": "triangular2",
        "cyclic_gamma": 1.0,
    }
    classes_weights: Dict[int, float] = {
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
    }
    binary_pos_weight: float = 3.5
    head_filters_settings: Dict[str, Union[str, list[int]]] = {
        "kernel_size": [9, 7, 5, 3],
        "out_channels": [20, 20, 20, 20],
        "padding_mode": "reflect",
    }
    mlp_hidden_layers: tuple[int, ...] = (400, 300, 200, 100, 50)
    dropout_prob: float = 0.2
    binary_osmroads_threshold: float = 0.05


class DataLoaderConfig(BaseModel):
    flip_augmentation: bool = True
    rotate_augmentation: bool = True
    noise_augmentation: bool = True
    spectral_augmentation: bool = True
    translation_augmentation: bool = True
    masking_augmentation: bool = True
    shuffle_locs: bool = True
    sort_locs_by_latitude: bool = True
    shuffle_train: bool = True
    k_factor: int = 0
    k_factor_jitter: int = 0
    meteo_jitter: float = 0.02
    latlon_jitter: float = 0.25
    batch_size: int = 64
    workers: int = 8
    n_val_locs: int = 10000
    locs_scenario: str = "base"


class Config(BaseModel):
    meta_config: MetaConfig
    trainer: TrainerConfig
    model: ModelConfig
    dataloader: DataLoaderConfig


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--model_name",
        type=str,
        help="Name of the model",
        default="TEST",
        required=True,
    )
    parser.add_argument(
        "-r", "--run_id", type=str, help="Run ID", default="v00", required=True
    )
    parser.add_argument(
        "-p", "--product", type=str, help="Product name", default="lcm10", required=True
    )
    parser.add_argument(
        "-e", "--email", type=str, help="Email address", default="", required=True
    )
    parser.add_argument("-s", "--submit", action="store_true", help="Submit the job")
    parser.add_argument(
        "-t",
        "--trainer_fn",
        type=str,
        help="Trainer file path",
        default="src/evotrain/models/lcm10/v12/trainer.py",
        required=True,
    )
    parser.add_argument(
        "-dr", "--debug_run", action="store_true", help="Debug-run mode"
    )
    args = parser.parse_args()

    if args.submit and args.debug_run:
        raise ValueError("Cannot use both --submit and --debug_run at the same time")

    model_name = args.model_name
    run_id = args.run_id
    product = args.product
    email = args.email
    trainer_fn = Path(args.trainer_fn)
    if not trainer_fn.exists():
        raise FileNotFoundError(f"File {trainer_fn} does not exist")

    debug = "debug" in model_name
    mep = "mep" in model_name

    if mep:
        outpath = "debug_models"
    else:
        outpath = f"/projects/TAP/vegteam/models_{product}/{run_id}"
        if debug:
            outpath += "_debug"

    config = Config(
        meta_config=MetaConfig(
            pt_model_name=model_name,
            email=email,
        ),
        trainer=TrainerConfig(
            output_path=outpath,
            model_name=model_name,
            debug=debug,
        ),
        model=ModelConfig(
            bands=[
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
            ],
            architecture="LcmUnetV2",
            head_filters_settings={
                "kernel_size": (3,),
                "out_channels": (4,),
                "padding_mode": "reflect",
            },
            binary_pos_weight=3.5,
            mlp_hidden_layers=(4,),
            loss="mse",
            activation="sigmoid",
            optimizer="adamw",
            optimizer_weight_decay=0.0001,
            scheduler="cosinewarm",
            scheduler_params={
                "cosinewarm_T_0": 5.0,
                "cosinewarm_T_mult": 2.0,
                "cosinewarm_eta_min": 6e-05,
            },
            binary_osmroads_threshold=0.15,
        ),
        dataloader=DataLoaderConfig(
            flip_augmentation=True,
            rotate_augmentation=True,
            noise_augmentation=True,
            spectral_augmentation=False,
            translation_augmentation=True,
            masking_augmentation=True,
            sort_locs_by_latitude=False,
            n_val_locs=1000,
        ),
    )

    fns = [
        Path(f"configs/{model_name}.json"),
        Path(outpath) / model_name / "config.json",
    ]

    for fn in fns:
        # Create the directory if it doesn't exist
        logger.info(f"Writing config to {fn}")
        logger.info("Verify that write permissions are set correctly")
        fn.parent.mkdir(parents=True, exist_ok=True)
        # Set the permissions to 2775
        fn.parent.chmod(0o2775)
        with open(fn, "w") as f:
            json.dump(config.dict(), f, indent=4)
        logger.info(f"Config written to {fn}")

    if args.submit:
        logger.info("Submitting the job")
        # To submit we need to run the command `bash job_submit.sh <trainer.py> <config.json>`
        # We can use the `subprocess` module to run the command

        cmd = f"bash job_submit.sh {trainer_fn} {fns[1]}"
        logger.info(f"Running command: {cmd}")
        subprocess.run(cmd, shell=True)
    elif args.debug_run:
        logger.info("Running the job in debug mode")
        # To run the job in debug mode we need to run the command `python <trainer.py> <config.json>`
        # We can use the `subprocess` module to run the command

        cmd = f"python {trainer_fn} {fns[1]}"
        logger.info(f"Running command: {cmd}")
        subprocess.run(cmd, shell=True)

# Example usage:
# python config.py -m TEST -r v12 -p lcm10 -e "your_email@example.com" -s -t src/evotrain/models/lcm10/v12/trainer.py
