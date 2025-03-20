from typing import Union
import cv2
import numpy as np
import funcnodes as fn
from ..imageformat import OpenCVImageFormat, ImageFormat
from ..utils import assert_opencvdata


@fn.NodeDecorator(
    node_id="cv2.add",
    outputs=[{"name": "out", "type": OpenCVImageFormat}],
    default_render_options={"data": {"src": "out"}},
    description="Add two images by adding their pixel values.",
)
def add(
    img1: ImageFormat,
    img2: ImageFormat,
    mask: ImageFormat = None,
) -> OpenCVImageFormat:
    data1 = assert_opencvdata(img1)
    data2 = assert_opencvdata(img2)
    mask = assert_opencvdata(mask, channel=1) if mask is not None else None
    result = cv2.add(data1, data2, mask=mask)
    return OpenCVImageFormat(result)


@fn.NodeDecorator(
    node_id="cv2.subtract",
    outputs=[{"name": "out", "type": OpenCVImageFormat}],
    default_render_options={"data": {"src": "out"}},
    description="Subtract two images by subtracting their pixel values.",
)
def subtract(
    img1: ImageFormat,
    img2: ImageFormat,
    mask: ImageFormat = None,
) -> OpenCVImageFormat:
    data1 = assert_opencvdata(img1)
    data2 = assert_opencvdata(img2)
    mask = assert_opencvdata(mask, channel=1) if mask is not None else None
    result = cv2.subtract(data1, data2, mask=mask)
    return OpenCVImageFormat(result)


@fn.NodeDecorator(
    node_id="cv2.multiply",
    outputs=[{"name": "out", "type": OpenCVImageFormat}],
    default_render_options={"data": {"src": "out"}},
    description="Multiply two images by multiplying their pixel values.",
)
def multiply(
    img1: ImageFormat,
    img2: ImageFormat,
) -> OpenCVImageFormat:
    data1 = assert_opencvdata(img1)
    data2 = assert_opencvdata(img2)
    result = cv2.multiply(
        data1,
        data2,
    )
    return OpenCVImageFormat(result)


@fn.NodeDecorator(
    node_id="cv2.divide",
    outputs=[{"name": "out", "type": OpenCVImageFormat}],
    default_render_options={"data": {"src": "out"}},
    description="Divide two images by dividing their pixel values.",
)
def divide(
    img1: ImageFormat,
    img2: ImageFormat,
) -> OpenCVImageFormat:
    data1 = assert_opencvdata(img1)
    data2 = assert_opencvdata(img2)
    result = cv2.divide(data1, data2)
    return OpenCVImageFormat(result)


@fn.NodeDecorator(
    node_id="cv2.addWeighted",
    outputs=[{"name": "out", "type": OpenCVImageFormat}],
    default_render_options={"data": {"src": "out"}},
    description="Add two images by adding their pixel values with a specified weight.",
    default_io_options={
        "alpha": {"value_options": {"min": 0, "max": 1}},
        "beta": {"value_options": {"min": 0, "max": 1}},
        "gamma": {"value_options": {"min": 0, "max": 255}},
    },
)
def addWeighted(
    img1: ImageFormat,
    img2: ImageFormat,
    alpha: float = 0.5,
    beta: float = 0.5,
    gamma: float = 0,
) -> OpenCVImageFormat:
    data1 = assert_opencvdata(img1)
    data2 = assert_opencvdata(img2)
    result = cv2.addWeighted(data1, alpha, data2, beta, gamma)
    return OpenCVImageFormat(result)


@fn.NodeDecorator(
    node_id="cv2.where",
    outputs=[{"name": "out", "type": OpenCVImageFormat}],
    default_render_options={"data": {"src": "out"}},
    description="Based on a mask sets the pixel values of an image to a specified value or another image.",
)
def where(
    img: ImageFormat,
    mask: ImageFormat,
    value: Union[int, ImageFormat],
) -> OpenCVImageFormat:
    data = assert_opencvdata(img)
    mask = assert_opencvdata(mask, channel=1)
    if isinstance(value, float):
        value = int(value)
    if not isinstance(value, int):
        value = assert_opencvdata(value, channel=data.ndim)
    result = data.copy()
    if isinstance(value, int):
        result[mask != 0] = value
    else:
        result[mask != 0] = value[mask != 0]
    return OpenCVImageFormat(result)


@fn.NodeDecorator(
    node_id="cv2.brighten",
    outputs=[{"name": "out", "type": OpenCVImageFormat}],
    default_render_options={"data": {"src": "out"}},
    description="Brighten an image by adding a specified value to all pixel values.",
    default_io_options={"value": {"value_options": {"min": -255, "max": 255}}},
)
def brighten(
    img: ImageFormat,
    value: int = 0,
) -> OpenCVImageFormat:
    data = assert_opencvdata(img)
    result = data + value
    result = np.clip(result, 0, 255)
    return OpenCVImageFormat(result)


NODE_SHELF = fn.Shelf(
    name="Arithmetic Operations",
    nodes=[add, subtract, multiply, divide, addWeighted, where],
    description="Nodes for performing arithmetic operations on images.",
    subshelves=[],
)
