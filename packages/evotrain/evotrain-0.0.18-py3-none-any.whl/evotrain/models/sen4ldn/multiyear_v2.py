from pathlib import Path

import pytorch_lightning as pl
import torch
from loguru import logger
from pytorch_lightning.callbacks import LearningRateMonitor, ModelCheckpoint
from pytorch_lightning.loggers import TensorBoardLogger
from segmentation_models_pytorch import losses, utils
from torch.optim.lr_scheduler import StepLR

from evotrain.labels import WORLDCOVER_LABELS
from evotrain.models.callbacks import InferencePreview
from evotrain.v2.dataloaders import get_single_patch_dataloaders

DEFAULT_TRAIN_BANDS = [
    "s2-B04-p50",
    "s2-B03-p50",
    "s2-B02-p50",
    "s2-B08-p50",
    "s2-B11-p50",
    "s2-B12-p50",
    "s2-ndvi-p10",
    "s2-ndvi-p25",
    "s2-ndvi-p50",
    "s2-ndvi-p75",
    "s2-ndvi-p90",
    "cop-DEM-alt",
    "lat",
    "lon",
]


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


def load_dataset_images(val_dataset, num=None, ids=None):
    if num is None:
        num = 10

    if ids is None:
        ids = range(num)

    return torch.stack([val_dataset[i][0] for i in ids], dim=0)


class EvoNet(pl.LightningModule):
    def __init__(
        self,
        bands: list = None,
        arch: str = "Unet",
        backbone: str = "mobilenet_v2",
        activation: str = "softmax2d",
        loss: str = "dice",
        learning_rate: float = 1e-3,
    ):
        super().__init__()
        self.hparams.update(
            {
                "in_channels": len(bands),
                "classes": WORLDCOVER_LABELS,
                "arch": arch,
                "backbone": backbone,
                "loss": loss,
                "activation": activation,
                "learning_rate": learning_rate,
                "bands": bands,
            }
        )
        self.save_hyperparameters(self.hparams)
        self.model = self.load_architecture()
        self.loss = self.load_loss()
        self.metric = utils.metrics.IoU(threshold=0.5)
        # self.optimizer, self.scheduler = self.configure_optimizers()

    def load_architecture(self):
        if self.hparams.arch == "Unet":
            from segmentation_models_pytorch import Unet as arch
        elif self.hparams.arch == "UnetPlusPlus":
            from segmentation_models_pytorch import UnetPlusPlus as arch
        elif self.hparams.arch == "Linknet":
            from segmentation_models_pytorch import Linknet as arch
        elif self.hparams.arch == "FPN":
            from segmentation_models_pytorch import FPN as arch
        elif self.hparams.arch == "PSPNet":
            from segmentation_models_pytorch import PSPNet as arch
        elif self.hparams.arch == "PAN":
            from segmentation_models_pytorch import PAN as arch
        elif self.hparams.arch == "MAnet":
            from segmentation_models_pytorch import MAnet as arch
        elif self.hparams.arch == "DeepLabV3":
            from segmentation_models_pytorch import DeepLabV3 as arch
        elif self.hparams.arch == "DeepLabV3Plus":
            from segmentation_models_pytorch import DeepLabV3Plus as arch

        else:
            raise ValueError("Uknown architecture")

        return arch(
            encoder_name=self.hparams.backbone,
            encoder_weights=None,
            classes=len(self.hparams.classes),
            activation=self.hparams.activation,
            in_channels=self.hparams.in_channels,
        )

    def load_loss(self):
        loss_functions = {
            "dice": losses.DiceLoss(mode="multilabel"),
            "lovasz": losses.LovaszLoss(mode="multilabel"),
            "ce": utils.losses.CrossEntropyLoss(),
            "focal": losses.FocalLoss(mode="multilabel"),
            "tversky": losses.TverskyLoss(mode="multilabel"),
            "softce": losses.SoftCrossEntropyLoss(),
            "jaccard": losses.JaccardLoss(mode="multilabel"),
        }

        return loss_functions[self.hparams.loss]

    def configure_optimizers(self, step_size=1):
        opt = torch.optim.Adam(
            [
                dict(
                    params=self.model.parameters(),
                    lr=self.hparams.learning_rate,
                ),
            ]
        )
        scheduler = StepLR(opt, step_size=step_size, gamma=0.965)
        return [opt], [scheduler]

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        x, y = batch
        y_pred = self.model(x)
        loss = self.loss(y_pred, y)
        self.log(
            "train_loss",
            loss,
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        y_pred = self.model(x)
        loss = self.loss(y_pred, y)
        iou_score = self.metric(y_pred, y)
        self.log(
            "iou_score", iou_score, on_step=False, on_epoch=True, prog_bar=True
        )
        self.log(
            "val_loss",
            loss,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )
        return loss


def train_evonet(
    output_path,
    model_name,
    bands=DEFAULT_TRAIN_BANDS,
    arch="Unet",
    activation="softmax2d",
    backbone="resnet101",
    loss="dice",
    learning_rate=1e-3,
    dataset_frac=1,
    train_frac=0.7,
    batch_size=50,
    val_ids=8,
    max_epochs=3,
    resume=True,
    gpus=1,
    workers=12,
    preview_every_n_steps=1000,
    flip_augmentation=True,
    locs_tag="locs_h3",
    k_factor=5,
    k_factor_jitter=2,
    lat_lon_jitter=1,
    dem_scaling=4000,
    lat_scaling=90,
    lon_scaling=180,
    cross_labels_mapping=None,
    val_check_interval=0.5,
    accumulate_grad_batches=1,
):
    logger.info("Preparing the dataloaders")
    train_loader, val_loader, train_dataset, val_dataset = (
        get_single_patch_dataloaders(
            bands=bands,
            dataset_frac=dataset_frac,
            train_frac=train_frac,
            train_batch_size=batch_size,
            val_batch_size=batch_size,
            dataloader_workers=workers,
            val_shuffle=False,
            flip_augmentation=flip_augmentation,
            locs_tag=locs_tag,
            k_factor=k_factor,
            k_factor_jitter=k_factor_jitter,
            lat_lon_jitter=lat_lon_jitter,
            dem_scaling=dem_scaling,
            lat_scaling=lat_scaling,
            lon_scaling=lon_scaling,
            cross_labels_mapping=cross_labels_mapping,
        )
    )

    # logger
    tt_logger = TensorBoardLogger(
        save_dir=str(output_path),
        name=model_name,
    )

    model_kwargs = dict(
        bands=bands,
        arch=arch,
        backbone=backbone,
        activation=activation,
        loss=loss,
        learning_rate=learning_rate,
    )

    logger.info("Checking for pre-trained checkpoint")
    # Check whether pretrained model exists. If yes, load it and resume
    checkpoints = get_checkpoints(output_path, model_name)
    if checkpoints is not None and resume:
        logger.info("Found pretrained model, resuming...")
        checkpoint = checkpoints[-1]
        model = EvoNet(**model_kwargs).load_from_checkpoint(
            checkpoints[-1],
        )
    else:
        checkpoint = None
        model = EvoNet(**model_kwargs)

    # set cuda device if available
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)

    trainer_kwargs = dict(
        max_epochs=max_epochs,
        callbacks=[
            ModelCheckpoint(
                save_weights_only=False,
                save_top_k=1,
                save_last=True,
                monitor="val_loss",
            ),
            InferencePreview(
                val_dataset,
                tt_logger,
                val_ids=val_ids,
                years=list(range(2018, 2023)),
                every_n_steps=preview_every_n_steps,
                rgb_ids=[0, 1, 2],
                augmented_scaling=True,
                augmented_scaling_params=dict(
                    k_factor=k_factor,
                    k_factor_jitter=0,  # do not jitter val ims
                    lat_lon_jitter=0,
                    dem_scaling=dem_scaling,
                    lat_scaling=lat_scaling,
                    lon_scaling=lon_scaling,
                ),
            ),
            LearningRateMonitor("epoch"),
        ],
        logger=tt_logger,
        devices=gpus,
        val_check_interval=val_check_interval,
        accumulate_grad_batches=accumulate_grad_batches,
    )

    logger.info("Training starting")
    trainer = pl.Trainer(**trainer_kwargs)
    trainer.fit(model, train_loader, val_loader, ckpt_path=checkpoint)

    logger.info("Training completed")
    return model
