import pytorch_lightning as pl
import torch
from torch.optim.lr_scheduler import StepLR

from evotrain.models.evonet import EvoNet

# TODO: add proper val loss training


def get_label_stats(outputs, targets, label_idx, mask=None, min_threshold=0.5):
    # Convert predictions and targets to class labels
    preds = torch.argmax(outputs, dim=1)
    true_labels = torch.argmax(targets, dim=1)

    # Apply mask if provided
    if mask is not None:
        mask = mask.squeeze(1)  # Remove the singleton channel dimension
        preds = preds[mask > min_threshold]
        true_labels = true_labels[mask > min_threshold]

    # Accumulate true positives, false positives, and false negatives
    tp = ((preds == label_idx) & (true_labels == label_idx)).sum()
    fp = ((preds == label_idx) & (true_labels != label_idx)).sum()
    fn = ((preds != label_idx) & (true_labels == label_idx)).sum()

    return tp, fp, fn


class Net(pl.LightningModule):
    def __init__(
        self,
        **evonet_kwargs,
    ):
        super().__init__()

        self.hparams.update(evonet_kwargs)

        self.save_hyperparameters(self.hparams)

        self._mse = torch.nn.MSELoss(reduction="none")

        self.loss_weight_cover = evonet_kwargs.get("loss_weight_cover", 1)
        self.loss_weight_occlusion = evonet_kwargs.get(
            "loss_weight_occlusion", 1
        )
        self.loss_weight_ecosystems = evonet_kwargs.get(
            "loss_weight_ecosystems", 1
        )

        classes_dict = evonet_kwargs["classes"]
        self.classes_dict = classes_dict

        self.classes_cover_ids = list(classes_dict["cover"].keys())
        self.classes_occlusion_ids = list(classes_dict["occlusion"].keys())
        self.classes_ecosystems_ids = list(classes_dict["ecosystems"].keys())
        self.classes_ids = (
            self.classes_cover_ids
            + self.classes_occlusion_ids
            + self.classes_ecosystems_ids
        )

        self.num_classes_cover = len(self.classes_cover_ids)
        self.num_classes_occlusion = len(self.classes_occlusion_ids)
        self.num_classes_ecosystems = len(self.classes_ecosystems_ids)
        self.num_classes = (
            self.num_classes_cover
            + self.num_classes_occlusion
            + self.num_classes_ecosystems
        )

        # device specific tensors
        self._classes_weights_tensor = None

        self._labels_types = ["cover", "occlusion", "ecosystems"]
        self._iou_accumulators_keys = [
            "true_positives",
            "false_positives",
            "false_negatives",
        ]
        self._iou_accumulators = {
            tag: {key: None for key in self._iou_accumulators_keys}
            for tag in self._labels_types
        }

        # update evonet_kwargs
        evonet_kwargs["out_channels"] = self.num_classes
        evonet_kwargs["activation_spatial"] = "sigmoid"
        evonet_kwargs["activation_mlp"] = "identity"

        self.evonet = EvoNet(**evonet_kwargs)

    def _slice_cover(self, x):
        return x[:, : self.num_classes_cover, ...]

    def _slice_occlusion(self, x):
        start = self.num_classes_cover
        end = start + self.num_classes_occlusion
        return x[:, start:end, ...]

    def _slice_ecosystems(self, x):
        start = self.num_classes_cover + self.num_classes_occlusion
        end = start + self.num_classes_ecosystems
        return x[:, start:end, ...]

    def _get_max_pixel_weight_mask(self, y_weights):
        mask, _ = torch.max(y_weights, dim=1, keepdim=True)
        return mask

    def _reset_accumulators(self):
        for tag in self._labels_types:
            for key in self._iou_accumulators_keys:
                self._iou_accumulators[tag][key].zero_()

    def configure_optimizers(self):
        opt = torch.optim.Adam(
            [
                dict(
                    params=self.evonet.parameters(),
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

    def get_classes_weights_tensor(self, classes_weights_dict):
        weights = torch.tensor(
            [classes_weights_dict.get(k, 1) for k in self.classes]
        )
        # Expand the weights to shape (1, classes, 1, 1) for broadcasting
        weights = weights.view(1, self.num_classes, 1, 1)
        return weights

    def _loss(self, y_pred, y, y_weight, slicer=None):
        # y_weight_mask has shape (batch, classes, y, x)
        # the weight is generally 1, but can be set to 0 to ignore pixels or
        # more than 1 to give more importance to some pixels (e.g. roads...)

        if slicer is not None:
            y_pred = slicer(y_pred)
            y = slicer(y)
            y_weight = slicer(y_weight)
            classes_weights_tensor = slicer(self._classes_weights_tensor)

        unreduced = self._mse(y_pred, y) * classes_weights_tensor
        unreduced = unreduced * y_weight
        unreduced = unreduced.sum(dim=1)
        return unreduced.mean()

    def loss_cover(self, y_pred, y, y_weight):
        return self._loss(y_pred, y, y_weight, self._slice_cover)

    def loss_occlusion(self, y_pred, y, y_weight_mask):
        return self._loss(y_pred, y, y_weight_mask, self._slice_occlusion)

    def loss_ecosystems(self, y_pred, y, y_weight_mask):
        return self._loss(y_pred, y, y_weight_mask, self._slice_ecosystems)

    def loss(self, y_pred, y, y_weight_mask):
        loss_cover = self.loss_cover(y_pred, y, y_weight_mask)
        loss_occlusion = self.loss_occlusion(y_pred, y, y_weight_mask)
        loss_ecosystems = self.loss_ecosystems(y_pred, y, y_weight_mask)

        loss_total = (
            self.loss_weight_cover * loss_cover
            + self.loss_weight_occlusion * loss_occlusion
            + self.loss_weight_ecosystems * loss_ecosystems
        )
        return loss_total

    def forward(self, x, x_head):
        y_pred = self.evonet.forward(x, x_head)
        # TODO: add softmax for each grup of classes
        raise NotImplementedError("Not implemented")
        y_pred_cover = self._slice_cover(y_pred)

        return y_pred_cover, y_pred_occlusion, y_pred_ecosystems

    def predict(self, x, x_head):
        return self.evonet.predict(x, x_head)

    def training_step(self, batch, batch_idx):
        # x, x_head, y, y_weight_mask = batch
        # x, x_head, y_cover, y_occlusion, y_ecosystems, y_weight_cover, y_weight_ = batch
        y_pred = self.evonet(x, x_head)
        loss = self.loss(y_pred, y, y_weight_mask)
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
        # Initialize device-aware tensors once at the beginning of training
        device = self.device

        # Initialize the class weights tensor if not already done
        if self._classes_weights_tensor is None:
            self._classes_weights_tensor = self.get_classes_weights_tensor(
                self._classes_weights or {}
            ).to(device)

        # Initialize true positives, false positives, false negatives accumulators
        for accumulator_type in self._labels_types:
            for key in self._iou_accumulators_keys:
                if self._iou_accumulators[accumulator_type][key] is None:
                    self._iou_accumulators[accumulator_type][key] = (
                        torch.zeros(
                            self.num_classes,
                            dtype=torch.float32,
                            device=device,
                        )
                    )

    def on_validation_start(self):
        return self.on_train_start()

    def validation_step(self, batch, batch_idx):
        x, x_head, y, y_weights = batch
        y_pred = self.evonet(x, x_head)

        self._update_iou_accumulators(y_pred, y, y_weights)

    def _slicer(self, labels_type):
        if labels_type == "cover":
            return self._slice_cover
        elif labels_type == "occlusion":
            return self._slice_occlusion
        elif labels_type == "ecosystems":
            return self._slice_ecosystems
        else:
            raise ValueError(f"Unknown labels type: {labels_type}")

    def _update_iou_accumulators(self, y_pred, y, y_weights):
        for labels_type in self._labels_types:
            slicer = self._slicer(labels_type)

            y_pred = slicer(y_pred)
            y = slicer(y)
            y_weights = slicer(y_weights)

            mask = self._get_max_pixel_weight_mask(y_weights)

            for lab_i in range(self.num_classes):
                tp, fp, fn = get_label_stats(y_pred, y, lab_i, mask=mask)
                self._iou_accumulators[labels_type]["true_positives"][
                    lab_i
                ] += tp
                self._iou_accumulators[labels_type]["false_positives"][
                    lab_i
                ] += fp
                self._iou_accumulators[labels_type]["false_negatives"][
                    lab_i
                ] += fn

    def on_validation_epoch_end(self):
        for label_type in self._labels_types:
            mean_iou, classes_iou = self._get_iou_metric(label_type)

            self.log(
                f"val_mIoU_{label_type}",
                mean_iou,
                prog_bar=True,
                sync_dist=True,
            )

            classes_dict = self.classes_dict[label_type]
            classes_ids = list(classes_dict.keys())

            for lab_i, iou in enumerate(classes_iou):
                class_idx = classes_ids[lab_i]
                class_name = classes_dict[class_idx]
                self.log(
                    f"val_IoU_{class_idx:03d}_{class_name}",
                    iou,
                    sync_dist=True,
                )

    def _get_iou_metric(self, labels_type):
        # Calculate IoU per class with weights applied
        classes_iou = []
        weighted_iou_sum = 0.0
        weight_sum = 0.0

        raise ValueError("Not implemented")  # fix range below
        for lab_i in range(self.num_classes):
            tp = self._iou_accumulators[labels_type]["true_positives"][lab_i]
            fp = self._iou_accumulators[labels_type]["false_positives"][lab_i]
            fn = self._iou_accumulators[labels_type]["false_negatives"][lab_i]
            union = tp + fp + fn
            if union > 0:
                iou = tp / union
                weight = self._classes_weights_tensor[0, lab_i, 0, 0]
                weighted_iou_sum += iou * weight
                weight_sum += weight
                classes_iou.append(iou.item())
            else:
                classes_iou.append(float("nan"))

        # Calculate the weighted mean IoU
        mean_iou = (
            (weighted_iou_sum / weight_sum).item()
            if weight_sum > 0
            else float("nan")
        )

        self._reset_accumulators()

        return mean_iou, classes_iou
