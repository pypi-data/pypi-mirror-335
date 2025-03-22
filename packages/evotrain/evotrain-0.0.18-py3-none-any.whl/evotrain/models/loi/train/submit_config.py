import json
import getpass
import socket
from pathlib import Path
from pydantic import BaseModel, field_validator
from typing import Dict, Union
from datetime import datetime


date_now_str = datetime.now().strftime("%y%m%d%H%M")  # Format: yymmddHHMM

# Define the model name
model_name = "v8aa"


class MetaConfig(BaseModel):
    date: str = date_now_str
    author: str = getpass.getuser()
    hostname: str = socket.gethostname()
    pt_model_name: str
    node_name: str = "sasdsnode05"
    email: str = "yannis.kalfas@vito.be"
    gpus: int = 1
    memory: str = "32gb"
    cpus_per_task: int = 4
    ntasks: int = 1
    walltime: str = "72:00:00"

    @field_validator("pt_model_name")
    def generate_pt_model_name(cls, v):
        return f"{date_now_str}_{v}"


class TrainingConfig(BaseModel):
    output_path: str = f"/home/vito/{getpass.getuser()}/projects/vegteam/models_clouds"
    pt_model_name: str
    debug: bool = False
    resume: bool = False
    use_wandb: bool = False
    enable_augmentations: dict[str, bool] = {
        "train": True,
        "val": False,
        "test": False,
    }
    augmentations: dict[str, bool] = {
        "flip_augmentation": True,
        "rotate_augmentation": True,
    }
    tune_lr: bool = True

    @field_validator("pt_model_name")
    def generate_pt_model_name(cls, v):
        return f"{date_now_str}_{v}"


class LightningTrainerConfig(BaseModel):
    log_every_n_steps: int = 50
    max_epochs: int = 120
    precision: str = "16-mixed"
    check_val_every_n_epoch: int = 1
    devices: int = 1  # number of gpus
    accumulate_grad_batches: int = 1  # number of batches to accumulate before backprop


class DataLoadersConfig(BaseModel):
    train: dict[str, Union[str, int]] = {
        "batch_size": 64,
        "shuffle": True,
        "num_workers": 2,
        "pin_memory": False,
    }
    val: dict[str, Union[str, int]] = {
        "batch_size": 32,
        "shuffle": False,
        "num_workers": 2,
        "pin_memory": False,
    }
    test: dict[str, Union[str, int]] = {
        "batch_size": 32,
        "shuffle": False,
        "num_workers": 2,
        "pin_memory": False,
    }


class DLModelConfig(BaseModel):
    activation: str = "softmax2d"  # is set to "sigmoid" downstream if softseg=True
    arch: str = "Unet"
    architecture_version: str = "vLcmUnetV2"  # "LcmUnet", "vLcmUnetV2"
    backbone: str = "mobilenet_v2"
    bands_head: list[str] = ["latlon", "meteo", "seasonal"]
    class_weights_list: list[float] = [
        1.0,
        1.0,
        1.0,
        1.0,
    ]
    # [class1, class2, class3, class4] according to the labels (NOTE: only works for ce loss)
    dropout_rate: float = 0.1
    head_filters_settings: Dict[str, Union[str, list[int]]] = {
        "kernel_size": [9, 7, 5, 3],
        "out_channels": [20, 20, 20, 20],
        "padding_mode": "reflect",
    }
    label_smoothing_factor: float = 0.0
    learning_rate: float = 0.001
    loss: str = "mse"  # "mse", "ce", "focal", "dice", ...
    mlp_hidden_layers: tuple[int, ...] = (256, 128, 64, 32)
    optimizer: str = "adamw"  # "adam", "sgd", "adamw"
    optimizer_weight_decay: float = 0.01
    sample_weights: list[float] = []
    # [weights for high, weights for other] - e.g. [1.0, 0.5] - empty [] to disable
    scheduler: str = "cosine"  # "steplr", "cosine", "cosinewarm", "plateau", "cyclic", "" (empty and sgd optimizer for fixed lr)
    scheduler_params: dict[str, Union[float, str]] = {
        "steplr_step_size": 5.0,  # for steplr
        "steplr_gamma": 0.1,  # for steplr
        "cosine_T_max": 10.0,  # for cosine
        "cosine_eta_min": 0.0,  # for cosine
        "cosinewarm_T_0": 10.0,  # for cosine warm restarts
        "cosinewarm_T_mult": 2.0,  # for cosine warm restarts
        "cosinewarm_eta_min": 0.0,  # for cosine warm restarts
        "plateau_patience": 5.0,  # for plateau
        "plateau_factor": 0.1,  # for plateau
        "plateau_min_lr": 1e-6,  # for plateau
        "cyclic_cycle_momentum": False,  # for cyclic
        "cyclic_base_lr": 1e-4,  # for cyclic
        "cyclic_max_lr": 1e-3,  # for cyclic
        "cyclic_step_size_up": 2000.0,  # for cyclic
        "cyclic_mode": "triangular2",  # for cyclic
        "cyclic_gamma": 1.0,  # for cyclic
    }


class DataConfig(BaseModel):
    dataset: str = "cloudsen12plus"  # "cloudsen12" or "cloudsen12plus"
    resolution: int = 60  # meters [60 or 80] # NOTE: adapt the dataset path accordingly
    dataset_path: str = "/local/TAP/vegteam/training_data/cloudsen12plus/dataset_60m"
    metadata_path: str = (
        "/local/TAP/vegteam/training_data/cloudsen12plus/metadata.parquet"
    )
    splitting_method: str = "cloudsen12"  # "cloudsen12" or "roibased" or "random"
    train_samples_into_val: int = 0  # number of samples to move from train to val
    merge_test_into_val: bool = False  # whether to merge the test set into val set
    label_layers: list[str] = [
        "label_cm2plus",
        "label_cm1plus",
        "label_fmask",
        "label_sen2cor",
    ]
    extra_other_samples: int = 30_000
    classify_snow: bool = False
    callback_val_inds: list[int] = [
        44,
        300,
        458,
        119,
        103,
        265,
        397,
        512,
        331,
        108,
        269,
        453,
        330,
    ]
    callback_test_inds: list[int] = [
        673,
        803,
        630,
        82,
        126,
        443,
        306,
        949,
        503,
        245,
        760,
    ]
    callback_train_inds: list[int] = [
        26690,
        15306,
        29397,
        10371,
        8015,
        24680,
        17972,
        26094,
        23620,
        13919,
        28639,
    ]


class BandsConfig(BaseModel):
    s2_bands: list[str] = [
        "l2a-B01",
        "l2a-B02",
        "l2a-B03",
        "l2a-B04",
        "l2a-B8A",
        "l2a-B09",
        "l2a-B11",
        "l2a-B12",
    ]


class ScalingConfig(BaseModel):
    s2_scaling: int = 10000
    k_factor: int = 5
    k_factor_jitter: int = 2
    dem_scaling: int = 4000
    lat_scaling: int = 90
    lon_scaling: int = 180
    latlon_jitter: float = 0.1
    meteo_jitter: float = 0.02


class LabelsConfig(BaseModel):
    selected: str = "cloudsen12_mergedclouds_extrasnow"
    cloudsen12: dict[str, int] = {
        "SURFACE": 0,
        "CLOUDS": 1,
        "THIN_CLOUDS": 2,
        "SHADOWS": 3,
    }
    cloudsen12plus: dict[str, int] = {
        "SURFACE": 0,
        "CLOUDS": 1,
        "THIN_CLOUDS": 2,
        "SHADOWS": 3,
    }
    fmask: dict[str, int] = {
        "SURFACE": 0,
        "WATER": 1,
        "SHADOWS": 2,
        "SNOW": 3,
        "CLOUDS": 4,
    }
    scl: dict[str, int] = {
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
    cloudsen12_mergedclouds_extrasnow: dict[str, int] = {
        "SURFACE": 0,
        "CLOUDS": 1,
        "SHADOWS": 2,
        "SNOW": 3,
    }
    cloudsen12_extrasnow: dict[str, int] = {
        "SURFACE": 0,
        "CLOUDS": 1,
        "THIN_CLOUDS": 2,
        "SHADOWS": 3,
        "SNOW": 4,
    }
    # source: https://huggingface.co/datasets/isp-uv-es/CloudSEN12Plus/blob/main/README.md
    cloudsen12plus_scribble: dict[str, int] = {
        "clear": 0,
        "thick-cloud border": 1,
        "thick-cloud center": 2,
        "thin-cloud border": 3,
        "thin-cloud center": 4,
        "cloud-shadow border": 5,
        "cloud-shadow center": 6,
    }


class ColorsConfig(BaseModel):
    SURFACE: list[int] = [0, 255, 0]  # green
    CLOUDS: list[int] = [255, 255, 255]  # white
    THIN_CLOUDS: list[int] = [0, 255, 255]  # cyan
    SHADOWS: list[int] = [105, 105, 105]  # darker gray
    SNOW: list[int] = [255, 0, 255]  # magenta

    # Sentinel-2 L2A SCL colors (https://custom-scripts.sentinel-hub.com/custom-scripts/sentinel-2/scene-classification/)
    NA: list[int] = [0, 0, 0]  # black
    SATURATED_DEFECTIVE: list[int] = [255, 0, 0]  # red
    DARK_FEATURES_SHADOWS: list[int] = [47, 47, 47]  # dark gray
    CLOUD_SHADOWS: list[int] = [100, 50, 0]  # brown
    VEGETATION: list[int] = [0, 160, 0]  # green
    NOT_VEGETATED: list[int] = [255, 230, 90]  # yellow
    WATER: list[int] = [0, 0, 255]  # blue
    UNCLASSIFIED: list[int] = [128, 128, 128]  # gray
    CLOUDS_MEDIUM_PROB: list[int] = [192, 192, 192]  # light gray
    CLOUDS_HIGH_PROB: list[int] = [255, 255, 255]  # white
    THIN_CIRRUS: list[int] = [100, 200, 255]  # light blue
    SNOW_ICE: list[int] = [255, 150, 255]  #


class Configuration(BaseModel):
    meta_config: MetaConfig
    lightning_trainer_config: LightningTrainerConfig
    dataloaders_config: DataLoadersConfig
    training_config: TrainingConfig
    dl_model_config: DLModelConfig
    data_config: DataConfig
    labels_config: LabelsConfig
    colors_config: ColorsConfig
    bands_config: BandsConfig
    scaling_config: ScalingConfig


############################################
# Main function to generate the config file
############################################
def main():
    # Create a configuration object to generate the configuration file
    config = Configuration(
        # Settings specific to the job submission on the HPC
        meta_config=MetaConfig(
            pt_model_name=model_name,
            node_name="sasdsnode05",
            # email="",  # set the email address to receive notifications
        ),
        # Settings for the DataLoaders
        dataloaders_config=DataLoadersConfig(
            train={
                "batch_size": 64,
                "num_workers": 2,
                "pin_memory": False,
                "shuffle": True,
            },
            val={
                "batch_size": 32,
                "num_workers": 2,
                "pin_memory": False,
                "shuffle": False,
            },
            test={
                "batch_size": 32,
                "num_workers": 2,
                "pin_memory": False,
                "shuffle": False,
            },
        ),
        # General training settings
        training_config=TrainingConfig(
            pt_model_name=model_name,
            enable_augmentations={
                "train": True,
                "val": False,
                "test": False,
            },
            tune_lr=False,
            debug=False,  # set to True to train on fewer samples
        ),
        # Settings for the Lightning Trainer
        lightning_trainer_config=LightningTrainerConfig(
            max_epochs=17,
            log_every_n_steps=10,
        ),
        # Model specific settings (go into model_kwargs)
        dl_model_config=DLModelConfig(
            architecture_version="CloudArchV2",  # "LcmUnetV2",
            head_filters_settings={
                "kernel_size": [3],
                "out_channels": [16],
                "padding_mode": "reflect",
            },
            mlp_hidden_layers=(16,),
            activation="sigmoid",
            backbone="mobilenet_v2",
            class_weights_list=[
                0.7,
                0.9,
                1.2,
                1.2,
            ],  # [0.1715, 0.3190, 1.5615, 1.9480] # for snow # [0.5,0.9,2.9,3.1,], # for normal
            dropout_rate=0.2,
            label_smoothing_factor=0.05,
            learning_rate=0.0001,  # 0.001,  # controlled by: 'tune_lr' (TrainingConfig)
            loss="mse",  # "mse", "ce", "focal", "dice", ...
            optimizer="adamw",  # "adam", "sgd", "adamw"
            optimizer_weight_decay=0.0001,
            scheduler="cosinewarm",
            scheduler_params={
                "cosinewarm_T_0": 5.0,
                "cosinewarm_T_mult": 2.0,
                "cosinewarm_eta_min": 6e-05,
            },
        ),
        # Settings for the data (splitting, paths, etc.)
        data_config=DataConfig(
            dataset="cloudsen12plus",
            train_samples_into_val=0,  # 5000,
            merge_test_into_val=False,  # True,
            resolution=60,  # meters
            extra_other_samples=31200,
            classify_snow=True,
        ),
        labels_config=LabelsConfig(),  # use the default labels
        colors_config=ColorsConfig(),  # use the default colors
        bands_config=BandsConfig(),  # use the default bands
        scaling_config=ScalingConfig(),  # use the default scaling params
    )

    mep_outpath = Path(f"/home/vito/{getpass.getuser()}/configs/train_configs")
    try:
        mep_outpath.mkdir(parents=True, exist_ok=True)
        print(f"Config will be saved to {mep_outpath}")
    except Exception as e:
        print(f"Failed to create directory: {mep_outpath}, Error: {e}")
        mep_outpath = Path(f"/data/users/Private/{getpass.getuser()}/configs/train_configs")
        try:
            mep_outpath.mkdir(parents=True, exist_ok=True)
            print(f"Config will be saved to {mep_outpath}")
        except Exception as e:
            print(f"Failed to create directory: {mep_outpath}, Error: {e}")
            raise e

    fn = f"{config.meta_config.pt_model_name}.json"
    with open(f"{mep_outpath}/{fn}", "w") as f:
        json.dump(config.dict(), f, indent=4)
        print(f"Config saved to {mep_outpath}/{fn}")

    # Make sure that the dataset_path and metadata_path are correctly set in the configuration
    # Check if the dataset_path and metadata_path are correctly set
    if not Path(config.data_config.dataset_path).exists():
        raise FileNotFoundError(
            f"Dataset path not found: {config.data_config.dataset_path}"
        )
    if not Path(config.data_config.metadata_path).exists():
        raise FileNotFoundError(
            f"Metadata path not found: {config.data_config.metadata_path}"
        )
    # Check if resolution is set to 60 or 80 then dataset_path should contain "60m" or "80m"
    if str(config.data_config.resolution) + "m" not in config.data_config.dataset_path:
        raise ValueError(
            f"Resolution {config.data_config.resolution}m does not match with dataset path: {config.data_config.dataset_path}"
        )

    # Check if debug has been set to True in the configuration
    if config.training_config.debug:
        print("Debug mode is enabled. Exiting...")
        # Ask user to confirm
        user_input = input("Do you want to continue with training? (y/n): ")
        if user_input.lower() != "y":
            print("Exiting...")
            exit()

    # Return the configuration file name (full path)
    return f"{mep_outpath}/{fn}"


if __name__ == "__main__":
    import os
    import argparse

    # From argparse we want a single bool argument (-s, --submit_to_hpc) of whether to submit the job or not
    parser = argparse.ArgumentParser(
        description="Generate a training configuration file for the cloud detection model."
    )
    parser.add_argument(
        "-s",
        "--submit_to_hpc",
        action="store_true",
        help="Submit the training job to the HPC.",
    )
    # now by default the argument is False so we need to negate it by running: python gen_config.py -s
    args = parser.parse_args()

    config_fn = main()

    if not args.submit_to_hpc:
        print(
            "Training job not submitted. Please use the -s/--submit_to_hpc flag to submit the job."
        )
        exit()
    else:
        print("Training job will be submitted to the HPC.")
        # Submit the training job to the HPC
        os.system(f"bash job_submit.sh trainer.py {config_fn}")
