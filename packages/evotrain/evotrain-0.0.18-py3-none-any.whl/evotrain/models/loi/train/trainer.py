"""
This script trains the CloudNet model using Pytorch Lightning. The model is
trained using the training and validation datasets generated using the
`get_train_val_dataloaders` function. The training is done using the `fit`
method of the Pytorch Lightning Trainer class. The training is done for a
maximum number of epochs specified in the configuration file. The model is
saved at the end of the training.
"""

import json
import os
from pathlib import Path

import torch
from loguru import logger

from lightning.pytorch.callbacks import (
    EarlyStopping,
    LearningRateMonitor,
    ModelCheckpoint,
    TQDMProgressBar,
)
from lightning.pytorch.loggers import TensorBoardLogger
from lightning.pytorch import Trainer
from lightning.pytorch.tuner import Tuner

from tbparse import SummaryReader

from evotrain.models.loi.callbacks import InferencePreviewClouds
from evotrain.models.loi.model import CloudNet, get_checkpoints
from evotrain.models.loi.dataset import CloudsenDataset, read_metadata


def train_cloudnet(config, debug=False):
    # Load configuration parameters from the config file
    lightning_trainer_config = config["lightning_trainer_config"]
    dl_model_config = config["dl_model_config"]
    training_config = config["training_config"]
    data_config = config["data_config"]
    meta_config = config["meta_config"]

    # Tensorboard logger
    tt_logger = TensorBoardLogger(
        save_dir=training_config["output_path"],
        version=0,  # pl always creates a log_dir/version_X folder; can only override "version"
        name=training_config["pt_model_name"],
    )

    # Define the sub-directory to save results
    output_path_subdir = (
        Path(tt_logger.save_dir) / tt_logger.name / f"version_{tt_logger.version}"
    )
    # Assert it does not exist yet
    assert not output_path_subdir.exists(), (
        f"Output path {output_path_subdir} already exists. Is the model already training/trained?"
    )
    Path(output_path_subdir).mkdir(parents=True, exist_ok=True)

    # Configure loguru logger to write to a file
    log_file_path = output_path_subdir / "process.log"
    logger.add(log_file_path, format="{time} {level} {message}", level="INFO")

    # Log meta information from the config file
    logger.info(f"Model: {meta_config['pt_model_name']}")
    logger.info(f"Node: {meta_config['node_name']}")
    logger.info(f"GPUs: {meta_config['gpus']}")
    logger.info(f"CPUs-per-task: {meta_config['cpus_per_task']}")
    logger.info(f"Memory: {meta_config['memory']}")
    logger.info(f"Walltime: {meta_config['walltime']}")

    # Log the dataset and metadata paths
    logger.info(f"Dataset: {data_config['dataset']}")
    logger.info(f"Resolution: {data_config['resolution']}m")
    logger.info(f"Loading dataset from: {config['data_config']['dataset_path']}")
    logger.info(f"Loading metadata from: {config['data_config']['metadata_path']}")

    # Log the model of the GPU if available
    if torch.cuda.is_available():
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")

    # Save the config dict to a file in the output_path_subdir
    with open(output_path_subdir / "config.json", "w") as f:
        json.dump(config, f, indent=4)
    logger.info("Config saved: ✓")

    if training_config["use_wandb"]:
        # Wandb logger
        from lightning.pytorch.loggers import WandbLogger

        wandb_logger = WandbLogger(
            name=training_config["pt_model_name"],
            project=os.environ["WANDB_PROJECT"],
            entity=os.environ["WANDB_ENTITY"],
            log_model=False,
            save_dir=training_config["output_path"],
        )
        # Include wandb logger in the list of loggers
        loggers = [tt_logger, wandb_logger]
        logger.info("Wandb logger: ENABLED")
    else:
        logger.info("Wandb logger: DISABLED")
        loggers = tt_logger

    # Setup the datasets
    dataset = CloudsenDataset(
        dataset=read_metadata(config["data_config"]["metadata_path"], config=config),
        config=config,
    )
    dataset.prepare_data()
    dataset.setup()

    # Define the model
    # Get the model arguments from the config file
    model_kwargs = {
        key: dl_model_config[key]
        for key in [
            "activation",
            "arch",
            "architecture_version",
            "backbone",
            "bands_head",
            "class_weights_list",
            "dropout_rate",
            "head_filters_settings",
            "label_smoothing_factor",
            "learning_rate",
            "loss",
            "mlp_hidden_layers",
            "optimizer",
            "sample_weights",
            "scheduler",
        ]
    }
    # Add the dataset, config, and device to the model arguments
    model_kwargs.update(
        {
            "bands": dataset.bands,
            "classes": dataset.labels,
            "config": config,
            "device": torch.device("cuda:0" if torch.cuda.is_available() else "cpu"),
        }
    )

    # Check whether pretrained model exists. If yes, load it and resume
    checkpoints = get_checkpoints(
        Path(training_config["output_path"]), training_config["pt_model_name"]
    )
    if checkpoints is not None and training_config["resume"]:
        logger.info("Found pretrained model, resuming...")
        # checkpoint = checkpoints[-1]
        model = CloudNet(**model_kwargs).load_from_checkpoint(
            checkpoints[-1],
        )
    else:
        # checkpoint = None
        model = CloudNet(**model_kwargs)

    # set cuda device if available
    model.to(model.device)

    # Get the trainer arguments from the config file
    trainer_kwargs = {
        key: lightning_trainer_config[key]
        for key in [
            "log_every_n_steps",
            "max_epochs",
            "precision",
            "check_val_every_n_epoch",
            "devices",
            "accumulate_grad_batches",
        ]
    }
    # Add the model, dataset, and loggers to the trainer arguments
    trainer_kwargs.update(
        {
            "logger": loggers,
            "callbacks": [
                ModelCheckpoint(
                    save_weights_only=False,
                    save_top_k=5,
                    mode="max",
                    save_last=True,
                    filename="ep={epoch:02d}-step={step:06d}-iou={mean_iou_val:.4f}",
                    monitor="mean_iou_val",
                    auto_insert_metric_name=False,
                    verbose=True,
                ),
                InferencePreviewClouds(
                    dataset.train_dataset,
                    tt_logger,
                    inference_freq="on_train_batch_end",
                    indices=data_config["callback_train_inds"],
                    config=config,
                ),
                InferencePreviewClouds(
                    dataset.val_dataset
                    if data_config["merge_test_into_val"]
                    else dataset.test_dataset,
                    tt_logger,
                    inference_freq="on_train_epoch_end",
                    indices=data_config["callback_val_inds"],
                    config=config,
                ),
                InferencePreviewClouds(
                    dataset.val_dataset
                    if data_config["merge_test_into_val"]
                    else dataset.test_dataset,
                    tt_logger,
                    inference_freq="on_train_end",
                    indices=data_config["callback_val_inds"]
                    if data_config["merge_test_into_val"]
                    else data_config["callback_test_inds"],
                    config=config,
                ),
                LearningRateMonitor(
                    logging_interval="step",
                    log_momentum=True,
                    log_weight_decay=True,
                ),
                TQDMProgressBar(
                    refresh_rate=1,
                    leave=True,
                ),
                EarlyStopping(
                    monitor="mean_iou_val",
                    min_delta=0.001,
                    patience=40,
                    verbose=True,
                    mode="max",
                    check_on_train_epoch_end=False,
                ),
            ],
        }
    )

    # Start training
    logger.info("Training: ⏳")
    trainer = Trainer(**trainer_kwargs)

    if training_config["tune_lr"]:
        logger.info("Tuning learning rate: ⏳")
        tuner = Tuner(trainer)
        lr_finder = tuner.lr_find(
            model,
            train_dataloaders=dataset.train_dataloader(),
            val_dataloaders=dataset.val_dataloader(),
            early_stop_threshold=5.0,
            min_lr=1e-6,
            max_lr=1e-1,
            num_training=100,
            mode="linear",
            update_attr=True,
        )
        new_lr = lr_finder.suggestion()
        logger.info(f"New learning rate: {new_lr}")
        model.hparams.learning_rate = new_lr

    try:
        trainer.fit(
            model,
            train_dataloaders=dataset.train_dataloader(),
            val_dataloaders=dataset.val_dataloader(),
        )
    except Exception as e:
        logger.error("Training failed: ❌")
        logger.error(f"Error: {e}")
        return None
    logger.info("Training: ✓")

    # Test the model on the test dataset
    if not data_config["merge_test_into_val"]:
        logger.info("Testing: ⏳")
        test_results = trainer.test(dataloaders=dataset.test_dataloader())
        logger.info("Testing: ✓")

        logger.info("Saving results: ⏳")
        # Save the test_results dict to a file
        with open(output_path_subdir / "test_results.json", "w") as f:
            json.dump(test_results, f, indent=4)
        # check if the file was saved
        if not os.path.exists(output_path_subdir / "test_results.json"):
            logger.error("Test results not saved: ❌")
        else:
            logger.info("Test results saved: ✓")

    logger.info("Saving tensorboard logs: ⏳")
    # Read tensorboard logs
    reader = SummaryReader(log_path=str(output_path_subdir))
    df = reader.scalars
    df.to_csv(output_path_subdir / "tbparse_scalars.csv", index=False)
    logger.info("Tensorboard logs saved: ✓")

    return model


if __name__ == "__main__":
    import getpass
    import json
    import time

    train_configs_dir = f"/home/vito/{getpass.getuser()}/configs/train_configs"
    config_fn = sorted(Path(train_configs_dir).glob("*.json"), key=os.path.getctime)[-1]

    with open(config_fn, "r") as f:
        config = json.load(f)

    logger.debug(f"Config loaded from {config_fn}")
    logger.debug(
        f"Starting training of model {config['training_config']['pt_model_name']}"
    )

    start_time = time.perf_counter()
    train_cloudnet(config)
    elapsed_time = time.perf_counter() - start_time

    elapsed_time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
    logger.info(f"Training completed in {elapsed_time_str}")
    logger.info("Process completed: ✓")
