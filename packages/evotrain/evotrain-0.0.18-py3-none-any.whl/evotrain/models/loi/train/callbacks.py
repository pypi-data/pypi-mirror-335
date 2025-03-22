import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import lightning as L
import torch
import torchvision
import torchmetrics
from evotrain.labels import binarize_probs


class InferencePreviewClouds(L.Callback):
    """
    Pytorch Lightning callback to generate a grid of images with the
    input features, the target and the predicted mask. The grid is saved
    to disk. The callback is called at the end of each training epoch and
    it is used to monitor the training progress and the model performance.
    """

    def __init__(
        self,
        inference_dataset,
        tt_logger,
        indices=None,
        inference_freq="on_train_epoch_end",
        config=None,
    ):
        super().__init__()

        self.bands = inference_dataset.bands
        self.dataset_labels = inference_dataset.labels
        self.tt_logger = tt_logger
        self.rgb_ids = [3, 2, 1]
        self.inference_freq = inference_freq
        assert (
            self.inference_freq
            in [
                "on_train_epoch_end",
                "on_train_end",
                "on_train_batch_end",
            ]
        ), "inference_freq must be one of 'on_train_epoch_end', 'on_train_end' or 'on_train_batch_end'"
        self.config = config

        if self.config["data_config"]["classify_snow"]:
            self.id_dict = self.config["labels_config"][
                "cloudsen12_mergedclouds_extrasnow"
            ]
        else:
            self.id_dict = self.config["labels_config"][
                self.config["data_config"]["dataset"]
            ]
        self.config["labels_config"][self.config["data_config"]["dataset"]]

        self.indices = indices

        self.feats, self.targets, self.feats_head = self._load_feats_targets(
            inference_dataset
        )

        self.folder = (
            Path(self.tt_logger.save_dir)
            / self.tt_logger.name
            / f"version_{self.tt_logger.version}"
            / self.inference_freq
        )
        self.folder.mkdir(exist_ok=True, parents=True)
        self.folder.chmod(0o775)

    def _load_feats_targets(self, inference_dataset):
        """
        Load the features and targets from the inference dataset.
        """
        # Find the indices of the samples to show in the grid

        # get the features and targets, and ignore the metadata
        X, y, x_head = zip(*[inference_dataset[i] for i in self.indices])
        X = torch.stack(X)
        y = torch.stack(y)
        x_head = torch.stack(x_head)

        return X, y, x_head

    def _get_model_output(
        self,
        pl_module,
        feats,
        feats_head,
        one_minus_surface_probs=False,
        raw_output=False,
    ):
        """
        Get the model output for a number of features and return the 1-P(Surface) probabilities.
        """
        inference_images = feats.to(pl_module.device)
        inference_images_head = feats_head.to(pl_module.device)
        with torch.no_grad():
            pl_module.eval()
            predicted = pl_module(inference_images, inference_images_head)
            pl_module.train()
            if isinstance(predicted, tuple):
                # This happens when we have a classification head on top of the segmentation model (e.g. when using dropout)
                logits, probs = predicted
                predicted = logits
            predicted = predicted.cpu()

        if raw_output:
            return predicted
        rgb_predictions = batch_probs_to_rgb(
            predicted, self.dataset_labels, id_dict=self.id_dict, config=self.config
        )

        if one_minus_surface_probs:
            # get the 1-P(Surface) probabilities from the model predictions (occlusion score)
            one_minus_surface_probs = []
            for i in range(predicted.shape[0]):
                one_minus_surface_probs.append(1 - predicted[i, 0, ...].numpy())
            one_minus_surface_probs = np.array(one_minus_surface_probs)

            return rgb_predictions, one_minus_surface_probs  # TODO
        else:
            return rgb_predictions

    def _build_grid(self, pl_module):
        """
        Build a grid of RGB images with the input features, the target and the predicted mask.
        """
        # the number of rows in the grid is the number of samples
        n_rows = len(self.indices)
        # select the RGB bands (self.rgb_ids) from the features (self.feats)
        feats_rgb = self.feats[:, self.rgb_ids, ...].cpu()
        # scale the pixel values to the range [0, 1] for each image in the batch
        feats_rgb = scale_minmax_batch(feats_rgb)
        # convert the target probabilities to RGB images
        targets_rgb = batch_probs_to_rgb(
            self.targets, self.dataset_labels, id_dict=self.id_dict, config=self.config
        )
        # convert the predicted probabilities to RGB images
        predicted_rgb, one_minus_surface_probs = self._get_model_output(
            pl_module, self.feats, self.feats_head, one_minus_surface_probs=True
        )
        # Let's repeat the matrix one_minus_surface_probs to have the same shape as the RGB images
        one_minus_surface_probs = np.repeat(
            one_minus_surface_probs[:, np.newaxis, ...], 3, axis=1
        )

        # for each batch/location_id we have a row, with each year feats,
        # the prediction and finally the target
        images = []
        for loc_id in range(n_rows):
            images.append(feats_rgb[loc_id])
            images.append(targets_rgb[loc_id])
            images.append(predicted_rgb[loc_id])
            images.append(torch.tensor(one_minus_surface_probs[loc_id]))

        grid = torchvision.utils.make_grid(images, nrow=(len(images) // n_rows))
        return grid

    def _build_advanced_grid(self, pl_module, trainer):
        # In this function we will make a matplotlib plot that displays
        # all layers of the mask and the rgb image in the first row
        # and all layers of the predicted mask in the second row

        feats_rgb = self.feats[:, self.rgb_ids, ...].cpu()
        feats_rgb = scale_minmax_batch(feats_rgb)
        target_masks = self.targets
        predic_masks = self._get_model_output(
            pl_module, self.feats, self.feats_head, raw_output=True
        )

        # We have 10 samples for each array so we will have 10 plots
        # In each plot we show in the first row all the layers of the mask
        # In the second row we show all the layers of the predicted mask

        for i in range(10):
            fig, axs = plt.subplots(3, 4, figsize=(20, 40))
            # in each plot we plot the RGB image in one row alone,
            # and then 4 layers of the target mask in a second row
            # and 4 layers of the predicted mask in a third row
            rgb_img = feats_rgb[i].numpy()
            rgb_img = np.moveaxis(rgb_img, 0, -1)
            axs[0, 0].imshow(rgb_img)
            axs[0, 0].set_title("RGB Image")
            axs[0, 0].axis("off")
            # Let's remove the axis for the rest of the plots in the first row
            for j in range(1, 4):
                axs[0, j].axis("off")

            for j in range(4):
                axs[1, j].imshow(target_masks[i, j, ...].numpy(), cmap="gray")
                axs[1, j].set_title(f"Target Mask Layer {j}")
                axs[1, j].axis("off")

                axs[2, j].imshow(predic_masks[i, j, ...], cmap="gray")
                axs[2, j].set_title(f"Predicted Mask Layer {j}")
                axs[2, j].axis("off")

            # Save the plot
            advanced_folder = self.folder / "advanced_grids"
            advanced_folder.mkdir(exist_ok=True, parents=True)
            fn = (
                advanced_folder / f"advanced_grid_epoch{trainer.current_epoch:03d}"
                f"_step{trainer.global_step:08d}_{i}.png"
            )

            # Save
            plt.savefig(fn, bbox_inches="tight")
            plt.close(fig)

        # Save the plot
        advanced_folder = self.folder / "advanced_grids"
        advanced_folder.mkdir(exist_ok=True, parents=True)
        fn = (
            advanced_folder / f"advanced_grid_epoch{trainer.current_epoch:03d}"
            f"_step{trainer.global_step:08d}_{i}.png"
        )

        plt.savefig(fn, bbox_inches="tight")
        plt.close(fig)

    def _save_grid(self, combined_grid, trainer):
        """
        Save the grid to disk.
        """
        fig, ax = plt.subplots(figsize=(14, 20))
        ax.imshow(combined_grid.permute(1, 2, 0).cpu())
        ax.set_title(
            f"epoch: {trainer.current_epoch:03d} - "
            f"step: {trainer.global_step / 1000:.02f}K"
        )
        ax.set_axis_off()

        grid_folder = self.folder / "grids"
        grid_folder.mkdir(exist_ok=True, parents=True)
        fn = (
            grid_folder / f"grid_epoch{trainer.current_epoch:03d}"
            f"_step{trainer.global_step:08d}.png"
        )

        plt.savefig(fn, bbox_inches="tight")
        plt.close(fig)
        os.chmod(fn, 0o755)

    def on_train_epoch_end(self, trainer, pl_module):
        """
        Callback called at the end of each training epoch.
        """
        if self.inference_freq == "on_train_epoch_end":
            grid = self._build_grid(pl_module)
            self._save_grid(grid, trainer)
            self._build_advanced_grid(pl_module, trainer)
            # also we want to build and save the confusion matrix.
            cm = self.create_confusion_matrix(trainer, pl_module)
            self.plot_confusion_matrix(cm, trainer, save=True)
        else:
            pass

    def on_train_end(self, trainer, pl_module):
        """
        Callback called at the end of the training loop.
        """
        if self.inference_freq == "on_train_end":
            # we want to build and save the grid
            grid = self._build_grid(pl_module)
            self._save_grid(grid, trainer)
            self._build_advanced_grid(pl_module, trainer)
            # also we want to build and save the confusion matrix.
            cm = self.create_confusion_matrix(trainer, pl_module)
            self.plot_confusion_matrix(cm, trainer, save=True)
        else:
            pass

    def on_train_batch_end(self, trainer, pl_module, batch_output, batch, batch_idx):
        """
        Callback called at the end of each training batch.
        """
        if self.inference_freq == "on_train_batch_end":
            if trainer.global_step in [1, 10, 20, 50, 100, 200]:
                grid = self._build_grid(pl_module)
                self._save_grid(grid, trainer)
                # also we want to build and save the confusion matrix.
                cm = self.create_confusion_matrix(trainer, pl_module)
                self.plot_confusion_matrix(cm, trainer, save=True)
        else:
            pass

    def create_confusion_matrix(self, trainer, pl_module):
        """
        Create a confusion matrix.
        """
        feats = self.feats.to(pl_module.device)
        feats_head = self.feats_head.to(pl_module.device)
        targets = self.targets

        with torch.no_grad():
            pl_module.eval()
            predicted = pl_module(feats, feats_head)
            pl_module.train()
            if isinstance(predicted, tuple):
                # This happens when we have a classification head on top of the segmentation model (e.g. when using dropout)
                logits, probs = predicted
                predicted = logits
            predicted = predicted.detach().cpu()

        predicted = binarize_probs(predicted, self.dataset_labels)
        targets = binarize_probs(targets, self.dataset_labels)

        # We'll use the confusion matrix from torchmetrics
        cm = torchmetrics.ConfusionMatrix(
            task="multiclass", num_classes=len(self.dataset_labels)
        )
        cm = cm(torch.tensor(predicted), torch.tensor(targets))

        return cm

    def plot_confusion_matrix(self, cm, trainer, save=True):
        """
        Plot the confusion matrix.

        Args:
            cm (torch.Tensor): Confusion matrix.
        """
        # Determine the appropriate label dictionary based on the configuration

        self.txt_labs = [k for k in self.id_dict.keys()]

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.matshow(cm)
        ax.set_xticks(range(len(self.dataset_labels)))
        ax.set_yticks(range(len(self.dataset_labels)))
        ax.set_xticklabels(self.txt_labs, rotation=45)
        ax.set_yticklabels(self.txt_labs)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
        ax.set_title("Confusion Matrix")
        for i in range(len(self.dataset_labels)):
            for j in range(len(self.dataset_labels)):
                ax.text(j, i, f"{cm[i, j]:.0f}", ha="center", va="center")

        if save:
            cm_folder = self.folder / "confusion_matrices"
            cm_folder.mkdir(exist_ok=True, parents=True)
            fn = (
                cm_folder / f"confusion_matrix_epoch{trainer.current_epoch:03d}"
                f"_step{trainer.global_step:08d}.png"
            )
            plt.savefig(fn, bbox_inches="tight")
            plt.close(fig)
        else:
            plt.show()


def probs_to_rgb(probs, dataset_labels, id_dict=None, config=None):
    """
    Convert class probabilities to RGB images.

    Args:
        probs (np.array): Array with class probabilities.
        dataset_labels (list): List with class labels.

    Returns:
        np.array: RGB image.
    """
    return label_to_rgb_clouds(
        binarize_probs(probs, dataset_labels), id_dict=id_dict, config=config
    )


def label_to_rgb_clouds(lc_pred, id_dict, config=None):
    color_dict = config["colors_config"]

    colors = {
        id_dict[class_name]: {
            "name": class_name,
            "color": np.array(color_dict[class_name]) / 255,
        }
        for class_name in id_dict.keys()
    }
    rgb_pred = np.zeros(
        (
            3,
            lc_pred.shape[0],
            lc_pred.shape[1],
        )
    )

    for k, v in colors.items():
        for ch in range(3):
            im = rgb_pred[ch, :, :]
            im[lc_pred == k] = v["color"][ch]

    return rgb_pred


def batch_probs_to_rgb(batch, dataset_labels, id_dict=None, config=None):
    """
    Convert batch of class probabilities to RGB images.

    Args:
        batch (np.array): Batch with class probabilities.
        dataset_labels (list): List with class labels.

    Returns:
        Union[np.array, torch.Tensor]: Batch of RGB images.
    """
    was_tensor = False
    if isinstance(batch, torch.Tensor):
        was_tensor = True
        batch = batch.numpy()

    new_batch = np.array(
        [probs_to_rgb(b, dataset_labels, id_dict=id_dict, config=config) for b in batch]
    )

    if was_tensor:
        new_batch = torch.Tensor(new_batch)
    return new_batch


def scale_minmax_batch(inference_images, axis=(1, 2, 3)):
    """
    Scale pixel values to the range [0, 1] for each image in the batch.

    Args:
        inference_images (torch.Tensor): Batch of images.
        axis (tuple): Tuple with the axes to compute the min and max values.

    Returns:
        torch.Tensor: Scaled batch of images.
    """
    inference_images = inference_images.numpy()
    vmin = inference_images.min(axis=axis)
    vmin = np.expand_dims(vmin, axis)
    vmin = np.broadcast_to(vmin, inference_images.shape)

    vmax = inference_images.max(axis=axis)
    vmax = np.expand_dims(vmax, axis)
    vmax = np.broadcast_to(vmax, inference_images.shape)

    inf_mm = inference_images - vmin
    inf_mm = inf_mm / (vmax - vmin)

    inf_mm = torch.tensor(inf_mm)

    return inf_mm
