import pytorch_lightning as pl
import torch
from torch.optim.lr_scheduler import StepLR
from torch import nn
from evotrain.models.evonet import EvoNet
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
import numpy as np

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
        self.loss_weight_attribute = evonet_kwargs.get(
            "loss_weight_attribute", 1
        )

        classes_dict = evonet_kwargs["classes_components"]
        self.classes_weights_components_dict = evonet_kwargs["classes_weights_components"]
        self.classes_weights_tensor_component = {}
        self.classes_weights_tensor_component['cover'] = self.get_classes_weights_tensor(self.classes_weights_components_dict['cover'], classes_dict['cover'])
        self.classes_weights_tensor_component['occlusion'] = self.get_classes_weights_tensor(self.classes_weights_components_dict['occlusion'], classes_dict['occlusion'])
        self.classes_weights_tensor_component['attribute'] = self.get_classes_weights_tensor(self.classes_weights_components_dict['attribute'], classes_dict['attribute'])
        self.classes_dict = classes_dict

        self.num_classes_components = {
            'cover': len(classes_dict["cover"].keys()),
            'occlusion': len(classes_dict["occlusion"].keys()),
            'attribute': len(classes_dict["attribute"].keys())
        }
            
        self.num_classes = (
            self.num_classes_components['cover']#num_classes_cover
            + self.num_classes_components['occlusion']#num_classes_occlusion
            + self.num_classes_components['attribute']#num_classes_attribute
        )

        self._labels_types = ["cover", "occlusion", "attribute"]
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
        evonet_kwargs["in_channels_spatial"] = len(evonet_kwargs["bands"])
        bands_head = evonet_kwargs["bands_head"]
        in_head_channels = 0
        if "latlon" in bands_head:
            in_head_channels += 3
        if "meteo" in bands_head:
            in_head_channels += 6
        if "doy" in bands_head:
            in_head_channels += 2
        evonet_kwargs["in_channels_head"] = in_head_channels
        
        evonet_kwargs["out_channels"] = self.num_classes
        # evonet_kwargs["activation_spatial"] = evonet_kwargs["activation_spatial"]   # "sigmoid"
        # evonet_kwargs["activation_mlp"] = evonet_kwargs["activation_mlp"]  
        # "identity"

        self.evonet = EvoNet(**evonet_kwargs)

    def _slice_cover(self, x):
        return x[:, : self.num_classes_components['cover']] #num_classes_cover, ...]

    def _slice_occlusion(self, x):
        start = self.num_classes_components['cover'] #num_classes_cover
        end = start + self.num_classes_components['occlusion'] #m_classes_occlusion
        return x[:, start:end, ...]

    def _slice_attribute(self, x):
        start = self.num_classes_components['cover'] + self.num_classes_components['occlusion'] # m_classes_cover + self.num_classes_occlusion
        end = start + self.num_classes_components['attribute'] #lf.num_classes_attribute
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
        
        if self.hparams.scheduler == 'StepLR':
            scheduler = StepLR(
                opt,
                step_size=self.hparams.scheduler_step_size,
                gamma=self.hparams.scheduler_gamma,
            )
        elif self.hparams.scheduler == 'CosineAnnealingWarmRestarts':
            scheduler = CosineAnnealingWarmRestarts(
                opt,
                T_0=self.hparams.scheduler_T_0,
                T_mult=self.hparams.scheduler_T_mult,
                eta_min=self.hparams.scheduler_eta_min,
                last_epoch=self.hparams.scheduler_last_epoch,
            )
        return [opt], [scheduler]

    def get_classes_weights_tensor(self, classes_weights_dict, classes):
        weights = torch.tensor(
            [classes_weights_dict.get(k, 1) for k in classes]
        )
        # Expand the weights to shape (1, classes, 1, 1) for broadcasting
        weights = weights.view(1, len(classes), 1, 1)
        return weights

    def _loss(self, y_pred, y, y_weight, classes_weights_tensor):#, slicer=None):
        # y_weight_mask has shape (batch, classes, y, x)
        # the weight is generally 1, but can be set to 0 to ignore pixels or
        # more than 1 to give more importance to some pixels (e.g. roads...)

        unreduced = self._mse(y_pred, y) * classes_weights_tensor
        unreduced = unreduced * y_weight
        unreduced = unreduced.sum(dim=1)
        return unreduced.mean()


    def loss(self, y_pred, y, y_weight_mask):
        
        loss_cover = self._loss(y_pred[0],
                                y[0],
                                y_weight_mask[0],
                                self.classes_weights_tensor_component['cover'].cuda()
                               )
        loss_occlusion = self._loss(y_pred[1],
                                    y[1],
                                    y_weight_mask[1],
                                    self.classes_weights_tensor_component['occlusion'].cuda())
        loss_attribute = self._loss(y_pred[2],
                                     y[2],
                                     y_weight_mask[2],
                                    self.classes_weights_tensor_component['attribute'].cuda())

        loss_total = (
            self.loss_weight_cover * loss_cover
            + self.loss_weight_occlusion * loss_occlusion
            + self.loss_weight_attribute * loss_attribute
        )
        return loss_total

    def forward(self, x, x_head):
        y_pred = self.evonet.forward(x, x_head)
        y_pred = [self._slice_cover(y_pred), self._slice_occlusion(y_pred), self._slice_attribute(y_pred)]
        softmax = nn.Softmax(dim=1)
        y_pred_cover = softmax(y_pred[0])
        y_pred_occlusion = softmax(y_pred[1])
        y_pred_attribute = y_pred[2]
        # y_pred_attribute = softmax(y_pred[2])

        return [y_pred_cover, y_pred_occlusion, y_pred_attribute]

    def predict(self, x, x_head):
        pred = self.evonet.predict(x, x_head)
        pred = pred[np.newaxis, ...]
        y_pred = [self._slice_cover(pred), self._slice_occlusion(pred), self._slice_attribute(pred)]
        softmax = nn.Softmax(dim=1)
        y_pred_cover = softmax(torch.from_numpy(y_pred[0])).numpy()
        y_pred_occlusion = softmax(torch.from_numpy(y_pred[1])).numpy()
        y_pred_attribute = y_pred[2]
        # y_pred_attribute = softmax(y_pred[2])
        return y_pred_cover, y_pred_occlusion, y_pred_attribute

    def training_step(self, batch, batch_idx):
        x, x_head, y, y_weight_mask = batch
        # x, x_head, y_cover, y_occlusion, y_attribute, y_weight_cover, y_weight_ = batch
        y_pred = self.evonet(x, x_head) #self.evonet
        y_pred = [self._slice_cover(y_pred), self._slice_occlusion(y_pred), self._slice_attribute(y_pred)]
        
        softmax = nn.Softmax(dim=1)
        y_pred_cover = softmax(y_pred[0])
        y_pred_occlusion = softmax(y_pred[1])
        y_pred_attribute = y_pred[2]
        # y_pred_attribute = softmax(y_pred[2])
        
        y_pred = [y_pred_cover, y_pred_occlusion, y_pred_attribute]
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

        # Initialize true positives, false positives, false negatives accumulators
        for accumulator_type in self._labels_types:
            for key in self._iou_accumulators_keys:
                if self._iou_accumulators[accumulator_type][key] is None:
                    self._iou_accumulators[accumulator_type][key] = (
                        torch.zeros(
                            self.num_classes_components[accumulator_type],
                            dtype=torch.float32,
                            device=device,
                        )
                    )

    def on_validation_start(self):
        return self.on_train_start()

    def validation_step(self, batch, batch_idx):
        # x, x_head, prob_cover, prob_occlusion, prob_attribute, weight_cover, weight_occlusion, weight_attribute
        x, x_head, y, y_weights = batch
        y_pred = self.evonet(x, x_head)
        y_pred = [self._slice_cover(y_pred), self._slice_occlusion(y_pred), self._slice_attribute(y_pred)]
        softmax = nn.Softmax(dim=1)
        y_pred_cover = softmax(y_pred[0])
        y_pred_occlusion = softmax(y_pred[1])
        y_pred_attribute = y_pred[2]
        # y_pred_attribute = softmax(y_pred[2])
        
        y_pred_softmax = [y_pred_cover, y_pred_occlusion, y_pred_attribute]
        self._update_iou_accumulators(y_pred_softmax, y, y_weights)


    def _update_iou_accumulators(self, y_pred, y, y_weights):
        for y_pred_component, y_component, y_weights_component, labels_type in zip(y_pred, y, y_weights, self._labels_types):
            
            mask = self._get_max_pixel_weight_mask(y_weights_component)

            for lab_i in range(self.num_classes_components[labels_type]):
                tp, fp, fn = get_label_stats(y_pred_component, y_component, lab_i, mask=mask)
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
                    f"val_IoU_{label_type}_{int(class_idx):03d}_{class_name}",
                    iou,
                    sync_dist=True,
                )
        self._reset_accumulators()

    def _get_iou_metric(self, labels_type):
        # Calculate IoU per class with weights applied
        classes_iou = []
        weighted_iou_sum = 0.0
        weight_sum = 0.0

        # raise ValueError("Not implemented")  # fix range below
        for lab_i in range(self.num_classes_components[labels_type]):
            tp = self._iou_accumulators[labels_type]["true_positives"][lab_i]
            fp = self._iou_accumulators[labels_type]["false_positives"][lab_i]
            fn = self._iou_accumulators[labels_type]["false_negatives"][lab_i]
            union = tp + fp + fn
            if union > 0:
                iou = tp / union
                weight = self.classes_weights_tensor_component[labels_type][0, lab_i, 0, 0]
                weighted_iou_sum += iou * weight
                weight_sum += weight
                classes_iou.append(iou.item())
            else:
                # from loguru import logger
                # logger.info(f'{labels_type} {lab_i} {tp}')
                classes_iou.append(float("nan"))

        # Calculate the weighted mean IoU
        mean_iou = (
            (weighted_iou_sum / weight_sum).item()
            if weight_sum > 0
            else float("nan")
        )

        # self._reset_accumulators()

        return mean_iou, classes_iou
