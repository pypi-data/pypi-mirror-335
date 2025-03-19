from typing import cast

from torch import nn
from torchvision.models import resnet
from torchvision.models._utils import IntermediateLayerGetter


class ResNetBackbone(IntermediateLayerGetter):
    """
    For resnet50, resnet101 and resnet152, recommend to build with
    `replace_stride_with_dilation=[False, True, True]`
    """

    def __init__(self, model: resnet.ResNet) -> None:
        layers = [f"layer{i+1}" for i in range(4)]
        return_layers = {layer: layer for layer in layers}
        super().__init__(model, return_layers)

    def layer_channels(self) -> dict[str, int]:
        num_channels: dict[str, int] = {}
        for name, module in self.named_children():
            if name not in self.return_layers:
                continue

            key = self.return_layers[name]
            last_block = cast(nn.Sequential, module)[-1]
            if isinstance(last_block, resnet.BasicBlock):
                num_channels[key] = cast(int, last_block.bn2.num_features)
            elif isinstance(last_block, resnet.Bottleneck):
                num_channels[key] = cast(int, last_block.bn3.num_features)
            else:
                raise ValueError(f"Unknown block {key} of type {type(module)}")
        return num_channels
