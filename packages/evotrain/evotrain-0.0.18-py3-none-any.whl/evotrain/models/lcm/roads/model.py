import pytorch_lightning as pl
import torch
from torch.optim.lr_scheduler import (
    CosineAnnealingLR,
    CosineAnnealingWarmRestarts,
    CyclicLR,
    ReduceLROnPlateau,
    StepLR,
)
from loguru import logger
from evotrain.models.lcm.roads.dataset import NET_LABELS


class Net(pl.LightningModule):
    def __init__(
        self,
        architecture: str = "LcmUnet",
        bands: list = None,
        bands_head: list = None,
        bands_aux: list = None,
        backbone: str = "resnet50",
        encoder_depth: int = 5,
        loss: str = "mse",
        activation: str = "sigmoid",
        activation_conv: str = "relu",
        learning_rate: float = 1e-3,
        classes_weights=None,
        head_filters_settings=None,
        mlp_hidden_layers=(400, 300, 200, 100, 50),
        dropout_prob=0.2,
        scheduler=None,
        scheduler_params=None,
        optimizer=None,
        optimizer_weight_decay=None,
        binary_osmroads_threshold=0.25,
        binary_pos_weight=None,  # Added positive weight for binary case
    ):
        super().__init__()

        in_head_channels = 0
        if "latlon" in bands_head:
            in_head_channels += 3
        if "meteo" in bands_head:
            in_head_channels += 6

        self.hparams.update(
            {
                "architecture": architecture,
                "in_channels": len(bands),
                "classes": NET_LABELS,
                "backbone": backbone,
                "loss": loss,
                "activation": activation,
                "activation_conv": activation_conv,
                "learning_rate": learning_rate,
                "bands": bands,
                "bands_head": bands_head,
                "scheduler": scheduler,
                "optimizer": optimizer,
                "optimizer_weight_decay": optimizer_weight_decay,
                "scheduler_params": scheduler_params,
                "classes_weights": classes_weights,
                "in_head_channels": in_head_channels,
                "head_filters_settings": head_filters_settings,
                "mlp_hidden_layers": mlp_hidden_layers,
                "dropout_prob": dropout_prob,
                "encoder_depth": encoder_depth,
                "pos_weight": binary_pos_weight,  # Added to hparams
            }
        )

        self.save_hyperparameters(self.hparams)
        self.model = self.load_architecture(architecture=architecture)

        self._loss = self.select_loss(loss)

        self._classes_weights = classes_weights
        self._binary_pos_weight = binary_pos_weight  # Store positive weight

        self.num_classes = len(NET_LABELS)

        # device specific tensors
        self._classes_weights_tensor = None
        self._binary_pos_weight_tensor = None  # New tensor for binary weighting
        self.val_true_positives = None
        self.val_false_positives = None
        self.val_false_negatives = None

        # binary mode
        self.binary = len(NET_LABELS) == 1
        self.binary_osmroads_threshold = binary_osmroads_threshold

    def select_loss(self, loss_name):
        if loss_name == "mse":
            return torch.nn.MSELoss(reduction="none")
        elif loss_name == "ce":
            return torch.nn.CrossEntropyLoss(reduction="none")
        elif loss_name == "bce":  # Added binary cross entropy option
            return torch.nn.BCELoss(reduction="none")
        elif loss_name == "bce_with_logits":  # Added BCE with logits option
            # pos_weight will be applied in loss() method
            return torch.nn.BCEWithLogitsLoss(reduction="none")
        else:
            raise ValueError(f"Unknown loss: {loss_name}")

    def load_architecture(self, architecture):
        logger.info(f"Loading architecture: {architecture}")
        if architecture.startswith("LcmUnet"):
            if architecture == "LcmUnet":
                from evotrain.models.lcm.roads.arch import LcmUnet as Arch
            elif architecture == "LcmUnetV2":
                from evotrain.models.lcm.roads.arch import LcmUnetV2 as Arch
            return Arch(
                encoder_name=self.hparams.backbone,
                encoder_depth=self.hparams.encoder_depth,
                in_channels=self.hparams.in_channels,
                in_head_channels=self.hparams.in_head_channels,
                classes=len(NET_LABELS),
                activation=self.hparams.activation,
                activation_conv=self.hparams.activation_conv,
                head_filters_settings=self.hparams.head_filters_settings,
                mlp_hidden_layers=self.hparams.mlp_hidden_layers,
                dropout_prob=self.hparams.dropout_prob,
            )
        elif architecture.startswith("DualEncoderLcmUnet"):
            if architecture == "DualEncoderLcmUnet":
                from evotrain.models.lcm.roads.arch import DualEncoderLcmUnet as Arch
            elif architecture == "DualEncoderLcmUnetV2":
                from evotrain.models.lcm.roads.arch import DualEncoderLcmUnetV2 as Arch
            return Arch(
                encoder1_name=self.hparams.backbone,
                encoder2_name=self.hparams.backbone,
                encoder_depth=self.hparams.encoder_depth,
                in_channels1=20,
                in_channels2=16,
                in_head_channels=self.hparams.in_head_channels,
                classes=len(NET_LABELS),
                activation=self.hparams.activation,
                activation_conv=self.hparams.activation_conv,
                head_filters_settings=self.hparams.head_filters_settings,
                mlp_hidden_layers=self.hparams.mlp_hidden_layers,
                dropout_prob=self.hparams.dropout_prob,
            )
        else:
            raise ValueError(f"Unknown architecture: {architecture}")

    def configure_optimizers(self):
        optimizer_name = self.hparams.optimizer
        scheduler_name = self.hparams.scheduler

        # Define the optimizer
        if optimizer_name == "adam":
            opt = torch.optim.Adam(
                [
                    dict(
                        params=self.model.parameters(),
                        lr=self.hparams.learning_rate,
                        betas=(0.9, 0.999),
                        eps=1e-08,
                        weight_decay=self.hparams.optimizer_weight_decay,
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
                        weight_decay=self.hparams.optimizer_weight_decay,
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
                        weight_decay=self.hparams.optimizer_weight_decay,
                        amsgrad=True,
                    )
                ]
            )
        else:
            raise ValueError("Unknown optimizer")

        # Define the scheduler
        sched_params = self.hparams.scheduler_params
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

    def classes_weights(self, classes_weights_dict):
        weights = torch.tensor(
            [classes_weights_dict.get(k, 1) for k in self.hparams.classes]
        )
        # Expand the weights to shape (1, num_classes, 1, 1) for broadcasting
        weights = weights.view(1, len(self.hparams.classes), 1, 1)
        return weights

    def loss(self, y_pred, y):
        # Check if we're in binary mode
        if self.binary:
            if self.hparams.loss == "bce_with_logits":
                # For BCEWithLogitsLoss, we need to apply pos_weight manually
                if self._binary_pos_weight_tensor is not None:
                    # Scale positive errors by pos_weight
                    pos_mask = (y > 0).float()
                    neg_mask = (y <= 0).float()

                    # Calculate BCE loss
                    unreduced = self._loss(y_pred, y)

                    # Apply weighting
                    weighted_loss = unreduced * (
                        pos_mask * self._binary_pos_weight_tensor + neg_mask
                    )
                    return weighted_loss.mean()
                else:
                    # No pos_weight, just calculate normal BCE loss
                    unreduced = self._loss(y_pred, y)
                    return unreduced.mean()
            else:
                # For other losses in binary mode, use pos_weight or class_weights if available
                unreduced = self._loss(y_pred, y)
                if self._binary_pos_weight_tensor is not None:
                    # Apply pixel-wise weighting based on target values
                    pos_mask = (y > 0).float()
                    neg_mask = (y <= 0).float()
                    weights = pos_mask * self._binary_pos_weight_tensor + neg_mask
                    unreduced = unreduced * weights
                elif self._classes_weights_tensor is not None:
                    # If no pos_weight but classes_weights is available
                    unreduced = unreduced * self._classes_weights_tensor

                return unreduced.mean()
        else:
            # Multi-class mode
            unreduced = self._loss(y_pred, y) * self._classes_weights_tensor
            unreduced = unreduced.sum(dim=1)
            return unreduced.mean()

    def forward(self, x, x_head):
        return self.model.forward(x, x_head)

    def predict(self, x, x_head):
        return self.model.predict(x, x_head)

    def training_step(self, batch, batch_idx):
        x, x_head, y = batch
        y_pred = self.model(x, x_head)
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

    def on_train_start(self):
        # Initialize device-aware tensors at the beginning of training
        device = self.device

        # Initialize the class weights tensor if not already done
        if self._classes_weights_tensor is None and self._classes_weights:
            self._classes_weights_tensor = self.classes_weights(
                self._classes_weights
            ).to(device)

        # Initialize pos_weight tensor for binary case
        if (
            self.binary
            and self._binary_pos_weight is not None
            and self._binary_pos_weight_tensor is None
        ):
            self._binary_pos_weight_tensor = torch.tensor(
                self._binary_pos_weight, device=device
            )

        # Initialize metrics accumulators
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

    def on_validation_start(self):
        return self.on_train_start()

    def validation_step(self, batch, batch_idx):
        x, x_head, y = batch
        y_pred = self.model(x, x_head)

        # Calculate and log validation loss
        val_loss = self.loss(y_pred, y)
        self.log("val_loss", val_loss, on_step=False, on_epoch=True, prog_bar=True)

        # Calculate metrics for each class
        for i, lab in enumerate(NET_LABELS):
            tp, fp, fn = get_label_stats(
                y_pred,
                y,
                i,
                binary=self.binary,
                binary_threshold=self.binary_osmroads_threshold,
            )

            # Update the running counts
            self.val_true_positives[i] += tp
            self.val_false_positives[i] += fp
            self.val_false_negatives[i] += fn

    def on_validation_epoch_end(self):
        # Calculate IoU metrics
        mean_iou, iou_per_class = self.calculate_iou(binary=self.binary)

        # Log the mean IoU and per-class IoU
        self.log("mean_iou_val", mean_iou, prog_bar=True)
        for lab_i, iou in enumerate(iou_per_class):
            self.log(f"class_iou_{NET_LABELS[lab_i]}_val", iou)

        # Reset accumulators after each epoch
        self.val_true_positives.zero_()
        self.val_false_positives.zero_()
        self.val_false_negatives.zero_()

    def calculate_iou(self, binary=False):
        if binary:
            return self.calculate_iou_binary()
        else:
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
                    # Use class weight if available, otherwise use 1.0
                    weight = 1.0
                    if self._classes_weights_tensor is not None:
                        weight = self._classes_weights_tensor[0, lab_i, 0, 0]

                    weighted_iou_sum += iou * weight
                    weight_sum += weight
                    iou_per_class.append(iou.item())
                else:
                    iou_per_class.append(
                        0.0
                    )  # Use 0 instead of NaN for better handling

            # Calculate the weighted mean IoU
            mean_iou = (weighted_iou_sum / weight_sum).item() if weight_sum > 0 else 0.0

        return mean_iou, iou_per_class

    def calculate_iou_binary(self):
        # Calculate IoU for binary classification with possible weighting
        tp = self.val_true_positives[0]
        fp = self.val_false_positives[0]
        fn = self.val_false_negatives[0]
        union = tp + fp + fn

        if union > 0:
            iou = tp / union

            # Apply weighting if available (either from pos_weight or class_weights)
            weight = 1.0
            if self._binary_pos_weight_tensor is not None:
                weight = self._binary_pos_weight_tensor.item()
            elif self._classes_weights_tensor is not None:
                weight = self._classes_weights_tensor[0, 0, 0, 0].item()

            # Return weighted IoU and list with single IoU
            mean_iou = (iou * weight).item()
            return mean_iou, [(iou * weight).item()]
        else:
            return 0.0, [0.0]  # Use 0 instead of NaN for better handling


def get_label_stats(outputs, targets, label, binary=False, binary_threshold=0.25):
    if binary:
        # Convert probabilities to binary predictions
        preds = (outputs > binary_threshold).int()
        true_labels = (targets > binary_threshold).int()

        # Accumulate true positives, false positives, and false negatives
        tp = (preds & true_labels).sum()
        fp = (preds & ~true_labels).sum()
        fn = (~preds & true_labels).sum()

    else:
        # Convert predictions and targets to class labels
        preds = torch.argmax(outputs, dim=1)
        true_labels = torch.argmax(targets, dim=1)

        # Accumulate true positives, false positives, and false negatives
        tp = ((preds == label) & (true_labels == label)).sum()
        fp = ((preds == label) & (true_labels != label)).sum()
        fn = ((preds != label) & (true_labels == label)).sum()

    return tp, fp, fn
