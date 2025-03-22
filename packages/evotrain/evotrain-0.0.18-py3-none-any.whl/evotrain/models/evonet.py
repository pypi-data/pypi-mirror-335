from typing import List, Optional, Union

import torch
import torch.nn as nn
from segmentation_models_pytorch.base import (
    SegmentationModel,
)
from segmentation_models_pytorch.base.initialization import initialize_decoder
from segmentation_models_pytorch.base.modules import Activation
from segmentation_models_pytorch.decoders.unet.decoder import UnetDecoder
from segmentation_models_pytorch.encoders import get_encoder

from evotrain import logistic


def initialize_head(module):
    for m in module.modules():
        if isinstance(m, (nn.Linear, nn.Conv2d)):
            print(f"Initializing {m}")
            nn.init.kaiming_uniform_(m.weight, mode="fan_in", nonlinearity="relu")
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)


class AdaptiveLogisticScalingLayer(nn.Module):
    def __init__(self, num_channels=1, k=None, L=None, x0=None, y0=None, s=None):
        super().__init__()
        self.identy = k is None  # no adaptive scaling

        # TODO: not really fixing these. provide a dict with a learnable param
        # If None, defaults and fixes the values
        default_L = 1
        default_x0 = 0
        default_y0 = -0.5
        default_s = 2

        self.k = nn.Parameter(k * torch.ones(num_channels)) if k is not None else None
        self.L = (
            nn.Parameter(L * torch.ones(num_channels))
            if L is not None
            else default_L * torch.ones(num_channels)
        )
        self.x0 = (
            nn.Parameter(x0 * torch.ones(num_channels))
            if x0 is not None
            else default_x0 * torch.ones(num_channels)
        )
        self.y0 = (
            nn.Parameter(y0 * torch.ones(num_channels))
            if y0 is not None
            else default_y0 * torch.ones(num_channels)
        )
        self.s = (
            nn.Parameter(s * torch.ones(num_channels))
            if s is not None
            else default_s * torch.ones(num_channels)
        )

    def forward(self, x):
        # Apply adaptive scaling per channel
        if self.identy:
            return x

        x = logistic(
            x,
            L=self.L.view(1, -1, 1, 1),
            k=self.k.view(1, -1, 1, 1),
            x0=self.x0.view(1, -1, 1, 1),
            y0=self.y0.view(1, -1, 1, 1),
            s=self.s.view(1, -1, 1, 1),
        )
        return x


class SpatialHead(nn.Module):
    def __init__(
        self,
        in_channels,
        filters_settings=None,
        activation=None,
    ):
        super().__init__()

        # Default settings for convolutional filters
        if filters_settings is None:
            filters_settings = {
                "kernel_size": [9, 7, 5, 3],
                "out_channels": [10, 10, 10, 10],
                "padding_mode": "reflect",
            }

        # Convolutional filters
        self.filters = nn.ModuleList(
            [
                nn.Conv2d(
                    in_channels,
                    filters_settings["out_channels"][i],
                    kernel_size=filters_settings["kernel_size"][i],
                    padding=filters_settings["kernel_size"][i] // 2,
                    padding_mode=filters_settings.get("padding_mode", "reflect"),
                )
                for i in range(len(filters_settings["out_channels"]))
            ]
        )

        self.activation = nn.ReLU() if activation == "relu" else Activation(activation)

        self.out_channels = sum(filters_settings["out_channels"])

    def forward(self, x):
        # Apply each convolutional filter
        out = [conv(x) for conv in self.filters]

        # Concatenate along the channel dimension
        x = torch.cat(out, dim=1)

        # apply activation to Convolutional output
        x = self.activation(x)

        return x


class MLPHead(nn.Module):
    def __init__(
        self,
        in_channels,
        out_channels,
        activation="identity",
        mlp_hidden_layers=(300, 200, 200, 100),
        dropout_prob=0.2,
        mlp_chunk_size=100_000,
    ):
        super().__init__()

        self.activation = Activation(activation)

        self.mlp = self._mlp_init(
            in_channels,
            out_channels,
            mlp_hidden_layers,
            dropout_prob,
        )
        self.mlp_chunk_size = mlp_chunk_size

    def _mlp_init(
        self,
        in_channels,
        out_channels,
        mlp_hidden_layers,
        dropout_prob,
    ):
        # Define the MLP
        mlp_layers = []
        input_dim = in_channels

        for hidden_units in mlp_hidden_layers:
            mlp_layers.append(nn.Linear(input_dim, hidden_units))
            mlp_layers.append(nn.ReLU())
            mlp_layers.append(nn.Dropout(p=dropout_prob))  # Add dropout after each ReLU
            input_dim = hidden_units

        # Final layer of MLP to output desired dimension
        mlp_layers.append(nn.Linear(input_dim, out_channels))
        mlp = nn.Sequential(*mlp_layers)
        return mlp

    def forward(self, x_conv, x_head, x_signal):
        # Concatenate with the head features
        x = torch.cat([x_conv, x_signal, x_head], dim=1)

        # Reshape for MLP
        batch_size, channels, height, width = x.shape
        x = x.view(
            batch_size, channels, height * width
        )  # Shape: (batch, 80, height * width)

        # Apply MLP to each spatial location independently
        x = x.permute(0, 2, 1)  # Shape: (batch, height * width, input_dim)
        x = self.mlp_forward_chunked(
            x, self.mlp_chunk_size
        )  # Shape: (batch, height * width, output_dim)

        # Reshape back to (batch, output_dim, height, width)
        x = x.permute(0, 2, 1).view(batch_size, -1, height, width)

        # Apply final activation
        x = self.activation(x)

        return x

    def mlp_forward_chunked(self, x, chunk_size=100_000):
        if chunk_size is None or x.shape[1] <= chunk_size:
            return self.mlp(x)

        chunks = [
            self.mlp(x[:, i : i + chunk_size, :])
            for i in range(0, x.shape[1], chunk_size)
        ]
        return torch.cat(chunks, dim=1)


class EvoNet(SegmentationModel):
    """Unet_ is a fully convolution neural network for image semantic segmentation. Consist of *encoder*
    and *decoder* parts connected with *skip connections*. Encoder extract features of different spatial
    resolution (skip connections) which are used by decoder to define accurate segmentation mask. Use *concatenation*
    for fusing decoder blocks with skip connections.

    Args:
        encoder_name: Name of the classification model that will be used as an encoder (a.k.a backbone)
            to extract features of different spatial resolution
        encoder_depth: A number of stages used in encoder in range [3, 5]. Each stage generate features
            two times smaller in spatial dimensions than previous one (e.g. for depth 0 we will have features
            with shapes [(N, C, H, W),], for depth 1 - [(N, C, H, W), (N, C, H // 2, W // 2)] and so on).
            Default is 5
        encoder_weights: One of **None** (random initialization), **"imagenet"** (pre-training on ImageNet) and
            other pretrained weights (see table with available weights for each encoder_name)
        decoder_channels: List of integers which specify **in_channels** parameter for convolutions used in decoder.
            Length of the list should be the same as **encoder_depth**
        decoder_use_batchnorm: If **True**, BatchNorm2d layer between Conv2D and Activation layers
            is used. If **"inplace"** InplaceABN will be used, allows to decrease memory consumption.
            Available options are **True, False, "inplace"**
        decoder_attention_type: Attention module used in decoder of the model. Available options are
            **None** and **scse** (https://arxiv.org/abs/1808.08127).
        in_channels: A number of input channels for the model, default is 3 (RGB images)
        classes: A number of classes for output mask (or you can think as a number of channels of output mask)
        activation: An activation function to apply after the final convolution layer.
            Available options are **"sigmoid"**, **"softmax"**, **"logsoftmax"**, **"tanh"**, **"identity"**,
                **callable** and **None**.
            Default is **None**
        aux_params: Dictionary with parameters of the auxiliary output (classification head). Auxiliary output is build
            on top of encoder if **aux_params** is not **None** (default). Supported params:
                - classes (int): A number of classes
                - pooling (str): One of "max", "avg". Default is "avg"
                - dropout (float): Dropout factor in [0, 1)
                - activation (str): An activation function to apply "sigmoid"/"softmax"
                    (could be **None** to return logits)

    Returns:
        ``torch.nn.Module``: Unet

    .. _Unet:
        https://arxiv.org/abs/1505.04597

    """

    def __init__(
        self,
        encoder_name: str = "mobilenet_v2",
        encoder_depth: int = 5,
        encoder_weights: Optional[str] = None,
        decoder_use_batchnorm: bool = True,
        decoder_channels: List[int] = (256, 128, 64, 32, 16),
        decoder_attention_type: Optional[str] = None,
        in_channels_spatial: int = 3,
        in_channels_head: int = 11,  # 6 meteo, 3 xyz, 2 time
        out_channels: int = 1,
        activation_spatial: Optional[str] = None,
        activation_mlp: Optional[Union[str, callable]] = None,
        spatial_filters_settings: dict = None,
        mlp_hidden_layers: tuple = (300, 200, 200, 100),
        dropout_prob: float = 0.2,
        mlp_chunk_size: int = 100_000,
        adaptive_scaling_spatial_params: dict = None,
        adaptive_scaling_mlp_params: dict = None,
        **kwargs,
    ):
        super().__init__()

        self.encoder = get_encoder(
            encoder_name,
            in_channels=in_channels_spatial,
            depth=encoder_depth,
            weights=encoder_weights,
        )

        self.decoder = UnetDecoder(
            encoder_channels=self.encoder.out_channels,
            decoder_channels=decoder_channels,
            n_blocks=encoder_depth,
            use_batchnorm=decoder_use_batchnorm,
            center=True if encoder_name.startswith("vgg") else False,
            attention_type=decoder_attention_type,
        )

        self.spatial_head = SpatialHead(
            in_channels=decoder_channels[-1],
            filters_settings=spatial_filters_settings,
            activation=activation_spatial,
        )

        mlp_in_channels = (
            self.spatial_head.out_channels + in_channels_head + in_channels_spatial
        )

        self.mlp_head = MLPHead(
            in_channels=mlp_in_channels,
            out_channels=out_channels,
            activation=activation_mlp,
            mlp_hidden_layers=mlp_hidden_layers,
            dropout_prob=dropout_prob,
            mlp_chunk_size=mlp_chunk_size,
        )

        adaptive_scaling_spatial_params = (
            adaptive_scaling_spatial_params
            if adaptive_scaling_spatial_params is not None
            else {}
        )

        adaptive_scaling_mlp_params = (
            adaptive_scaling_mlp_params
            if adaptive_scaling_mlp_params is not None
            else {}
        )

        self.scaler_spatial = AdaptiveLogisticScalingLayer(
            **adaptive_scaling_spatial_params
        )
        self.scaler_mlp = AdaptiveLogisticScalingLayer(**adaptive_scaling_mlp_params)

        self.classification_head = None

        self.name = "u-{}".format(encoder_name)
        self.initialize()

    def forward_unet(self, x_signal):
        self.check_input_shape(x_signal)
        unet_features = self.encoder(self.scaler_spatial(x_signal))
        decoder_output = self.decoder(*unet_features)
        return decoder_output

    def forward_spatial(self, x_signal):
        spatial_features = self.spatial_head(self.forward_unet(x_signal))
        return spatial_features

    def forward(self, x_signal, x_head, return_spatial_features=False):
        spatial_features = self.forward_spatial(x_signal)
        probs = self.mlp_head.forward(
            spatial_features, x_head, self.scaler_mlp(x_signal)
        )

        if return_spatial_features:
            return probs, spatial_features
        else:
            return probs

    @torch.no_grad()
    def predict(
        self,
        feats,
        head,
        pad=64,
        padding_mode="reflect",
        return_spatial_features=False,
    ):
        """Inference method. Switch model to `eval` mode, call `.forward(x)` with `torch.no_grad()`
        Adds padding to the input array, then removes it from the output.

        Args:
            arr: 3D numpy array with shape (channels, height, width)
            arr_head: 3D numpy array with shape (channels, height, width)
            pad: int, padding size
            padding_mode: str, padding mode for torch.nn.functional.pad

        Return:
            prediction: 3D numpy array with shape (classes, height, width)

        """
        if self.training:
            self.eval()

        feats = torch.from_numpy(feats).float()
        head = torch.from_numpy(head).float()

        rows, cols = feats.shape[-2:]

        rows_rem = (rows + 2 * pad) % 32
        cols_rem = (cols + 2 * pad) % 32

        pad_rows_1 = pad
        pad_rows_2 = pad + (32 - rows_rem) if rows_rem > 0 else pad

        pad_cols_1 = pad
        pad_cols_2 = pad + (32 - cols_rem) if cols_rem > 0 else pad

        torch_pad = (pad_cols_1, pad_cols_2, pad_rows_1, pad_rows_2)

        feats = feats.unsqueeze(0)
        feats = torch.nn.functional.pad(feats, torch_pad, mode=padding_mode)

        head = head.unsqueeze(0)
        head = torch.nn.functional.pad(head, torch_pad, mode=padding_mode)

        if return_spatial_features:
            probs, conv = self.forward(
                feats, head, return_spatial_features=return_spatial_features
            )
            probs = probs[..., pad_rows_1:-pad_rows_2, pad_cols_1:-pad_cols_2]
            conv = conv[..., pad_rows_1:-pad_rows_2, pad_cols_1:-pad_cols_2]
            return probs[0].numpy(), conv[0].numpy()
        else:
            probs = self.forward(
                feats, head, return_spatial_features=return_spatial_features
            )
            probs = probs[..., pad_rows_1:-pad_rows_2, pad_cols_1:-pad_cols_2]
            return probs[0].numpy()

    def initialize(self):
        initialize_decoder(self.decoder)
        initialize_head(self.spatial_head)
        initialize_head(self.mlp_head)
