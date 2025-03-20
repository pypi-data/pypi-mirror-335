from .imageformat import OpenCVImageFormat

from . import (
    colornodes,
    image_operations,
    image_processing,
    drawing,
    segmentation,
)
import funcnodes as fn
import funcnodes_numpy as fnnp  # noqa: F401 # for type hinting


__all__ = [
    "OpenCVImageFormat",
    "NODE_SHELF",
    "image_operations",
    "image_processing",
    "colornodes",
    "drawing",
]


__version__ = "0.2.13"


NODE_SHELF = fn.Shelf(
    name="OpenCV",
    description="OpenCV image processing nodes.",
    subshelves=[
        image_operations.NODE_SHELF,
        image_processing.NODE_SHELF,
        colornodes.NODE_SHELF,
        drawing.NODE_SHELF,
        segmentation.NODE_SHELF,
    ],
    nodes=[],
)
