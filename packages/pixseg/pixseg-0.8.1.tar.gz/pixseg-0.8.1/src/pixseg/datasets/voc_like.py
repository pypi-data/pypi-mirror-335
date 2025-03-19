from torchvision import datasets

from .dataset_registry import DatasetMeta, register_dataset

# fmt: off
VOC_LABELS = ("background",
              "person", 
              "bird", "cat", "cow", "dog", "horse", "sheep", 
              "aeroplane", "bicycle", "boat", "bus", "car", "motorbike", "train", 
              "bottle", "chair", "diningtable", "pottedplant", "sofa", "tvmonitor")
VOC_COLORS = ((0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0), (0, 0, 128), 
              (128, 0, 128), (0, 128, 128), (128, 128, 128), (64, 0, 0), (192, 0, 0), 
              (64, 128, 0), (192, 128, 0), (64, 0, 128), (192, 0, 128), (64, 128, 128), 
              (192, 128, 128), (0, 64, 0), (128, 64, 0), (0, 192, 0), (128, 192, 0), (0, 64, 128))
# fmt: on

# register builtin datasets
register_dataset(
    {"image_set": "train"},
    {"image_set": "val"},
    meta=DatasetMeta(21, 255, VOC_LABELS, VOC_COLORS),
    name="VOC",
)(datasets.VOCSegmentation)

register_dataset(
    {"mode": "segmentation", "image_set": "train"},
    {"mode": "segmentation", "image_set": "val"},
    meta="VOC",
    name="SBD",
)(datasets.SBDataset)
