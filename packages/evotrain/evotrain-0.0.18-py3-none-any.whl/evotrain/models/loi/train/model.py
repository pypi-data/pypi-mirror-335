from pathlib import Path

import lightning as L
import segmentation_models_pytorch as smp
import torch
from loguru import logger
from segmentation_models_pytorch import losses, utils
from torch.distributed import ReduceOp, all_reduce, is_initialized
from torch.optim.lr_scheduler import (
    CosineAnnealingLR,
    CosineAnnealingWarmRestarts,
    CyclicLR,
    ReduceLROnPlateau,
    StepLR,
)

from evotrain.models.loi.train.metrics import (
    get_label_stats,
)

from .architectures import CloudArchV1, CloudArchV2


class CloudNet(L.LightningModule):
    def __init__(
        self,
        activation: str = "softmax2d",
        activation_conv: str = "relu",
        arch: str = "Unet",
        architecture_version: str = "v3",
        backbone: str = "mobilenet_v2",
        bands: list = [],
        bands_head: list = [],
        classes: list = [],
        class_weights_list: list = [],
        config: dict = dict(),
        dropout_rate: float = 0.0,
        encoder_depth: int = 5,
        head_filters_settings: list = [],
        label_smoothing_factor: float = 0.1,
        learning_rate: float = 1e-3,
        loss: str = "dice",
        loss2: str = "",
        mlp_hidden_layers=(256, 128, 64, 32),
        optimizer: str = "adam",
        sample_weights: list = [],
        scheduler: str = "steplr",
        softseg: bool = False,
        device: str = "cuda",
    ):
        super().__init__()
        self.config = config
        self.architecture_version = architecture_version
        self.softseg = softseg
        # self.learning_rate = learning_rate
        self.hparams.update(
            {
                "activation": activation,
                "arch": arch,
                "backbone": backbone,
                "bands": bands,
                "bands_head": bands_head,
                "classes": classes,
                "in_channels": len(bands),
                "learning_rate": learning_rate,
                "loss": loss,
                "loss2": loss2,
                "optimizer": optimizer,
                "scheduler": scheduler,
            }
        )
        self.save_hyperparameters(self.hparams)
        self.encoder_depth = encoder_depth
        self.head_filters_settings = head_filters_settings
        self.mlp_hidden_layers = mlp_hidden_layers
        self.dropout_rate = dropout_rate
        self.model = self.load_architecture(name=self.architecture_version)
        self.class_weights_list = class_weights_list
        # Make class_weights_dict which is mapping classes to class_weights_list
        self.class_weights_dict = dict(zip(classes, class_weights_list))
        self.sample_weights = sample_weights
        self.label_smoothing_factor = label_smoothing_factor
        if self.hparams.loss == "ce":
            assert len(self.class_weights) == len(self.hparams.classes), (
                "class_weights must have the same length as classes"
            )
            if len(self.sample_weights):
                assert len(self.sample_weights) == 2, (
                    f"sample_weights must have length 2 (weights for 'high', weights for other) but got {len(self.sample_weights)}"
                )
                assert all([isinstance(w, float) for w in self.sample_weights]), (
                    "sample_weights must be floats"
                )
                assert all([0 <= w <= 1 for w in self.sample_weights]), (
                    "sample_weights must be between 0 and 1"
                )

        self.num_classes = len(self.hparams.classes)
        assert classes == list(range(self.num_classes)), "Classes must be 0, 1, 2, ..."

        self._loss = torch.nn.MSELoss(reduction="none")

        # Device specific tensors
        self._class_weights_tensor = None
        self.val_true_positives = None
        self.val_false_positives = None
        self.val_false_negatives = None

    def get_class_weights_tensor(self, classes_weights_dict):
        weights = torch.tensor(
            [classes_weights_dict.get(k, 1) for k in self.hparams.classes]
        )
        # Expand the weights to shape (1, 9, 1, 1) for broadcasting
        weights = weights.view(1, len(self.hparams.classes), 1, 1)
        return weights

    def load_architecture(self, name="v1"):
        in_head_channels = 0
        if "latlon" in self.hparams.bands_head:
            in_head_channels += 3
        if "meteo" in self.hparams.bands_head:
            in_head_channels += 6
        if "seasonal" in self.hparams.bands_head:
            in_head_channels += 2

        if name.startswith("LcmUnet"):
            if name == "LcmUnet":
                from evotrain.models.lcm10.v11.arch import LcmUnet as Arch
            elif name == "LcmUnetV2":
                from evotrain.models.lcm10.v11.arch import LcmUnetV2 as Arch
            else:
                raise ValueError(f"Unknown architecture: {name}")
            return Arch(
                encoder_name=self.hparams.backbone,
                encoder_depth=self.encoder_depth,
                in_channels=len(self.hparams.bands),
                in_head_channels=in_head_channels,
                classes=len(self.hparams.classes),
                activation=self.hparams.activation,
                head_filters_settings=self.head_filters_settings,
                mlp_hidden_layers=self.mlp_hidden_layers,
                dropout_prob=self.dropout_rate,
            )
        elif name == "CloudArchV1":
            return CloudArchV1(
                encoder_name=self.hparams.backbone,
                in_channels=len(self.hparams.bands) + in_head_channels,
                classes=len(self.hparams.classes),
                activation=self.hparams.activation,
            )
        elif name == "CloudArchV2":
            return CloudArchV2(
                encoder_name=self.hparams.backbone,
                encoder_depth=self.encoder_depth,
                in_channels=len(self.hparams.bands),
                in_head_channels=in_head_channels,
                classes=len(self.hparams.classes),
                activation=self.hparams.activation,
                head_filters_settings=self.head_filters_settings,
                mlp_hidden_layers=self.mlp_hidden_layers,
                dropout_prob=self.dropout_rate,
            )

        else:
            raise ValueError(f"Unknown architecture: {name}")

    def load_loss(self, loss=""):
        loss_functions = {
            "dice": losses.DiceLoss(mode="multilabel"),
            "lovasz": losses.LovaszLoss(mode="multilabel"),
            "ce": utils.losses.CrossEntropyLoss(
                weight=torch.tensor(self.class_weights), reduction="none"
            ),
            "focal": losses.FocalLoss(mode="multilabel"),
            "tversky": losses.TverskyLoss(mode="multilabel"),
            "jaccard": losses.JaccardLoss(mode="multilabel"),
            "mse": torch.nn.MSELoss(reduction="none"),
            "soft_bce": losses.SoftBCEWithLogitsLoss(reduction="none"),
            "soft_ce": losses.SoftCrossEntropyLoss(reduction="none"),
        }

        return loss_functions[loss]

    def configure_optimizers(self):
        optimizer_name = self.hparams.optimizer
        scheduler_name = self.hparams.scheduler
        assert scheduler_name == self.config["dl_model_config"]["scheduler"], (
            "Scheduler name in the config file does not match the scheduler name in the model"
        )
        assert optimizer_name == self.config["dl_model_config"]["optimizer"], (
            "Optimizer name in the config file does not match the optimizer name in the model"
        )

        # Define the optimizer
        if optimizer_name == "adam":
            opt = torch.optim.Adam(
                [
                    dict(
                        params=self.model.parameters(),
                        lr=self.hparams.learning_rate,
                        betas=(0.9, 0.999),
                        eps=1e-08,
                        weight_decay=self.config["dl_model_config"][
                            "optimizer_weight_decay"
                        ],
                        amsgrad=True,
                    )
                ]
            )
        elif optimizer_name == "sgd":
            opt = torch.optim.SGD(
                [
                    dict(
                        params=self.model.parameters(),
                        lr=self.hparams.learning_rate,
                        momentum=0.9,
                        weight_decay=self.config["dl_model_config"][
                            "optimizer_weight_decay"
                        ],
                    )
                ]
            )
        elif optimizer_name == "adamw":
            opt = torch.optim.AdamW(
                [
                    dict(
                        params=self.model.parameters(),
                        lr=self.hparams.learning_rate,
                        betas=(0.9, 0.999),
                        eps=1e-08,
                        weight_decay=self.config["dl_model_config"][
                            "optimizer_weight_decay"
                        ],
                        amsgrad=True,
                    )
                ]
            )
        else:
            raise ValueError("Unknown optimizer")

        # Define the scheduler
        sched_params = self.config["dl_model_config"]["scheduler_params"]
        if scheduler_name == "steplr":
            scheduler = StepLR(
                opt,
                step_size=sched_params["steplr_step_size"],
                gamma=sched_params["steplr_gamma"],
            )
        elif scheduler_name == "cosine":
            scheduler = CosineAnnealingLR(
                opt,
                T_max=sched_params["cosine_T_max"],
                eta_min=sched_params["cosine_eta_min"],
                last_epoch=-1,
            )
        elif scheduler_name == "cosinewarm":
            scheduler = CosineAnnealingWarmRestarts(
                opt,
                T_0=int(sched_params["cosinewarm_T_0"]),
                T_mult=int(sched_params["cosinewarm_T_mult"]),
                eta_min=sched_params["cosinewarm_eta_min"],
                last_epoch=-1,
            )
        elif scheduler_name == "cyclic":
            scheduler = CyclicLR(
                opt,
                base_lr=sched_params["cyclic_base_lr"],
                max_lr=sched_params["cyclic_max_lr"],
                step_size_up=sched_params["cyclic_step_size_up"],
                gamma=sched_params["cyclic_gamma"],
                mode=sched_params["cyclic_mode"],
                cycle_momentum=sched_params["cyclic_cycle_momentum"],
            )
        elif scheduler_name == "plateau":
            scheduler = ReduceLROnPlateau(
                opt,
                mode="min",
                factor=sched_params["plateau_factor"],
                patience=sched_params["plateau_patience"],
                verbose=True,
                threshold=0.0001,
                threshold_mode="rel",
                cooldown=0,
                min_lr=sched_params["plateau_min_lr"],
                eps=1e-08,
            )
        elif scheduler_name == "":
            scheduler = None
        else:
            raise ValueError("Unknown scheduler")

        if scheduler is not None:
            lr_scheduler_config = {
                "scheduler": scheduler,
                "interval": "epoch",
                "monitor": "val_loss",  # for ReduceLROnPlateau
                "frequency": 1,
                "strict": True,
                "name": "lr_scheduler",
            }
            logger.info(
                f"Using scheduler: {scheduler_name} with config: \n{lr_scheduler_config} and params: \n{sched_params}"
            )
            return [opt], [lr_scheduler_config]
        else:
            return [opt]

    def forward(self, x, x_head=None):
        return self.model.forward(x, x_head)

    def predict(self, x, x_head=None):
        return self.model.predict(x, x_head)

    def on_train_start(self):
        # Initialize device-aware tensors once at the beginning of training
        device = self.device

        # Initialize the class weights tensor if not already done
        if self._class_weights_tensor is None:
            self._class_weights_tensor = self.get_class_weights_tensor(
                self.class_weights_dict or {}
            ).to(device)

        # Initialize true positives, false positives, false negatives accumulators
        if self.val_true_positives is None:
            self.val_true_positives = torch.zeros(
                self.num_classes, dtype=torch.float32, device=device
            )
            self.val_false_positives = torch.zeros(
                self.num_classes, dtype=torch.float32, device=device
            )
            self.val_false_negatives = torch.zeros(
                self.num_classes, dtype=torch.float32, device=device
            )

    def training_step(self, batch, batch_idx):
        x, y, x_head = batch
        y_pred = self.model(x, x_head)
        loss = self.loss_v3(
            y_pred,
            y,
            label_smoothing=self.label_smoothing_factor > 0,
        )

        self.log(
            "train_loss",
            loss,
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            logger=True,
            batch_size=x.size(0),
        )
        return loss

    def on_validation_start(self):
        return self.on_train_start()

    def validation_step(self, batch, batch_idx):
        return self._shared_step(batch, batch_idx)

    def test_step(self, batch, batch_idx):
        return self._shared_step(batch, batch_idx)

    def loss_v3(self, y_pred, y, label_smoothing=False):
        if label_smoothing:
            y = (
                y * (1 - self.label_smoothing_factor)
                + self.label_smoothing_factor / self.num_classes
            )

        # y for pixels that are 0s over all probs should be ignored
        mask = y.sum(dim=1) > 0
        unreduced = self._loss(y_pred, y) * self._class_weights_tensor
        unreduced = unreduced.sum(dim=1)
        unreduced[~mask] = 0
        return unreduced.mean()

    def _shared_step(self, batch, batch_idx, x_head=None):
        # Unpack the batch into inputs and targets
        x, y, x_head = batch
        y_pred = self.model(x, x_head)

        # Compute the metrics
        for i, lab in enumerate(self.hparams.classes):
            tp, fp, fn = get_label_stats(y_pred, y, i)

            # Update the running counts
            self.val_true_positives[i] += tp
            self.val_false_positives[i] += fp
            self.val_false_negatives[i] += fn

    def on_validation_epoch_end(self):
        if is_initialized():  # Only perform all_reduce if in distributed mode
            for cls in range(self.num_classes):
                all_reduce(self.val_true_positives[cls], op=ReduceOp.SUM)
                all_reduce(self.val_false_positives[cls], op=ReduceOp.SUM)
                all_reduce(self.val_false_negatives[cls], op=ReduceOp.SUM)

        # Calculate IoU per class with weights applied
        iou_per_class = []
        weighted_iou_sum = 0.0
        weight_sum = 0.0

        for lab_i in range(self.num_classes):
            tp = self.val_true_positives[lab_i]
            fp = self.val_false_positives[lab_i]
            fn = self.val_false_negatives[lab_i]
            union = tp + fp + fn
            if union > 0:
                iou = tp / union
                weight = self._class_weights_tensor[0, lab_i, 0, 0]
                weighted_iou_sum += iou * weight
                weight_sum += weight
                iou_per_class.append(iou.item())
            else:
                iou_per_class.append(float("nan"))

        # Calculate the weighted mean IoU
        mean_iou = (
            (weighted_iou_sum / weight_sum).item() if weight_sum > 0 else float("nan")
        )

        # Log the weighted mean IoU and per-class IoU
        self.log("mean_iou_val", mean_iou, prog_bar=True, sync_dist=True)
        for lab_i, iou in enumerate(iou_per_class):
            self.log(
                f"class_iou_{self.hparams.classes[lab_i]}_val",
                iou,
                sync_dist=True,
                on_step=False,
                on_epoch=True,
            )

        # Reset accumulators after each epoch
        self.val_true_positives.zero_()
        self.val_false_positives.zero_()
        self.val_false_negatives.zero_()

    def get_class_weights(self, dataloader, return_counts=False):
        from tqdm import tqdm

        # Initialize the counts tensor
        counts = torch.zeros(self.num_classes, dtype=torch.float32, device=self.device)
        # Count the number of samples for each class
        for x, y, _ in tqdm(dataloader, desc="Counting classes"):
            counts += y.sum(dim=(0, 2, 3))
        # Convert to float32 to avoid overflow
        counts = counts.float()
        # Compute the total number of samples
        total_samples = torch.sum(counts)
        # Compute the number of classes
        num_classes = len(self.hparams.classes)
        # Compute the class weights as the inverse of the class frequencies
        weights = total_samples / (num_classes * counts)
        # Normalize the weights so that they sum to the number of classes
        weights = weights * (num_classes / torch.sum(weights))

        if return_counts:
            return weights, counts
        return weights


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


def compute_metrics_smp(output, target, mode="multilabel", threshold=0.25):
    # output and target are torch tensors probs
    tp, fp, fn, tn = smp.metrics.get_stats(
        output, target.long(), mode=mode, threshold=threshold
    )

    # then compute metrics with required reduction (see metric docs)
    iou_score = smp.metrics.iou_score(tp, fp, fn, tn, reduction="micro")
    f1_score = smp.metrics.f1_score(tp, fp, fn, tn, reduction="micro")
    f2_score = smp.metrics.fbeta_score(tp, fp, fn, tn, beta=2, reduction="micro")
    accuracy = smp.metrics.accuracy(tp, fp, fn, tn, reduction="macro")
    recall = smp.metrics.recall(tp, fp, fn, tn, reduction="micro-imagewise")
    precision = smp.metrics.precision(tp, fp, fn, tn, reduction="micro")
    balanced_accuracy = smp.metrics.balanced_accuracy(tp, fp, fn, tn, reduction="macro")

    metrics = dict(
        iou_score=iou_score,
        f1_score=f1_score,
        f2_score=f2_score,
        accuracy=accuracy,
        recall=recall,
        precision=precision,
        balanced_accuracy=balanced_accuracy,
    )

    return metrics


def apply_label_smoothing(y, num_classes, label_smoothing_factor):
    """
    Applies label smoothing to the target labels.

    Args:
        y (torch.Tensor): The target labels.
        num_classes (int): The number of classes.
        label_smoothing_factor (float): The label smoothing factor.

    Returns:
        torch.Tensor: The smoothed target labels.
    """
    if label_smoothing_factor == 0:
        return y
    uniform_dist = torch.full_like(y, fill_value=1 / num_classes)
    y_smoothed = (
        1 - label_smoothing_factor
    ) * y + label_smoothing_factor * uniform_dist
    return y_smoothed
