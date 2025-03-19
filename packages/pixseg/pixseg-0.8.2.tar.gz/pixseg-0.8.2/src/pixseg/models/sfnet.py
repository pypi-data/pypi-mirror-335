"""Implementation of SFNet

Since this use the FPN architecture, the implementation is very similar to UPerNet
"""

import torch
from torch import Tensor, nn
from torch.hub import load_state_dict_from_url
from torch.nn import functional as F
from torchvision.models.resnet import (
    ResNet18_Weights,
    ResNet101_Weights,
    resnet18,
    resnet101,
)

from ..datasets import CITYSCAPES_LABELS, VOC_LABELS
from .backbones import ResNetBackbone
from .model_registry import SegWeights, SegWeightsEnum, register_model
from .model_utils import _generate_docstring, _validate_weights_input
from .pspnet import PyramidPoolingModule


class ConvNormAct(nn.Sequential):
    def __init__(
        self, in_channels: int, out_channels: int, kernel_size: int, stride: int = 1
    ):
        super().__init__(
            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size,
                padding=kernel_size // 2,
                stride=stride,
                bias=False,
            ),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )


#####
# region FAM
#####


def pair_grid(xs: Tensor, ys: Tensor):
    """Return a pairing grid of shape (X, Y, 2) given 1d tensors. Element at [i, j] is (y, x)"""
    grid_x, grid_y = torch.meshgrid(xs, ys, indexing="ij")
    return torch.stack((grid_y, grid_x), dim=-1)


def flow_warp(x: Tensor, flow_field: Tensor) -> Tensor:
    """Wrap the input according to the flow

    Args:
        x (Tensor (N, C, H, W)): Input tensor
        flow_field (Tensor (N, 2, FH, FW)): Relative offset on a normalized grid
            of `x`, i.e. element at *[n, :, x, y]* decides how the coordinates of `x`
            after normalizing to range (-1, 1) should flow.
    """
    FH, FW = flow_field.shape[-2:]
    assert flow_field.size(1) == 2, "flow_field should only has 2 channels"

    # make normalized coordinate grid
    fh_space = torch.linspace(-1.0, 1.0, FH)
    fw_space = torch.linspace(-1.0, 1.0, FW)
    coord_grid = pair_grid(fh_space, fw_space).to(x.device)

    field_size = torch.tensor([FW, FH], device=flow_field.device)
    norm_field = flow_field.permute(0, 2, 3, 1) / field_size
    coord_grid = coord_grid + norm_field
    output = F.grid_sample(x, coord_grid, align_corners=True)
    return output.to(x.dtype)


class FlowAlignmentModule(nn.Module):
    """Quoted from the paper:

    > ... align feature maps of two adjacent levels by predicting a flow field
    inside the network
    """

    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.down_high = nn.Conv2d(in_channels, out_channels, 1, bias=False)
        self.down_low = nn.Conv2d(in_channels, out_channels, 1, bias=False)
        self.flow_make = nn.Conv2d(out_channels * 2, 2, 3, padding=1, bias=False)

    def forward(self, low_feature: Tensor, high_feature: Tensor):
        """low_feature has larger spatial dimension and finer features"""
        output_size = low_feature.shape[2:]
        low_out = self.down_low(low_feature)
        high_out = self.down_high(high_feature)
        high_out = F.interpolate(
            high_out, output_size, mode="bilinear", align_corners=True
        )
        flow = self.flow_make(torch.cat([high_out, low_out], dim=1))
        out = flow_warp(high_feature, flow)
        return out


#####
# region Head
#####


class SFNetHead(nn.Module):
    def __init__(
        self,
        out_channels: int,
        feature_channels: dict[str, int],
        fpn_channels: int,
        enable_dsn=False,
    ):
        super().__init__()
        fpn_keys = list(feature_channels.keys())[:-1]  # last layer is not needed
        self.fpn_ins = nn.ModuleDict()
        self.fpn_outs = nn.ModuleDict()
        self.fams = nn.ModuleDict()
        for k in fpn_keys:
            self.fpn_ins[k] = ConvNormAct(feature_channels[k], fpn_channels, 1)
            self.fpn_outs[k] = ConvNormAct(fpn_channels, fpn_channels, 3)
            self.fams[k] = FlowAlignmentModule(
                in_channels=fpn_channels, out_channels=fpn_channels // 2
            )

        self.dsns = None
        if enable_dsn:
            self.dsns = nn.ModuleDict()
            for k in fpn_keys:
                self.dsns[k] = nn.Sequential(
                    ConvNormAct(fpn_channels, fpn_channels, 3),
                    nn.Dropout2d(0.1),
                    nn.Conv2d(fpn_channels, out_channels, kernel_size=1, bias=True),
                )

        self.final_conv = nn.Sequential(
            ConvNormAct(len(feature_channels) * fpn_channels, fpn_channels, 3),
            nn.Conv2d(fpn_channels, out_channels, kernel_size=1),
        )

    def forward(
        self, feature_maps: dict[str, Tensor]
    ) -> tuple[Tensor, list[Tensor] | None]:
        last_feature = list(feature_maps.values())[-1]
        layer_outs: dict[str, Tensor] = {}
        layer_acc = last_feature  # accumulate layers
        reverse_fpn_keys = list(feature_maps.keys())[-2::-1]  # also skip last key
        for k in reverse_fpn_keys:
            feature = feature_maps[k]
            feature_out = self.fpn_ins[k](feature)
            fam_out = self.fams[k](feature_out, layer_acc)
            layer_acc = feature_out + fam_out
            layer_outs[k] = layer_acc

        fpn_features = [last_feature]
        fpn_features += [self.fpn_outs[k](out) for k, out in layer_outs.items()]
        dsn_outs: list[Tensor] | None = None
        if self.dsns is not None:
            dsn_outs = [self.dsns[k](out) for k, out in layer_outs.items()]

        fpn_features.reverse()  # from 1/4 to 1/32 features
        # there can be FAMs during upsampling
        output_size = fpn_features[0].shape[2:]
        fusion_list = [fpn_features[0]]
        fusion_list += [
            F.interpolate(feat, output_size, mode="bilinear", align_corners=True)
            for feat in fpn_features[1:]
        ]

        fusion_out = torch.cat(fusion_list, 1)
        out = self.final_conv(fusion_out)
        return out, dsn_outs


#####
# region SFNet
#####


class SFNet(nn.Module):
    """Implement SFNet from [Semantic Flow for Fast and Accurate Scene
    Parsing](https://arxiv.org/abs/2002.10120)"""

    def __init__(
        self,
        num_classes: int,
        backbone: nn.Module,
        backbone_channels: dict[str, int],
        fpn_channels=128,
        enable_dsn=False,
    ) -> None:
        super().__init__()
        if enable_dsn:
            raise NotImplementedError("SFNet does not support dsn")

        self.backbone = backbone

        in_channels = list(backbone_channels.values())[-1]
        self.neck = PyramidPoolingModule(
            in_channels,
            fpn_channels,
            (1, 2, 3, 6),
            pool_channels=fpn_channels,
            dropout=0.1,
        )

        self.head = SFNetHead(
            num_classes,
            backbone_channels,
            fpn_channels=fpn_channels,
            enable_dsn=enable_dsn,
        )

    def forward(self, x: Tensor) -> dict[str, Tensor]:
        feature_maps: dict[str, Tensor] = self.backbone(x)
        last_key = list(feature_maps.keys())[-1]
        feature_maps[last_key] = self.neck(feature_maps[last_key])
        head_outs: tuple[Tensor, list[Tensor] | None] = self.head(feature_maps)
        main_out = F.interpolate(head_outs[0], size=x.shape[2:], mode="bilinear")
        return {"out": main_out}


class SFNet_ResNet18_Weights(SegWeightsEnum):
    CITYSCAPES = SegWeights(
        "sfnet/sfnet_resnet18-cityscapes-512x1024.pth",
        CITYSCAPES_LABELS,
        "Trained on Cityscapes (fine) dataset",
    )
    SBD = SegWeights(
        "sfnet/sfnet_resnet18-sbd-500x500.pth",
        VOC_LABELS,
        "Trained on Semantic Boundaries Dataset (SBD)",
    )
    DEFAULT = CITYSCAPES


class SFNet_ResNet101_Weights(SegWeightsEnum):
    CITYSCAPES = SegWeights(
        "sfnet/sfnet_resnet101-cityscapes-512x1024.pth",
        CITYSCAPES_LABELS,
        "Trained on Cityscapes (fine) dataset",
    )
    DEFAULT = CITYSCAPES


@_generate_docstring("Semantic Flow Network model with a ResNet-18 backbone")
@register_model()
def sfnet_resnet18(
    num_classes: int | None = None,
    weights: SFNet_ResNet18_Weights | str | None = None,
    progress: bool = True,
    weights_backbone: ResNet18_Weights | str | None = ResNet18_Weights.DEFAULT,
    **kwargs,
) -> SFNet:
    weights_model = SFNet_ResNet18_Weights.resolve(weights)
    weights_model, weights_backbone, num_classes = _validate_weights_input(
        weights_model, weights_backbone, num_classes
    )

    backbone_model = resnet18(weights=weights_backbone, progress=progress)
    backbone = ResNetBackbone(backbone_model)
    channels = backbone.layer_channels()
    model = SFNet(num_classes, backbone, channels, **kwargs)

    if weights_model is not None:
        state_dict = load_state_dict_from_url(weights_model.url, progress=progress)
        model.load_state_dict(state_dict)
    return model


@_generate_docstring("Semantic Flow Network model with a ResNet-101 backbone")
@register_model()
def sfnet_resnet101(
    num_classes: int | None = None,
    weights: SFNet_ResNet101_Weights | str | None = None,
    progress: bool = True,
    weights_backbone: ResNet101_Weights | str | None = ResNet101_Weights.DEFAULT,
    **kwargs,
) -> SFNet:
    """See :class:`SFNet` for supported kwargs"""
    weights_model = SFNet_ResNet101_Weights.resolve(weights)
    weights_model, weights_backbone, num_classes = _validate_weights_input(
        weights_model, weights_backbone, num_classes
    )

    backbone_model = resnet101(weights=weights_backbone, progress=progress)
    backbone = ResNetBackbone(backbone_model)
    channels = backbone.layer_channels()
    model = SFNet(num_classes, backbone, channels, **kwargs)

    if weights_model is not None:
        state_dict = load_state_dict_from_url(weights_model.url, progress=progress)
        model.load_state_dict(state_dict)
    return model
