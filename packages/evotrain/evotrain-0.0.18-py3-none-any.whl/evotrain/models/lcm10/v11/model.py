import pytorch_lightning as pl
import torch
from torch.optim.lr_scheduler import StepLR

from evotrain.models.lcm10.v11.dataset import NET_LABELS


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
        mlp_hidden_layers=(300, 200, 200, 100),
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
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self._classes_weights_tensor = self.classes_weights(
            classes_weights or {}
        ).to(device)
        self._classes_weights = classes_weights

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

    def validation_step(self, batch, batch_idx):
        x, x_head, y = batch
        y_pred = self.model(x, x_head)

        metrics = compute_metrics(y_pred, y, suffix="val")

        for k, v in metrics.items():
            prog_bar = True if "mean_iou" in k else False
            self.log(
                k,
                v,
                on_step=False,
                on_epoch=True,
                prog_bar=prog_bar,
                logger=True,
                sync_dist=True,
            )


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
