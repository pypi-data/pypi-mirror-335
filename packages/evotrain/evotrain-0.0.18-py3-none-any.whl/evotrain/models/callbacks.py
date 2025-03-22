import os
from pathlib import Path

import numpy as np
import torch
import torchvision
import matplotlib.pyplot as plt
import pytorch_lightning as pl
from loguru import logger

from evotrain.labels import get_labeled_image, batch_probs_to_rgb
from evotrain.v2.dataloaders import SinglePatchDataset


def scale_minmax_batch(val_images, axis=(1, 2, 3)):
    val_images = val_images.numpy()
    vmin = val_images.min(axis=axis)
    vmin = np.expand_dims(vmin, axis)
    vmin = np.broadcast_to(vmin, val_images.shape)

    vmax = val_images.max(axis=axis)
    vmax = np.expand_dims(vmax, axis)
    vmax = np.broadcast_to(vmax, val_images.shape)

    val_mm = val_images - vmin
    val_mm = val_mm / (vmax - vmin)

    val_mm = torch.tensor(val_mm)

    return val_mm


class MonitorEpochs(pl.Callback):

    def __init__(self,
                 feats,
                 targets,
                 labs,
                 every_n_epochs,
                 tt_logger):

        super().__init__()
        self.feats = feats  # Images to reconstruct during training
        self.targets = targets
        self.labs = labs
        # Only save those images every N epochs (otherwise tensorboard gets
        # quite large)
        self.every_n_epochs = every_n_epochs
        self.tt_logger = tt_logger

    def on_train_epoch_end(self, trainer, pl_module):
        if trainer.current_epoch % self.every_n_epochs == 0:
            val_images = self.feats.to(pl_module.device)
            with torch.no_grad():
                pl_module.eval()
                predicted = pl_module(val_images)
                pl_module.train()
                predicted = predicted.cpu().numpy()

            val_images = val_images[:, :3, ...].cpu()
            val_masks = get_labeled_image(self.targets, self.labs)
            predicted = get_labeled_image(predicted, self.labs)

            # concatenate tensors along the channel dimension
            imgs = torch.cat([val_images, val_masks, predicted], dim=0)

            # create grids of images for each column
            n_batches = val_images.shape[0]
            grid1 = torchvision.utils.make_grid(
                imgs[:n_batches, ...], nrow=1, normalize=True,
                value_range=(-2, 2))
            grid2 = torchvision.utils.make_grid(
                imgs[n_batches:n_batches*2, ...], nrow=1, normalize=True)
            grid3 = torchvision.utils.make_grid(
                imgs[n_batches*2:, ...], nrow=1, normalize=True)

            # combine the grids into a single image
            combined_grid = torch.cat([grid1, grid2, grid3], dim=2)

            fig, ax = plt.subplots(figsize=(8, 10))
            ax.imshow(combined_grid.permute(1, 2, 0).cpu())
            ax.set_title(f'epoch: {trainer.current_epoch}')
            ax.set_axis_off()

            folder = Path(self.tt_logger.save_dir) / self.tt_logger.name / \
                f'version_{self.tt_logger.version}' / 'predictions'
            folder.mkdir(exist_ok=True, parents=True)
            folder.chmod(0o755)

            fn = folder / f'grid_{trainer.current_epoch:03d}.png'
            logger.info(f"Saving {fn}")
            plt.savefig(fn, bbox_inches='tight')
            plt.close(fig)
            os.chmod(fn, 0o755)


class MonitorBatches(pl.Callback):

    def __init__(self,
                 feats,
                 targets,
                 labs,
                 every_n_steps,
                 tt_logger):

        super().__init__()
        self.feats = feats  # Images to reconstruct during training
        self.targets = targets
        self.labs = labs
        self.every_n_steps = every_n_steps
        self.tt_logger = tt_logger

    def on_train_batch_end(self, trainer, pl_module,
                           batch_output, batch, batch_idx):
        if trainer.global_step % self.every_n_steps == 0:
            val_images = self.feats.to(pl_module.device)
            with torch.no_grad():
                pl_module.eval()
                predicted = pl_module(val_images)
                pl_module.train()
                predicted = predicted.cpu().numpy()

            val_images = val_images[:, :3, ...].cpu()
            val_labs = self.targets
            val_labs = batch_probs_to_rgb(val_labs, self.labs)
            predicted = batch_probs_to_rgb(predicted, self.labs)

            val_images = scale_minmax_batch(val_images)

            # concatenate tensors along the channel dimension
            imgs = torch.stack([val_images,
                                torch.Tensor(val_labs),
                                torch.Tensor(predicted)], dim=0)

            # create grids of images for each column
            n_batches = val_images.shape[0]
            grid1 = torchvision.utils.make_grid(
                imgs[:n_batches, ...], nrow=1, normalize=True,
                value_range=(-2, 2))
            grid2 = torchvision.utils.make_grid(
                imgs[n_batches:n_batches*2, ...], nrow=1, normalize=True)
            grid3 = torchvision.utils.make_grid(
                imgs[n_batches*2:, ...], nrow=1, normalize=True)

            # combine the grids into a single image
            combined_grid = torch.cat([grid1, grid2, grid3], dim=2)

            fig, ax = plt.subplots(figsize=(8, 10))
            ax.imshow(combined_grid.permute(1, 2, 0).cpu())
            ax.set_title(
                f'epoch: {trainer.current_epoch:03d} - '
                f'step: {trainer.global_step / 1000:.02f}K'
            )
            ax.set_axis_off()
            folder = Path(self.tt_logger.save_dir) / self.tt_logger.name / \
                f'version_{self.tt_logger.version}' / 'predictions'
            folder.mkdir(exist_ok=True, parents=True)
            folder.chmod(0o755)

            fn = (folder /
                  f'grid_epoch{trainer.current_epoch:03d}'
                  f'_step{trainer.global_step:08d}.png')

            plt.savefig(fn, bbox_inches='tight')
            plt.close(fig)
            os.chmod(fn, 0o755)


class InferencePreview(pl.Callback):

    def __init__(self,
                 val_dataset: SinglePatchDataset,
                 tt_logger,
                 val_ids=8,
                 years=None,
                 every_n_steps=1000,
                 rgb_ids=[0, 1, 2],
                 augmented_scaling=False,
                 augmented_scaling_params=None):

        super().__init__()

        if years is None:
            years = list(range(2018, 2023))
        self.years = years

        self.bands = val_dataset.bands
        self.labs = val_dataset.labels
        self.every_n_steps = every_n_steps
        self.tt_logger = tt_logger
        self.rgb_ids = rgb_ids

        self.augmented_scaling = augmented_scaling
        self.augmented_scaling_params = augmented_scaling_params

        if val_ids is None:
            val_ids = 8
        self.location_ids = self._location_ids(val_dataset, val_ids)
        self.feats_years, self.targets = self._load_feats_targets(
            val_dataset,
            self.location_ids
        )

    def _location_ids(self, val_dataset, val_ids):
        """Return location_ids to display"""

        if isinstance(val_ids, int):
            location_ids = (val_dataset.evo_dataset
                            .location_ids.sample(val_ids, random_state=0)
                            .values.tolist())
        elif isinstance(val_ids, (list, tuple)):
            location_ids = val_dataset.evo_dataset.location_ids
            location_ids = location_ids[location_ids.isin(
                val_ids)].values.tolist()
            if len(location_ids.size) != len(val_ids):
                not_found = [lc for lc in val_ids if lc not in location_ids]
                raise ValueError(f"The following location_ids could not be "
                                 "found in the validation dataset: "
                                 f"{not_found}")
        else:
            TypeError(f"`val_ids` is of type: {type(val_ids)}. "
                      "Expected list or tuple of location_ids or integer")

        return location_ids

    def _load_feats_targets(self, val_dataset: SinglePatchDataset,
                            location_ids):
        """Loads dictionary of feats tensors (years are the keys for each
        year batch) and the target features, which are the same for all
        years."""

        years = self.years
        feats = {}
        for year in years:
            feats[year] = torch.from_numpy(
                np.array([val_dataset.read(loc_id,
                                           year,
                                           load_target=False,
                                           augmented_scaling=self.augmented_scaling,  # noqa: E501
                                           augmented_scaling_params=self.augmented_scaling_params).data  # noqa: E501
                          for loc_id in location_ids]))
        # target is the same (worldcover_2021), load from year 0
        _, targets = zip(*[val_dataset.read(loc_id,
                                            years[0],
                                            load_target=True)
                           for loc_id in location_ids])
        targets = torch.from_numpy(np.array(targets))
        return feats, targets

    def _predicted_rgb(self, pl_module, feats):
        val_images = feats.to(pl_module.device)
        with torch.no_grad():
            pl_module.eval()
            predicted = pl_module(val_images)
            pl_module.train()
            predicted = predicted.cpu()

        predicted = batch_probs_to_rgb(predicted, self.labs)

        return predicted

    def _targets_rgb(self, targets):
        return batch_probs_to_rgb(targets, self.labs)

    def _feats_rgb(self, feats):
        feats_rgb = feats[:, self.rgb_ids, ...].cpu()
        feats_rgb = scale_minmax_batch(feats_rgb)
        return feats_rgb

    def _build_grid(self, pl_module):

        feats_years = self.feats_years
        targets = self.targets
        n_rows = len(self.location_ids)

        # for each location there is an element of the batch
        feats_rgb = {}
        predicted_rgb = {}
        targets_rgb = self._targets_rgb(targets)

        for year in self.years:
            predicted_rgb[year] = self._predicted_rgb(pl_module,
                                                      feats_years[year])
            feats_rgb[year] = self._feats_rgb(feats_years[year])

        # for each batch/location_id we have a row, with each year feats,
        # the prediction and finally the target
        images = []
        for loc_id in range(n_rows):
            for year in self.years:
                images.append(feats_rgb[year][loc_id])
                images.append(predicted_rgb[year][loc_id])
            images.append(targets_rgb[loc_id])

        grid = torchvision.utils.make_grid(images,
                                           nrow=(len(images) // n_rows))
        return grid

    def _save_grid(self, combined_grid, trainer):
        fig, ax = plt.subplots(figsize=(14, 20))
        ax.imshow(combined_grid.permute(1, 2, 0).cpu())
        ax.set_title(
            f'epoch: {trainer.current_epoch:03d} - '
            f'step: {trainer.global_step / 1000:.02f}K'
        )
        ax.set_axis_off()
        folder = Path(self.tt_logger.save_dir) / self.tt_logger.name / \
            f'version_{self.tt_logger.version}' / 'predictions'
        folder.mkdir(exist_ok=True, parents=True)
        folder.chmod(0o755)

        fn = (folder /
              f'grid_epoch{trainer.current_epoch:03d}'
              f'_step{trainer.global_step:08d}.png')

        plt.savefig(fn, bbox_inches='tight')
        plt.close(fig)
        os.chmod(fn, 0o755)

    def on_train_batch_end(self, trainer, pl_module,
                           batch_output, batch, batch_idx):
        if trainer.global_step % self.every_n_steps == 0:
            grid = self._build_grid(pl_module)
            self._save_grid(grid, trainer)
