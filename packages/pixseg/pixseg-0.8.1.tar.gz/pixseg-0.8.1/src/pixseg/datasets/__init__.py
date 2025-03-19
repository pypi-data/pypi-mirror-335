from .ade20k import ADE20K, ADE20K_LABELS
from .bdd100k import BDD100K
from .cityscapes import (
    CITYSCAPES_CATEGORY_LABELS,
    CITYSCAPES_COLORS,
    CITYSCAPES_FULL_COLORS,
    CITYSCAPES_FULL_LABELS,
    CITYSCAPES_LABELS,
    CityscapesSubset,
)
from .coco_stuff import COCO_FULL_LABELS, COCO_STUFF_LABELS, COCO_VOC_LABELS, COCOStuff
from .dataset_registry import (
    DATASET_METADATA,
    DATASET_ZOO,
    DatasetEntry,
    DatasetMeta,
    register_dataset,
    resolve_metadata,
)
from .lip import LIP, LIP_LABELS
from .mapillary import (
    MAPILLARY_COLORS,
    MAPILLARY_FULL_COLORS,
    MAPILLARY_FULL_LABELS,
    MAPILLARY_LABELS,
    MapillaryVistas,
)
from .voc_like import VOC_COLORS, VOC_LABELS
