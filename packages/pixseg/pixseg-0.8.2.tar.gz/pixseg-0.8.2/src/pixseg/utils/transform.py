import random
from typing import Any, Dict, Literal, Sequence

import numpy
import PIL
import PIL.Image
import torch
from torch import Tensor, nn
from torchvision.transforms import v2
from torchvision.transforms.v2 import functional as TF
from torchvision.transforms.v2._geometry import _FillType

from .rng import get_rng_state, set_rng_state

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STDDEV = (0.229, 0.224, 0.225)


class RandomRescale(v2.Transform):
    """Similar to :class:`RandomResize` but for scale"""

    def __init__(
        self,
        scale_range: Sequence[float],
        interpolation: v2.InterpolationMode = v2.InterpolationMode.BILINEAR,
        antialias: bool = True,
    ) -> None:
        """
        Args:
            scale_range: Range of scale (min, max)
        """
        super().__init__()
        if len(scale_range) != 2:
            raise ValueError(
                "Expected scale_range to be of the form (min, max), but got",
                scale_range,
            )
        self.scale_range = scale_range
        self.interpolation = interpolation
        self.antialias = antialias

    def make_params(self, flat_inputs: list[Any]) -> Dict[str, Any]:
        img = flat_inputs[0]
        assert isinstance(img, Tensor)
        scale = random.uniform(*self.scale_range)
        size: list[int] = [int(img.size(i) * scale) for i in [-2, -1]]
        return dict(size=size)

    def transform(self, inpt: Any, params: Dict[str, Any]) -> Any:
        return self._call_kernel(
            TF.resize,
            inpt,
            params["size"],
            interpolation=self.interpolation,
            antialias=self.antialias,
        )


class SafeRandomCrop(v2.Transform):
    """:class:`torchvision.transforms.v2.RandomCrop` throws error when size is more than
    double of input. This class repeats the process instead.

    Expect input of shape (..., H, W) and type PIL Image, numpy array or tensor
    """

    def __init__(
        self,
        size: int | Sequence[int],
        padding: int | Sequence[int] | None = None,
        pad_if_needed: bool = False,
        fill: _FillType | Dict[type | str, _FillType] = 0,
        padding_mode: Literal["constant", "edge", "reflect", "symmetric"] = "constant",
    ) -> None:
        """See :class:`torchvision.transforms.v2.RandomCrop` for arguments"""
        super().__init__()
        # for initializing args
        instance = v2.RandomCrop(size, padding, pad_if_needed, fill, padding_mode)
        self.size = instance.size
        self.target_size = (self.size[0], self.size[1])  # type: ignore
        self.args = [
            instance.padding,
            instance.pad_if_needed,
            instance.fill,
            instance.padding_mode,
        ]

    def transform(self, inpt: Any, params: Dict[str, Any]) -> Any:
        cur_size = self._get_inpt_size(inpt)
        while cur_size != self.target_size:
            next_size = [min(self.target_size[i], cur_size[i] * 2) for i in (0, 1)]
            op = v2.RandomCrop(next_size, *self.args)
            inpt = op(inpt)
            cur_size = self._get_inpt_size(inpt)
        return inpt

    @staticmethod
    def _get_inpt_size(inpt) -> tuple[int, int]:
        if isinstance(inpt, PIL.Image.Image):
            return inpt.size
        if isinstance(inpt, numpy.ndarray):
            return tuple(inpt.shape[-2:])
        if isinstance(inpt, Tensor):
            return (inpt.size(-2), inpt.size(-1))
        raise ValueError(f"Input of type {type(inpt)} not supported")


class ImageMaskTransform(nn.Module):
    """Data transform for semantic segmentation.

    Apply transforms on image and mask. Random process will be fixed on both sides if they
    are applied in the same order.
    """

    # inherit from nn.Module for custom forward

    def __init__(self, image: v2.Transform, mask: v2.Transform) -> None:
        super().__init__()
        self.image = image
        self.mask = mask

    def forward(
        self, image: Tensor, mask: Tensor | None = None
    ) -> tuple[Tensor, Tensor | None]:
        rng_state = get_rng_state()
        image = self.image(image)
        if mask is not None:
            set_rng_state(*rng_state)
            mask = self.mask(mask)
        return image, mask


class SegmentationTransform(v2.Compose):
    """The basic data transform for semantic segmentation task

    This ensures 2 things:
    1. Image will be float `Tensor` with correct range of values; Mask will be long
        `Tensor` without the channel dimension.
    2. If `size` is provided, all images and masks will have the same final size using
        `RandomCrop`
    """

    def __init__(
        self, size: Sequence[int] | None = None, mask_fill: int = -100
    ) -> None:
        image_transforms = [v2.ToImage(), v2.ToDtype(torch.float32, scale=True)]
        mask_transforms = [
            v2.ToImage(),
            v2.ToDtype(torch.long),
            lambda mask: torch.squeeze(mask, 0),
        ]
        if size is not None:
            image_transforms.insert(
                0, v2.RandomCrop(size, pad_if_needed=True, padding_mode="reflect")
            )
            mask_transforms.insert(
                0, v2.RandomCrop(size, pad_if_needed=True, fill=mask_fill)
            )

        image_transform = v2.Compose(image_transforms)
        mask_transform = v2.Compose(mask_transforms)
        super().__init__([ImageMaskTransform(image_transform, mask_transform)])


class SegmentationAugment(v2.Compose):
    """Default data augmentations for semantic segmentation"""

    def __init__(
        self,
        hflip=0.0,
        vflip=0.0,
        blur_size=1,
        blur_sigma: Sequence[float] = (0.1, 2.0),
        color_jitter: Sequence[float] = (0, 0, 0, 0),
        perspective=0.0,
        rotation_range: Sequence[float] = (0, 0),
        scale_range: Sequence[float] = (1, 1),
        auto_contrast=0.0,
        mask_fill=255,
    ) -> None:
        """If all args are kept at default, no destructive transform is performed

        Example for training:
        ```
        SegmentationAugment(hflip = 0.5, color_jitter = (0.1, 0.1, 0.1), blur_size=9,
            perspective = 0.2, rotation_range = (-30, 30), auto_contrast = 0.5)
        ```

        Args:
            scale_range: random scale range for image. Mask will not be scaled
            mask_fill: used for filling the mask when neccessary
        """
        image_transform = v2.Compose(
            [
                v2.RandomHorizontalFlip(hflip),
                v2.RandomVerticalFlip(vflip),
                v2.RandomPerspective(perspective),
                v2.RandomRotation(degrees=rotation_range),
                v2.GaussianBlur(blur_size, blur_sigma),
                v2.ColorJitter(*color_jitter),
                RandomRescale(scale_range),
                v2.RandomAutocontrast(auto_contrast),
                v2.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STDDEV),
            ]
        )
        mask_transform = v2.Compose(
            [
                v2.RandomHorizontalFlip(hflip),
                v2.RandomVerticalFlip(vflip),
                v2.RandomPerspective(
                    perspective,
                    interpolation=v2.InterpolationMode.NEAREST,
                    fill=mask_fill,
                ),
                v2.RandomRotation(degrees=rotation_range, fill=mask_fill),
            ]
        )
        super().__init__([ImageMaskTransform(image_transform, mask_transform)])
