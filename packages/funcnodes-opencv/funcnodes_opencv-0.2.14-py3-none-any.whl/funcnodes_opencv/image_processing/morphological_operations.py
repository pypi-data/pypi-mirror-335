from typing import Optional, Union
import cv2
import numpy as np
import funcnodes as fn
from ..imageformat import OpenCVImageFormat, ImageFormat
from ..utils import assert_opencvdata


@fn.NodeDecorator(
    node_id="cv2.dilate",
    default_render_options={"data": {"src": "out"}},
    description="Dilates an image.",
)
def dilate(
    img: ImageFormat,
    kernel: Optional[np.ndarray] = None,
    iterations: int = 1,
) -> OpenCVImageFormat:
    return OpenCVImageFormat(
        cv2.dilate(assert_opencvdata(img), kernel=kernel, iterations=iterations)
    )


@fn.NodeDecorator(
    node_id="cv2.erode",
    default_render_options={"data": {"src": "out"}},
    description="Erodes an image.",
)
def erode(
    img: ImageFormat,
    kernel: Optional[np.ndarray] = None,
    iterations: int = 1,
) -> OpenCVImageFormat:
    return OpenCVImageFormat(
        cv2.erode(assert_opencvdata(img), kernel=kernel, iterations=iterations)
    )


class MorphologicalOperations(fn.DataEnum):
    """
    Morphological operations.

    Attributes:
        ERODE: cv2.MORPH_ERODE: erodes an image
        DILATE: cv2.MORPH_DILATE: dilates an image
        OPEN: cv2.MORPH_OPEN: an erosion followed by a dilation
        CLOSE: cv2.MORPH_CLOSE: a dilation followed by an erosion
        GRADIENT: cv2.MORPH_GRADIENT: the difference between dilation and erosion of an image
        TOPHAT: cv2.MORPH_TOPHAT: the difference between input image and opening of the image
        BLACKHAT: cv2.MORPH_BLACKHAT: the difference between the closing of the input image and input image
        HITMISS: cv2.MORPH_HITMISS: a hit-or-miss transform

    """

    ERODE = cv2.MORPH_ERODE
    DILATE = cv2.MORPH_DILATE
    OPEN = cv2.MORPH_OPEN
    CLOSE = cv2.MORPH_CLOSE
    GRADIENT = cv2.MORPH_GRADIENT
    TOPHAT = cv2.MORPH_TOPHAT
    BLACKHAT = cv2.MORPH_BLACKHAT
    HITMISS = cv2.MORPH_HITMISS


@fn.NodeDecorator(
    node_id="cv2.morphologyEx",
    default_render_options={"data": {"src": "out"}},
    description="Performs advanced morphological transformations.",
)
def morphologyEx(
    img: ImageFormat,
    op: MorphologicalOperations = MorphologicalOperations.ERODE,
    kernel: Optional[Union[int, np.ndarray]] = None,
    iterations: int = 1,
) -> OpenCVImageFormat:
    op = MorphologicalOperations.v(op)

    if kernel is not None and isinstance(kernel, (int, float)):
        kernel = np.ones((int(kernel), int(kernel)), np.uint8)

    data = assert_opencvdata(img, channel=None if op != cv2.MORPH_HITMISS else 1)
    return OpenCVImageFormat(
        cv2.morphologyEx(
            data,
            op=op,
            kernel=kernel,
            iterations=iterations,
        )
    )


NODE_SHELF = fn.Shelf(
    nodes=[dilate, erode, morphologyEx],
    name="Morphological Operations",
    description="OpenCV morphological operations.",
)
