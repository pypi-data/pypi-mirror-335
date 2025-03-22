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


def initialize_head(module):
    for m in module.modules():
        if isinstance(m, (nn.Linear, nn.Conv2d)):
            print(f"Initializing {m}")
            nn.init.kaiming_uniform_(m.weight, mode="fan_in", nonlinearity="relu")
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)


class MultiConvSegmentationHead(nn.Module):
    def __init__(
        self,
        in_channels,
        in_head_channels,
        out_channels,
        head_filters_settings=None,
        activation=None,
        activation_conv=None,
        mlp_hidden_layers=(300, 200, 200, 100),
        dropout_prob=0.2,
    ):
        super().__init__()

        # Default settings for convolutional filters
        if head_filters_settings is None:
            head_filters_settings = {
                "kernel_size": [9, 7, 5, 3],
                "out_channels": [20, 20, 20, 20],
                "padding_mode": "reflect",
            }

        # Convolutional filters
        self.filters = nn.ModuleList(
            [
                nn.Conv2d(
                    in_channels,
                    head_filters_settings["out_channels"][i],
                    kernel_size=head_filters_settings["kernel_size"][i],
                    padding=head_filters_settings["kernel_size"][i] // 2,
                    padding_mode=head_filters_settings.get("padding_mode", "reflect"),
                )
                for i in range(len(head_filters_settings["out_channels"]))
            ]
        )

        self.activation_conv = (
            nn.ReLU() if activation_conv == "relu" else Activation(activation_conv)
        )
        self.activation = Activation(activation)

        self.mlp = self._mlp_init(
            in_channels,
            in_head_channels,
            head_filters_settings,
            out_channels,
            mlp_hidden_layers,
            dropout_prob,
        )

    def _mlp_channels(self, in_channels, in_head_channels, head_filters_settings):
        # Calculate the number of input channels for the MLP
        input_dim = in_head_channels
        for out in head_filters_settings["out_channels"]:
            input_dim += out
        return input_dim

    def _mlp_init(
        self,
        in_channels,
        in_head_channels,
        head_filters_settings,
        out_channels,
        mlp_hidden_layers,
        dropout_prob,
    ):
        # Define the MLP
        mlp_layers = []
        input_dim = self._mlp_channels(
            in_channels, in_head_channels, head_filters_settings
        )

        for hidden_units in mlp_hidden_layers:
            mlp_layers.append(nn.Linear(input_dim, hidden_units))
            mlp_layers.append(nn.ReLU())
            mlp_layers.append(nn.Dropout(p=dropout_prob))  # Add dropout after each ReLU
            input_dim = hidden_units

        # Final layer of MLP to output desired dimension
        mlp_layers.append(nn.Linear(input_dim, out_channels))
        mlp = nn.Sequential(*mlp_layers)
        return mlp

    def forward_conv(self, x):
        # Apply each convolutional filter
        out = [conv(x) for conv in self.filters]

        # Concatenate along the channel dimension
        x = torch.cat(out, dim=1)

        # apply activation to Convolutional output
        x = self.activation_conv(x)

        return x

    def forward_mlp(self, x_conv, x_head):
        # Concatenate with the head features
        x = torch.cat([x_conv, x_head], dim=1)

        # Reshape for MLP
        batch_size, channels, height, width = x.shape
        x = x.view(
            batch_size, channels, height * width
        )  # Shape: (batch, 80, height * width)

        # Apply MLP to each spatial location independently
        x = x.permute(0, 2, 1)  # Shape: (batch, height * width, 80)
        x = self.mlp(x)  # Shape: (batch, height * width, output_dim)

        # Reshape back to (batch, output_dim, height, width)
        x = x.permute(0, 2, 1).view(batch_size, -1, height, width)

        # Apply final activation
        x = self.activation(x)

        return x

    def forward(self, x, x_head):
        x_conv = self.forward_conv(x)
        x = self.forward_mlp(x_conv, x_head)
        return x


class LcmUnet(SegmentationModel):
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
        encoder_name: str = "resnet34",
        encoder_depth: int = 5,
        encoder_weights: Optional[str] = "imagenet",
        decoder_use_batchnorm: bool = True,
        decoder_channels: List[int] = (256, 128, 64, 32, 16),
        decoder_attention_type: Optional[str] = None,
        in_channels: int = 3,
        classes: int = 1,
        activation: Optional[Union[str, callable]] = None,
        activation_conv: Optional[str] = None,
        in_head_channels: int = 0,
        head_filters_settings: dict = None,
        mlp_hidden_layers: tuple = (300, 200, 200, 100),
        dropout_prob: float = 0.2,
    ):
        super().__init__()

        self.encoder = get_encoder(
            encoder_name,
            in_channels=in_channels,
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

        self.segmentation_head = self.SegmentationHead(
            in_channels=decoder_channels[-1],
            in_head_channels=in_head_channels,
            head_filters_settings=head_filters_settings,
            activation=activation,
            activation_conv=activation_conv,
            mlp_hidden_layers=mlp_hidden_layers,
            dropout_prob=dropout_prob,
            out_channels=classes,
        )

        self.classification_head = None

        self.name = "u-{}".format(encoder_name)
        self.initialize()

    @property
    def SegmentationHead(self):
        return MultiConvSegmentationHead

    def forward(self, x_signal, x_head, return_conv=False):
        """Sequentially pass `x` trough model`s encoder, decoder and heads"""
        self.check_input_shape(x_signal)

        features = self.encoder(x_signal)
        decoder_output = self.decoder(*features)

        x_conv = self.segmentation_head.forward_conv(decoder_output)
        masks = self.segmentation_head.forward_mlp(x_conv, x_head, x_signal)

        # masks = self.segmentation_head(decoder_output, x_head)
        if return_conv:
            return masks, x_conv

        return masks

    @torch.no_grad()
    def predict_tensor(self, x, x_head):
        """Inference method. Switch model to `eval` mode, call `.forward(x)` with `torch.no_grad()`

        Args:
            x: 4D torch tensor with shape (batch_size, channels, height, width)

        Return:
            prediction: 4D torch tensor with shape (batch_size, classes, height, width)

        """
        if self.training:
            self.eval()

        x = self.forward(x, x_head)

        return x

    @torch.no_grad()
    def predict(self, feats, head, pad=64, padding_mode="reflect", return_conv=False):
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

        if return_conv:
            probs, conv = self.forward(feats, head, return_conv=return_conv)
            probs = probs[..., pad_rows_1:-pad_rows_2, pad_cols_1:-pad_cols_2]
            conv = conv[..., pad_rows_1:-pad_rows_2, pad_cols_1:-pad_cols_2]
            return probs[0].numpy(), conv[0].numpy()
        else:
            probs = self.forward(feats, head, return_conv=return_conv)
            probs = probs[..., pad_rows_1:-pad_rows_2, pad_cols_1:-pad_cols_2]
            return probs[0].numpy()

    def initialize(self):
        initialize_decoder(self.decoder)
        initialize_head(self.segmentation_head)


class MultiConvSegmentationHeadV2(MultiConvSegmentationHead):
    def forward_mlp(self, x_conv, x_head, x_signal):
        x_conv = torch.cat([x_conv, x_signal], dim=1)
        return super().forward_mlp(x_conv, x_head)

    def forward(self, x_decoder, x_head, x_signal):
        x_conv = self.forward_conv(x_decoder)
        x = self.forward_mlp(x_conv, x_head, x_signal)
        return x

    def _mlp_channels(self, in_channels, in_head_channels, head_filters_settings):
        # Calculate the number of input channels for the MLP
        input_dim = in_head_channels + in_channels
        for out in head_filters_settings["out_channels"]:
            input_dim += out
        # return input_dim TODO: fix this
        return 33


class LcmUnetV2(LcmUnet):
    @property
    def SegmentationHead(self):
        return MultiConvSegmentationHeadV2

    def forward(self, x_signal, x_head, return_conv=False):
        """Sequentially pass `x` trough model`s encoder, decoder and heads"""
        self.check_input_shape(x_signal)

        features = self.encoder(x_signal)
        decoder_output = self.decoder(*features)

        x_conv = self.segmentation_head.forward_conv(decoder_output)
        masks = self.segmentation_head.forward_mlp(x_conv, x_head, x_signal)

        if return_conv:
            return masks, x_conv

        return masks


class DualEncoderLcmUnet(SegmentationModel):
    def __init__(
        self,
        encoder1_name: str = "resnet34",
        encoder2_name: str = "resnet34",
        encoder_depth: int = 5,
        encoder_weights: Optional[str] = "imagenet",
        decoder_use_batchnorm: bool = True,
        decoder_channels: List[int] = (256, 128, 64, 32, 16),
        decoder_attention_type: Optional[str] = None,
        in_channels1: int = 20,  # First 20 bands
        in_channels2: int = 16,  # Other 16 bands
        classes: int = 1,
        activation: Optional[Union[str, callable]] = None,
        activation_conv: Optional[str] = None,
        in_head_channels: int = 0,
        head_filters_settings: dict = None,
        mlp_hidden_layers: tuple = (300, 200, 200, 100),
        dropout_prob: float = 0.2,
    ):
        super().__init__()

        # Two separate encoders
        self.encoder1 = get_encoder(
            encoder1_name,
            in_channels=in_channels1,
            depth=encoder_depth,
            weights=encoder_weights,
        )

        self.encoder2 = get_encoder(
            encoder2_name,
            in_channels=in_channels2,
            depth=encoder_depth,
            weights=encoder_weights,
        )

        # Modify decoder to handle combined features
        # We need to adjust the input channels as we'll be combining features from both encoders
        combined_channels = [
            ch1 + ch2
            for ch1, ch2 in zip(self.encoder1.out_channels, self.encoder2.out_channels)
        ]

        self.decoder = UnetDecoder(
            encoder_channels=combined_channels,
            decoder_channels=decoder_channels,
            n_blocks=encoder_depth,
            use_batchnorm=decoder_use_batchnorm,
            center=True if encoder1_name.startswith("vgg") else False,
            attention_type=decoder_attention_type,
        )

        self.segmentation_head = self.SegmentationHead(
            in_channels=decoder_channels[-1],
            in_head_channels=in_head_channels,
            head_filters_settings=head_filters_settings,
            activation=activation,
            activation_conv=activation_conv,
            mlp_hidden_layers=mlp_hidden_layers,
            dropout_prob=dropout_prob,
            out_channels=classes,
        )

        self.classification_head = None
        self.name = f"dual-u-{encoder1_name}-{encoder2_name}"
        self.initialize()

    @property
    def SegmentationHead(self):
        return MultiConvSegmentationHead

    def forward(self, x_signal, x_head, return_conv=False):
        """Forward pass with split input processing"""
        # Split the input signal into two parts
        x_signal1 = x_signal[:, :20]  # First 20 bands
        x_signal2 = x_signal[:, 20:]  # Remaining 16 bands

        # Get features from both encoders
        features1 = self.encoder1(x_signal1)
        features2 = self.encoder2(x_signal2)

        # Combine features from both encoders
        combined_features = [
            torch.cat([f1, f2], dim=1) for f1, f2 in zip(features1, features2)
        ]

        # Process through decoder
        decoder_output = self.decoder(*combined_features)

        # Process through segmentation head
        x_conv = self.segmentation_head.forward_conv(decoder_output)
        masks = self.segmentation_head.forward_mlp(x_conv, x_head)

        if return_conv:
            return masks, x_conv

        return masks

    def predict(self, feats, head, pad=64, padding_mode="reflect", return_conv=False):
        """Modified predict method to handle the split input"""
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

        if return_conv:
            probs, conv = self.forward(feats, head, return_conv=return_conv)
            probs = probs[..., pad_rows_1:-pad_rows_2, pad_cols_1:-pad_cols_2]
            conv = conv[..., pad_rows_1:-pad_rows_2, pad_cols_1:-pad_cols_2]
            return probs[0].numpy(), conv[0].numpy()
        else:
            probs = self.forward(feats, head, return_conv=return_conv)
            probs = probs[..., pad_rows_1:-pad_rows_2, pad_cols_1:-pad_cols_2]
            return probs[0].numpy()

    def initialize(self):
        initialize_decoder(self.decoder)
        initialize_head(self.segmentation_head)


class DualEncoderLcmUnetV2(DualEncoderLcmUnet):
    @property
    def SegmentationHead(self):
        return MultiConvSegmentationHeadV2

    def forward(self, x_signal, x_head, return_conv=False):
        """Forward pass with split input processing and V2 features"""
        # Split the input signal into two parts
        x_signal1 = x_signal[:, :20]  # First 20 bands
        x_signal2 = x_signal[:, 20:]  # Remaining 16 bands

        # Get features from both encoders
        features1 = self.encoder1(x_signal1)
        features2 = self.encoder2(x_signal2)

        # Combine features from both encoders
        combined_features = [
            torch.cat([f1, f2], dim=1) for f1, f2 in zip(features1, features2)
        ]

        # Process through decoder
        decoder_output = self.decoder(*combined_features)

        # Process through segmentation head with V2 features
        x_conv = self.segmentation_head.forward_conv(decoder_output)
        masks = self.segmentation_head.forward_mlp(x_conv, x_head, x_signal)

        if return_conv:
            return masks, x_conv

        return masks
