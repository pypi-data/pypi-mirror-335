from typing import Tuple
import cv2
import numpy as np
import funcnodes as fn

from ..imageformat import OpenCVImageFormat, ImageFormat
from ..utils import assert_opencvdata


@fn.NodeDecorator(
    node_id="cv2.normalize",
    outputs=[
        {
            "name": "out_img",
        },
        {"name": "out_arr"},
    ],
    default_render_options={"data": {"src": "out"}},
    description="Normalizes the input image, scaling it to a given range.",
)
def normalize(
    img: ImageFormat,
    alpha: float = 0,
    beta: float = 255,
    norm_type: int = cv2.NORM_MINMAX,
    dtype: int = -1,
) -> Tuple[OpenCVImageFormat, np.ndarray]:
    data = assert_opencvdata(img)
    result = cv2.normalize(data, None, alpha, beta, norm_type, dtype)
    return OpenCVImageFormat(result), result


@fn.NodeDecorator(
    node_id="cv2.equalizeHist",
    outputs=[{"name": "out", "type": OpenCVImageFormat}],
    default_render_options={"data": {"src": "out"}},
    description="Equalizes the histogram of a grayscale image.",
)
def equalizeHist(
    img: ImageFormat,
) -> OpenCVImageFormat:
    data = assert_opencvdata(img, channel=1)
    result = cv2.equalizeHist(data)
    return OpenCVImageFormat(result)


@fn.NodeDecorator(
    node_id="cv2.CLAHE",
    outputs=[{"name": "out", "type": OpenCVImageFormat}],
    default_render_options={"data": {"src": "out"}},
    description="Applies Contrast Limited Adaptive Histogram Equalization (CLAHE) to a grayscale image.",
)
def CLAHE(
    img: ImageFormat,
    clip_limit: float = 40.0,
    tile_grid_size: tuple = (8, 8),
) -> cv2.CLAHE:
    data = assert_opencvdata(img, channel=1)
    return OpenCVImageFormat(
        cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size).apply(data)
    )


NODE_SHELF = fn.Shelf(
    name="Normalization & Equalization",
    description="OpenCV image normalization and equalization nodes.",
    nodes=[normalize, equalizeHist, CLAHE],
    subshelves=[],
)
