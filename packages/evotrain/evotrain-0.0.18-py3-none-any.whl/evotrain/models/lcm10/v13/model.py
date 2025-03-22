import pytorch_lightning as pl
import torch
from torch.distributed import ReduceOp, all_reduce, is_initialized
from torch.optim.lr_scheduler import StepLR

from .dataset import NET_LABELS

# TODO: change imports to relative
# TODO: add scaling params to Net init and model config
# TODO: add missing params in hparams so we can check in tb while training
# TODO: add scaling_params...
# TODO: add mIoU metric for training
# TODO: add proper val loss training
# TODO: add early stopping
# TODO: split metrics to separate file
# TODO: split segmentation head in 2 heads
# TODO: modify the dataloader to only scale the DEM and let the model handle the rest


def compute_iou(preds, true_labels, num_classes=9):
    # Step 2: Flatten the predictions and true labels
    preds = preds.view(-1)  # Shape: (batch * y * x)
    true_labels = true_labels.view(-1)  # Shape: (batch * y * x)

    # Step 3: Compute IoU for each class
    iou_per_class = []
    for cls in range(num_classes):
        # True Positive (intersection)
        intersection = ((preds == cls) & (true_labels == cls)).sum().item()
        # Union (total area of both predictions and targets for this class)
        union = ((preds == cls) | (true_labels == cls)).sum().item()

        if union == 0:
            iou_per_class.append(
                float("nan")
            )  # Ignore this class if union is zero
        else:
            iou_per_class.append(intersection / union)

    # Step 4: Compute the mean IoU, ignoring NaNs
    mean_iou = torch.tensor(iou_per_class).nanmean().item()

    return mean_iou, iou_per_class


def compute_class_fraction_accuracy(preds, true_labels, num_classes=9):
    # Step 2: Calculate the fraction of each class in predictions and targets
    batch_size = preds.size(0)
    pred_fractions = torch.zeros(batch_size, num_classes, device=preds.device)
    target_fractions = torch.zeros(
        batch_size, num_classes, device=true_labels.device
    )

    for cls in range(num_classes):
        # For each batch, count pixels belonging to the current class
        pred_fractions[:, cls] = (preds == cls).float().sum(dim=(1, 2)) / (
            preds.size(1) * preds.size(2)
        )
        target_fractions[:, cls] = (true_labels == cls).float().sum(
            dim=(1, 2)
        ) / (true_labels.size(1) * true_labels.size(2))

    # Step 3: Compute class-wise absolute differences (accuracy metric)
    class_accuracies = 1 - torch.abs(
        pred_fractions - target_fractions
    )  # Shape: (batch_size, num_classes)

    # Step 4: Calculate the mean accuracy per class across the batch
    mean_class_accuracy = class_accuracies.mean(dim=0)  # Shape: (num_classes,)

    # Step 5: Calculate overall accuracy by averaging across classes and batch
    overall_accuracy = mean_class_accuracy.mean().item()

    return overall_accuracy, mean_class_accuracy


def get_label_stats(outputs, targets, label):
    # Convert predictions and targets to class labels
    preds = torch.argmax(outputs, dim=1)
    true_labels = torch.argmax(targets, dim=1)

    # Accumulate true positives, false positives, and false negatives
    tp = ((preds == label) & (true_labels == label)).sum()
    fp = ((preds == label) & (true_labels != label)).sum()
    fn = ((preds != label) & (true_labels == label)).sum()

    return tp, fp, fn


def compute_metrics(outputs, targets, num_classes=len(NET_LABELS), suffix=""):
    # Handle suffix
    suffix = f"_{suffix}" if suffix else ""

    preds = torch.argmax(outputs, dim=1)  # Shape: (batch, y, x)
    true_labels = torch.argmax(targets, dim=1)  # Shape: (batch, y, x)

    # Compute IoU and class fraction accuracy
    mean_iou, iou_per_class = compute_iou(preds, true_labels, num_classes)
    overall_accuracy, mean_class_accuracy = compute_class_fraction_accuracy(
        preds, true_labels, num_classes
    )

    # Create a dictionary of metrics
    metrics = {
        f"mean_iou{suffix}": mean_iou,
        f"overall_accuracy{suffix}": overall_accuracy,
    }

    for cls, acc in enumerate(mean_class_accuracy):
        metrics[f"class_accuracy_{NET_LABELS[cls]}{suffix}"] = acc.item()

    for cls, iou in enumerate(iou_per_class):
        metrics[f"class_iou_{NET_LABELS[cls]}{suffix}"] = iou

    return metrics


class Net(pl.LightningModule):
    def __init__(
        self,
        architecture: str = "LcmUnet",
        bands: list = None,
        bands_head: list = None,
        backbone: str = "resnet50",
        encoder_depth: int = 5,
        activation: str = "sigmoid",
        activation_conv: str = "relu",
        learning_rate: float = 1e-3,
        scheduler_step_size=1,
        scheduler_gamma=0.965,
        classes_weights=None,
        head_filters_settings=None,
        mlp_hidden_layers=(400, 300, 200, 100, 50),
        dropout_prob=0.2,
    ):
        super().__init__()

        self.hparams.update(
            {
                "architecture": architecture,
                "in_channels": len(bands),
                "classes": NET_LABELS,
                "backbone": backbone,
                "activation": activation,
                "activation_conv": activation_conv,
                "learning_rate": learning_rate,
                "bands": bands,
                "bands_head": bands_head,
                "scheduler_step_size": scheduler_step_size,
                "scheduler_gamma": scheduler_gamma,
                "classes_weights": classes_weights,
            }
        )
        in_head_channels = 0
        if "latlon" in bands_head:
            in_head_channels += 3
        if "meteo" in bands_head:
            in_head_channels += 6

        self.save_hyperparameters(self.hparams)
        Arch = self.load_architecture(architecture=architecture)
        self.model = Arch(
            encoder_name=backbone,
            encoder_depth=encoder_depth,
            in_channels=len(bands),
            in_head_channels=in_head_channels,
            classes=len(NET_LABELS),
            activation=activation,
            activation_conv=activation_conv,
            head_filters_settings=head_filters_settings,
            mlp_hidden_layers=mlp_hidden_layers,
            dropout_prob=dropout_prob,
        )

        self._loss = torch.nn.MSELoss(reduction="none")

        self._classes_weights = classes_weights

        self.num_classes = len(NET_LABELS)

        # device specific tensors
        self._classes_weights_tensor = None
        self.val_true_positives = None
        self.val_false_positives = None
        self.val_false_negatives = None

    def load_architecture(self, architecture):
        if architecture == "LcmUnet":
            from evotrain.models.lcm10.v11.arch import LcmUnet as Arch
        elif architecture == "LcmUnetV2":
            from evotrain.models.lcm10.v11.arch import LcmUnetV2 as Arch
        else:
            raise ValueError(f"Unknown architecture: {architecture}")
        return Arch

    def configure_optimizers(self):
        opt = torch.optim.Adam(
            [
                dict(
                    params=self.model.parameters(),
                    lr=self.hparams.learning_rate,
                ),
            ]
        )
        scheduler = StepLR(
            opt,
            step_size=self.hparams.scheduler_step_size,
            gamma=self.hparams.scheduler_gamma,
        )
        return [opt], [scheduler]

    def classes_weights(self, classes_weights_dict):
        weights = torch.tensor(
            [classes_weights_dict.get(k, 1) for k in self.hparams.classes]
        )
        # Expand the weights to shape (1, 9, 1, 1) for broadcasting
        weights = weights.view(1, len(self.hparams.classes), 1, 1)
        return weights

    def loss(self, y_pred, y):
        # y for pixels that are 0s over all probs should be ignored
        mask = y.sum(dim=1) > 0
        unreduced = self._loss(y_pred, y) * self._classes_weights_tensor
        unreduced = unreduced.sum(dim=1)
        unreduced[~mask] = 0
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

    # def validation_step(self, batch, batch_idx):
    #     x, x_head, y = batch
    #     y_pred = self.model(x, x_head)

    #     metrics = compute_metrics(y_pred, y, suffix="val")

    #     for k, v in metrics.items():
    #         prog_bar = True if "mean_iou" in k else False
    #         self.log(
    #             k,
    #             v,
    #             on_step=False,
    #             on_epoch=True,
    #             prog_bar=prog_bar,
    #             logger=True,
    #             sync_dist=True,
    #         )
    def on_train_start(self):
        # Initialize device-aware tensors once at the beginning of training
        device = self.device

        # Initialize the class weights tensor if not already done
        if self._classes_weights_tensor is None:
            self._classes_weights_tensor = self.classes_weights(
                self._classes_weights or {}
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

    def on_validation_start(self):
        return self.on_train_start()

    # def training_step(self, batch, batch_idx):
    #     x, x_head, y = batch
    #     y_pred = self.model(x, x_head)
    #     loss = self.loss(y_pred, y)

    #     # Accumulate the loss for epoch-end logging
    #     self.log(
    #         "train_loss_step",
    #         loss,
    #         on_step=True,
    #         prog_bar=True,
    #         logger=True,
    #         sync_dist=True,
    #     )
    #     return loss

    # def on_train_epoch_end(self):
    #     # Aggregate and average the loss across all GPUs
    #     avg_loss = torch.tensor(
    #         [self.trainer.callback_metrics["train_loss_step"].mean().item()]
    #     )

    #     if is_initialized():  # Ensure distributed training is active
    #         all_reduce(avg_loss, op=ReduceOp.SUM)
    #         avg_loss /= torch.distributed.get_world_size()

    #     # Log the synchronized train loss for the entire epoch
    #     self.log(
    #         "train_loss_epoch",
    #         avg_loss.item(),
    #         prog_bar=True,
    #         logger=True,
    #         sync_dist=True,
    #     )

    def validation_step(self, batch, batch_idx):
        x, x_head, y = batch
        y_pred = self.model(x, x_head)

        for i, lab in enumerate(NET_LABELS):
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
                weight = self._classes_weights_tensor[0, lab_i, 0, 0]
                weighted_iou_sum += iou * weight
                weight_sum += weight
                iou_per_class.append(iou.item())
            else:
                iou_per_class.append(float("nan"))

        # Calculate the weighted mean IoU
        mean_iou = (
            (weighted_iou_sum / weight_sum).item()
            if weight_sum > 0
            else float("nan")
        )

        # Log the weighted mean IoU and per-class IoU
        self.log("mean_iou_val", mean_iou, prog_bar=True, sync_dist=True)
        for lab_i, iou in enumerate(iou_per_class):
            self.log(f"class_iou_{NET_LABELS[lab_i]}_val", iou, sync_dist=True)

        # Reset accumulators after each epoch
        self.val_true_positives.zero_()
        self.val_false_positives.zero_()
        self.val_false_negatives.zero_()


if __name__ == "__main__":
    import torch

    def test_compute_multilabel_metrics():
        # Sample data with batch size of 2, 3 channels (multilabel), and 4x4 spatial dimensions
        # `output` represents model predictions with probabilities
        output = torch.rand(32, 9, 128, 128)

        # `target` with all-zero channels in some areas, simulating ignored pixels
        target = torch.rand(32, 9, 128, 128)

        # Run the metrics function
        metrics = compute_metrics(output, target, suffix="test")

        # Print metrics
        print("Computed Metrics:")
        for metric_name, value in metrics.items():
            print(f"{metric_name}: {value:.4f}")

    # Run the test
    test_compute_multilabel_metrics()
