import funcnodes as fn
from .filtering_smoothing import NODE_SHELF as FILTERING_SMOOTHING_SHELF
from .geometric_transformations import NODE_SHELF as GEOMETRIC_TRANSFORMATIONS_SHELF
from .thresholding import NODE_SHELF as THRESHOLDING_SHELF
from .morphological_operations import NODE_SHELF as MORPHOLOGICAL_OPERATIONS_SHELF
from .edge_gradient import NODE_SHELF as EDGE_GRADIENT_SHELF

NODE_SHELF = fn.Shelf(
    nodes=[],
    subshelves=[
        FILTERING_SMOOTHING_SHELF,
        GEOMETRIC_TRANSFORMATIONS_SHELF,
        THRESHOLDING_SHELF,
        MORPHOLOGICAL_OPERATIONS_SHELF,
        EDGE_GRADIENT_SHELF,
    ],
    name="Image Processing",
    description="Image processing operations.",
)
