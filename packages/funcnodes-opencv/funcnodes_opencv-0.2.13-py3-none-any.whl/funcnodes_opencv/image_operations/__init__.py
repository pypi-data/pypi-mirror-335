import funcnodes as fn
from .arithmetic_operations import NODE_SHELF as ARITHMETIC_OPERATIONS_NODE_SHELF
from .matrix_operations import NODE_SHELF as MATRIX_OPERATIONS_NODE_SHELF
from .bitwise_operations import NODE_SHELF as BITWISE_OPERATIONS_NODE_SHELF
from .normalization_equalization import (
    NODE_SHELF as NORMALIZATION_EQUALIZATION_NODE_SHELF,
)

NODE_SHELF = fn.Shelf(
    name="Image Operations",
    nodes=[],
    description="Nodes for performing operations on images.",
    subshelves=[
        ARITHMETIC_OPERATIONS_NODE_SHELF,
        BITWISE_OPERATIONS_NODE_SHELF,
        MATRIX_OPERATIONS_NODE_SHELF,
        NORMALIZATION_EQUALIZATION_NODE_SHELF,
    ],
)
