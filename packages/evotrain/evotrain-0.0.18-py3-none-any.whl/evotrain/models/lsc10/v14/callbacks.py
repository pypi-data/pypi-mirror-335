import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytorch_lightning as pl
import torch
import torchvision
from dataset import EvoNetV1Dataset
from evotrain.models.lsc10.v14.labels import (LSC_COVER_LABELS, LSC_OCCLUSION_LABELS, LSC_ECOSYSTEM_LABELS)

from evotrain.models.lsc10.v14.labels import batch_probs_to_rgb
from evotrain.models.lsc10 import day_of_year_cyclic_feats


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


def load_target_probs(val_dataset, sample_id):
    # try:
    # target_probs = val_dataset.read_evov1_target(location_id)
    prob_cover, prob_occlusion, prob_eco, weight_cover, weight_occlusion, weight_eco = val_dataset.read_evov1_target(sample_id)
    
    # prob_cover = val_dataset.evo_dataset.read_annotation(
    #     sample_id, annotation_name="lsc-evo-v1-prob-cover-v1"
    # )
    # prob_occlusion = val_dataset.evo_dataset.read_annotation(
    #     sample_id, annotation_name="lsc-evo-v1-prob-occlusion-v1"
    # )
    # prob_eco = val_dataset.evo_dataset.read_annotation(
    #     sample_id, annotation_name="lsc-evo-v1-prob-eco-v1"
    # )
    # except Exception:
        # logger.error(
        #     f"Error reading evo target for location {location_id}"
        # )
        # target_probs = val_dataset.read_worldcover2021_target(location_id)
    return [prob_cover, prob_occlusion, prob_eco, weight_cover, weight_occlusion, weight_eco]


class InferencePreview(pl.Callback):
    def __init__(
        self,
        val_dataset: EvoNetV1Dataset,
        tt_logger,
        val_ids=8,
        years=[2020],
        every_n_steps=1000,
        rgb_ids=None,
        augmented_scaling=False,
        augmented_scaling_params=None,
    ):
        super().__init__()

        # if years is None:
        #     years = list(range(2018, 2023))
        self.years = years
        self.components = ['cover', 'occlusion', 'ecosystem']

        self.bands = val_dataset.bands
    
        self.labels = {'cover': LSC_COVER_LABELS,
                       'occlusion': LSC_OCCLUSION_LABELS,
                       'ecosystem': LSC_ECOSYSTEM_LABELS}
        self.every_n_steps = every_n_steps
        self.tt_logger = tt_logger

        self.rgb_ids = rgb_ids or [
            self.bands.index(b) for b in val_dataset.bands_rgb
        ]

        self.augmented_scaling = augmented_scaling
        self.augmented_scaling_params = augmented_scaling_params

        if val_ids is None:
            val_ids = 8

        self.sample_ids = self._sample_ids(val_dataset, val_ids)
        (
            self.feats_years,
            self.feats_head_year,
            self.target_prob_cover, 
            self.target_prob_occlusion, 
            self.target_prob_eco,            
            self.weight_prob_cover, 
            self.weight_prob_occlusion, 
            self.weight_prob_eco
        ) = self._load_feats_targets(val_dataset, self.sample_ids)

    def _sample_ids(self, val_dataset, val_ids):
        """Return location_ids to display"""

        if isinstance(val_ids, int):
            sample_ids = val_dataset.evo_dataset.sample_ids.sample(
                val_ids, random_state=0
            ).values.tolist()
        elif isinstance(val_ids, (list, tuple)):
            sample_ids = val_dataset.evo_dataset.sample_ids
            sample_ids = sample_ids[
                sample_ids.isin(val_ids)
            ].values.tolist()
            if len(sample_ids.size) != len(val_ids):
                not_found = [lc for lc in val_ids if lc not in sample_ids]
                raise ValueError(
                    f"The following location_ids could not be "
                    "found in the validation dataset: "
                    f"{not_found}"
                )
        else:
            TypeError(
                f"`val_ids` is of type: {type(val_ids)}. "
                "Expected list or tuple of location_ids or integer"
            )

        return sample_ids

    def _load_feats_targets(self, val_dataset: EvoNetV1Dataset, sample_ids):
        """Loads dictionary of feats tensors (years are the keys for each
        year batch) and the target features, which are the same for all
        years."""

        # years = self.years
        # feats = {}
        # feats_head = {}
        # for year in years:
        feats = torch.from_numpy(
                np.array(
                    [
                        val_dataset.read_feats(
                            sample_id,
                            # year,
                            val_dataset.bands,
                            augmented_scaling=True,  # noqa: E501
                            augmented_scaling_params=val_dataset._augmented_scaling_params,
                        ).data  # noqa: E501
                        for sample_id in sample_ids
                    ]
                )
            )

        # for year in years:
#         location_ids = ["_".join(sample_id.split("_")[:-1]) for sample_id in sample_ids]
        
        list_feats_head = []
        for sample_id in sample_ids:
            location_id = "_".join(sample_id.split("_")[:-1])
            head = val_dataset.evov2_dataset.read_head_features(
                            location_id,
                            val_dataset.reference_year,
                            meteo_jitter=0,
                            latlon_jitter=0
                        )  # noqa: E501
            doy = day_of_year_cyclic_feats(sample_id, 0)
            head = np.concatenate((head, doy), axis=0).astype(
                np.float32
            )
            list_feats_head.append(head)
        feats_head = torch.from_numpy(
            np.array(list_feats_head))
            
        
        
        # feats_head = torch.from_numpy(
        #         np.array(
        #             [
        #                 val_dataset.evov2_dataset.read_head_features(
        #                     location_id,
        #                     val_dataset.reference_year,
        #                     meteo_jitter=0,
        #                     latlon_jitter=0
        #                 )  # noqa: E501
        #                 for location_id in location_ids
        #             ]
        #         )
        #     )

        # target is the same (worldcover_2021), load from year 0
        target_prob_cover = []
        target_prob_occlusion = []
        target_prob_eco = []
        weight_prob_cover = []
        weight_prob_occlusion = []
        weight_prob_eco = []
        for sample_id in sample_ids:                   
            _prob_cover, _prob_occlusion, _prob_eco, _weight_cover, _weight_occlusion, _weight_eco = load_target_probs(val_dataset, sample_id) 
            target_prob_cover.append(_prob_cover)
            target_prob_occlusion.append(_prob_occlusion)
            target_prob_eco.append(_prob_eco)
            weight_prob_cover.append(_weight_cover)
            weight_prob_occlusion.append(_weight_occlusion)
            weight_prob_eco.append(_weight_eco)
            
        # worldcover_2021 = [
        #     val_dataset.read_worldcover2021_target(loc_id)
        #     for loc_id in location_ids
        # ]

        target_prob_cover = torch.from_numpy(np.array(target_prob_cover))
        target_prob_occlusion = torch.from_numpy(np.array(target_prob_occlusion))
        target_prob_eco = torch.from_numpy(np.array(target_prob_eco))
        
        weight_prob_cover = torch.from_numpy(np.array(weight_prob_cover))
        weight_prob_occlusion = torch.from_numpy(np.array(weight_prob_occlusion))
        weight_prob_eco = torch.from_numpy(np.array(weight_prob_eco))
        # worldcover_2021 = torch.from_numpy(np.array(worldcover_2021))
        return feats, feats_head, target_prob_cover, target_prob_occlusion, target_prob_eco, weight_prob_cover, weight_prob_occlusion, weight_prob_eco

    def _predicted_rgb(self, pl_module, feats, feats_head):
        val_images = feats.to(pl_module.device)
        val_images_head = feats_head.to(pl_module.device)
        with torch.no_grad():
            pl_module.eval()
            predicted = pl_module(val_images, val_images_head)
            pl_module.train()
            predicted = [p.cpu() for p in predicted]

        predicted = [batch_probs_to_rgb(p, self.labels[comp], comp) for p, comp in zip(predicted, self.components)]

        return predicted

    def _targets_rgb(self, targets):
        targets = [self.target_prob_cover,
                   self.target_prob_occlusion,
                   self.target_prob_eco]
        weights = [self.weight_prob_cover,
                   self.weight_prob_occlusion,
                   self.weight_prob_eco]
        nodata_masks = [(m[:,0,:,:]< 0.1).squeeze() for m in weights
        ]
        targets_rgb = [self._masked_batch_probs_to_rgb(p, mask, self.labels[comp], comp ) for p, mask, comp in zip(targets, nodata_masks, self.components)]
        return targets_rgb
    
    def _masked_batch_probs_to_rgb(self, prob, masks, labs, component):
        rgb_unmasked = batch_probs_to_rgb(prob, labs, component) 
        list_ims = []
        for im, mask in zip(rgb_unmasked, masks):
            im[:,mask] = 0
            list_ims.append(im)
        rgb = torch.from_numpy(np.array(list_ims))
        return rgb

    def _feats_rgb(self, feats):
        feats_rgb = feats[:, self.rgb_ids, ...].cpu()
        feats_rgb = scale_minmax_batch(feats_rgb)
        return feats_rgb

    def _build_grid(self, pl_module):
        feats_years = self.feats_years
        # target_prob_cover = self.target_prob_cover 
        # target_prob_occlusion = self.target_prob_occlusion, 
        # target_prob_eco = self.target_prob_eco
        n_rows = len(self.sample_ids)

        # for each location there is an element of the batch
        feats_rgb = {}
        predicted_rgb = {}
        targets = [self.target_prob_cover,
                   self.target_prob_occlusion,
                   self.target_prob_eco]
        targets_rgb = self._targets_rgb(targets)
        
        from loguru import logger
        logger.info(f'feats: {self.feats_years.shape}')
        logger.info(f'feats_head_year: {self.feats_head_year.shape}')
        logger.info(f'target_prob_cover: {self.target_prob_cover.shape}')

        # for year in self.years:
        predicted_rgb = self._predicted_rgb(
                pl_module, feats_years, self.feats_head_year
            )
        feats_rgb = self._feats_rgb(feats_years)

        # for each batch/location_id we have a row, with each year feats,
        # the prediction and finally the target
        images = []
        for sample_id in range(n_rows):
            # for year in self.years:
            images.append(feats_rgb[sample_id])
            images.append(predicted_rgb[0][sample_id])
            images.append(targets_rgb[0][sample_id])
            images.append(predicted_rgb[1][sample_id])
            images.append(targets_rgb[1][sample_id])
            images.append(predicted_rgb[2][sample_id])
            images.append(targets_rgb[2][sample_id])

        grid = torchvision.utils.make_grid(
            images, nrow=(len(images) // n_rows)
        )
        return grid

    def _save_grid(self, combined_grid, trainer):
        fig, ax = plt.subplots(figsize=(14, 20))
        ax.imshow(combined_grid.permute(1, 2, 0).cpu())
        ax.set_title(
            f"epoch: {trainer.current_epoch:03d} - "
            f"step: {trainer.global_step / 1000:.02f}K"
        )
        ax.set_axis_off()
        folder = (
            Path(self.tt_logger.save_dir)
            / self.tt_logger.name
            / f"version_{self.tt_logger.version}"
            / "predictions"
        )
        folder.mkdir(exist_ok=True, parents=True)
        folder.chmod(0o755)

        fn = (
            folder / f"grid_epoch{trainer.current_epoch:03d}"
            f"_step{trainer.global_step:08d}.png"
        )

        plt.savefig(fn, bbox_inches="tight")
        plt.close(fig)
        os.chmod(fn, 0o755)

    def on_train_batch_end(
        self, trainer, pl_module, batch_output, batch, batch_idx
    ):
        if trainer.global_step in [1, 10, 100, 200]:
            # sanity checks on first steps
            grid = self._build_grid(pl_module)
            self._save_grid(grid, trainer)

        if trainer.global_step % self.every_n_steps == 0:
            grid = self._build_grid(pl_module)
            self._save_grid(grid, trainer)

    def on_train_epoch_end(self, trainer, pl_module):
        grid = self._build_grid(pl_module)
        self._save_grid(grid, trainer)
