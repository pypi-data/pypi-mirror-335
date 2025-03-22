from pathlib import Path

import pytorch_lightning as pl
import torch
from callbacks import InferencePreview
from dataset import get_train_val_dataloaders
from loguru import logger
from pytorch_lightning.callbacks import LearningRateMonitor, ModelCheckpoint
from pytorch_lightning.loggers import TensorBoardLogger

from evotrain.models.lsc10.v14.model import Net

torch.set_float32_matmul_precision("medium")
from loguru import logger

logger.info(f'CUDA available to torch: {torch.cuda.is_available()}')

def get_checkpoints(folder, model_name):
    """
    Get path model checkpoints
    """
    folder = Path(folder) / model_name

    if not folder.is_dir():
        return None

    folder = sorted(list(folder.iterdir()))[-1] / "checkpoints"

    if not folder.is_dir():
        return None

    checkpoints = sorted(list(folder.iterdir()))

    if len(checkpoints) == 0:
        return None

    return checkpoints


def train(config):
    trainer_config = config["trainer"]
    dataloader_config = config["dataloader"]
    model_config = config["model"]

    bands = model_config["bands"]
    config["bands"] = bands
    dataloader_config["bands"] = bands

    output_path = Path(trainer_config["output_path"])
    model_name = trainer_config["model_name"]
    max_epochs = trainer_config["max_epochs"]
    resume = trainer_config["resume"]
    accumulate_grad_batches = trainer_config.get("accumulate_grad_batches", 1)

    train_loader, val_loader, _, val_dataset = get_train_val_dataloaders(
        config
    )

    # logger
    tt_logger = TensorBoardLogger(
        save_dir=str(output_path),
        name=model_name,
    )

    logger.info("Checking for pre-trained checkpoint")
    # Check whether pretrained model exists. If yes, load it and resume
    checkpoints = get_checkpoints(output_path, model_name)
    if checkpoints is not None and resume:
        logger.info("Found pretrained model, resuming...")
        checkpoint = checkpoints[-1]
        logger.info(f"Loading model from {checkpoint}")
        logger.info(f"Model config: {model_config}")
        model = Net.load_from_checkpoint(
            checkpoints[-1],
        )#(**model_config)
    else:
        checkpoint = None
        model = Net(**model_config)

    # set cuda device if available
    # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    # model.to(device)
    # cuda = torch.cuda.is_available()

    # devices = gpus if cuda else 0
    # accelerator = "gpu" if cuda else "cpu"
    # strategy = "ddp" if ((gpus > 1) & cuda) else None
    devices = "auto"
    accelerator = "auto"
    strategy = "auto"

    trainer_kwargs = dict(
        max_epochs=max_epochs,
        precision=trainer_config.get("precision", 16),
        callbacks=[
            ModelCheckpoint(
                monitor="val_mIoU_cover",
                mode="max",
                save_weights_only=False,
                save_top_k=3,
                save_last=True,
                filename="epoch={epoch}-step={step}-iou={val_mIoU_cover:.4f}",
                auto_insert_metric_name=False,
            ),
            InferencePreview(
                val_dataset,
                tt_logger,
                val_ids=12,
                years=[2020],
                every_n_steps=250,
                rgb_ids=[2, 1, 0],
            ),
            LearningRateMonitor("epoch"),
        ],
        logger=tt_logger,
        devices=devices,
        accelerator=accelerator,
        strategy=strategy,
        accumulate_grad_batches=accumulate_grad_batches,
    )

    logger.info("Training starting")
    trainer = pl.Trainer(**trainer_kwargs)
    trainer.fit(model, train_loader, val_loader, ckpt_path=checkpoint)

    logger.info("Training completed")
    return model


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("config_fn", type=str)
    args = parser.parse_args()

    with open(args.config_fn, "r") as f:
        config = json.load(f)

    logger.info(f"Config loaded from {args.config_fn}")
    logger.info(
        f"Starting training of model {config['trainer']['model_name']}"
    )

    train(config)
