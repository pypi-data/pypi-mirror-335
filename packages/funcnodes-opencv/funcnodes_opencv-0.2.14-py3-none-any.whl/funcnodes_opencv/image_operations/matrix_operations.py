from typing import List
import cv2
import numpy as np
import funcnodes as fn
from ..imageformat import OpenCVImageFormat, ImageFormat
from ..utils import assert_opencvdata


@fn.NodeDecorator(
    node_id="cv2.merge",
    outputs=[{"name": "out", "type": OpenCVImageFormat}],
    default_render_options={"data": {"src": "out"}},
    description="Merge multiple single-channel images into a multi-channel image.",
)
def merge(
    channels: List[OpenCVImageFormat],  # list of images
) -> OpenCVImageFormat:
    ch_list = [assert_opencvdata(ch, channel=1) for ch in channels]
    merged = cv2.merge(ch_list)
    return OpenCVImageFormat(merged)


@fn.NodeDecorator(
    node_id="cv2.split",
    outputs=[{"name": "channels", "type": list}],
    description="Split a multi-channel image into multiple single-channel images.",
)
def split(
    img: ImageFormat,
) -> List[OpenCVImageFormat]:
    data = assert_opencvdata(img)
    channels = cv2.split(data)
    return [OpenCVImageFormat(ch) for ch in channels]


@fn.NodeDecorator(
    node_id="cv2.transpose",
    outputs=[{"name": "out", "type": OpenCVImageFormat}],
    default_render_options={"data": {"src": "out"}},
    description="Transpose an image.",
)
def transpose(
    img: ImageFormat,
) -> OpenCVImageFormat:
    data = assert_opencvdata(img)
    transposed = cv2.transpose(data)
    return OpenCVImageFormat(transposed)


@fn.NodeDecorator(
    node_id="cv2.repeat",
    outputs=[{"name": "out", "type": OpenCVImageFormat}],
    default_render_options={"data": {"src": "out"}},
    description="Repeat an image in the vertical and horizontal directions.",
)
def repeat(
    img: ImageFormat,
    ny: int = 2,
    nx: int = 2,
) -> OpenCVImageFormat:
    data = assert_opencvdata(img)
    repeated = cv2.repeat(data, ny, nx)
    return OpenCVImageFormat(repeated)


@fn.NodeDecorator(
    node_id="cv2.getAffineTransform_points",
)
def getAffineTransform_points(
    i1x1: int,
    i1y1: int,
    i1x2: int,
    i1y2: int,
    i1x3: int,
    i1y3: int,
    i2x1: int,
    i2y1: int,
    i2x2: int,
    i2y2: int,
    i2x3: int,
    i2y3: int,
) -> np.ndarray:
    return cv2.getAffineTransform(
        np.array([[i1x1, i1y1], [i1x2, i1y2], [i1x3, i1y3]], dtype=np.float32),
        np.array([[i2x1, i2y1], [i2x2, i2y2], [i2x3, i2y3]], dtype=np.float32),
    )


@fn.NodeDecorator(
    node_id="cv2.getPerspectiveTransform_points",
)
def getPerspectiveTransform_points(
    i1x1: int,
    i1y1: int,
    i1x2: int,
    i1y2: int,
    i1x3: int,
    i1y3: int,
    i1x4: int,
    i1y4: int,
    i2x1: int,
    i2y1: int,
    i2x2: int,
    i2y2: int,
    i2x3: int,
    i2y3: int,
    i2x4: int,
    i2y4: int,
) -> np.ndarray:
    return cv2.getPerspectiveTransform(
        np.array(
            [[i1x1, i1y1], [i1x2, i1y2], [i1x3, i1y3], [i1x4, i1y4]], dtype=np.float32
        ),
        np.array(
            [[i2x1, i2y1], [i2x2, i2y2], [i2x3, i2y3], [i2x4, i2y4]], dtype=np.float32
        ),
    )


@fn.NodeDecorator(
    node_id="cv2.getAffineTransform",
)
def getAffineTransform(src: np.ndarray, dst: np.ndarray) -> np.ndarray:
    return cv2.getAffineTransform(src.astype(np.float32), dst.astype(np.float32))


@fn.NodeDecorator(
    node_id="cv2.getPerspectiveTransform",
)
def getPerspectiveTransform(src: np.ndarray, dst: np.ndarray) -> np.ndarray:
    return cv2.getPerspectiveTransform(src.astype(np.float32), dst.astype(np.float32))


NODE_SHELF = fn.Shelf(
    name="Matrix Operations",
    nodes=[
        merge,
        split,
        transpose,
        repeat,
        getAffineTransform_points,
        getPerspectiveTransform_points,
        getAffineTransform,
        getPerspectiveTransform,
    ],
    description="Nodes for matrix operations on images.",
    subshelves=[],
)
