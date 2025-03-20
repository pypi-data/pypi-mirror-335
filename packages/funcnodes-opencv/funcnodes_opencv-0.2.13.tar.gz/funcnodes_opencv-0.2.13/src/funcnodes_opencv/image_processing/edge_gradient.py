from typing import Literal
import cv2
import funcnodes as fn
from ..imageformat import OpenCVImageFormat, ImageFormat
from ..utils import assert_opencvdata


# canny
@fn.NodeDecorator(
    node_id="cv2.Canny",
    default_render_options={"data": {"src": "out"}},
    description="Finds edges in an image using the Canny algorithm.",
)
def Canny(
    img: ImageFormat,
    threshold1: float,
    threshold2: float,
    apertureSize: int = 3,
    L2gradient: bool = False,
) -> OpenCVImageFormat:
    return OpenCVImageFormat(
        cv2.Canny(
            assert_opencvdata(img),
            threshold1,
            threshold2,
            apertureSize=apertureSize,
            L2gradient=L2gradient,
        )
    )


@fn.NodeDecorator(
    node_id="cv2.Laplacian",
    default_render_options={"data": {"src": "out"}},
    description="Calculates the Laplacian of an image, which is the sum of second derivatives of the image.",
)
def Laplacian(
    img: ImageFormat,
    ksize: int = 1,
    scale: float = 1,
    delta: int = 0,
) -> OpenCVImageFormat:
    if ksize % 2 == 0:
        ksize += 1
    return OpenCVImageFormat(
        cv2.Laplacian(assert_opencvdata(img), -1, ksize=ksize, scale=scale, delta=delta)
    )


@fn.NodeDecorator(
    node_id="cv2.Sobel",
    default_render_options={"data": {"src": "out"}},
    description="Calculates the first, second, third, or mixed image derivatives using an extended Sobel operator.",
)
def Sobel(
    img: ImageFormat,
    dx: int = 1,
    dy: int = 0,
    ksize: Literal[1, 3, 5, 7] = 3,
    scale: float = 1,
    delta: int = 0,
) -> OpenCVImageFormat:
    return OpenCVImageFormat(
        cv2.Sobel(
            assert_opencvdata(img),
            -1,
            dx=dx,
            dy=dy,
            ksize=int(ksize),
            scale=scale,
            delta=delta,
        )
    )


@fn.NodeDecorator(
    node_id="cv2.Scharr",
    default_render_options={"data": {"src": "out"}},
    description="Calculates the first image derivative using Scharr operator.",
)
def Scharr(
    img: ImageFormat,
    dx: int = 1,
    dy: int = 0,
    scale: float = 1,
    delta: int = 0,
) -> OpenCVImageFormat:
    return OpenCVImageFormat(
        cv2.Scharr(assert_opencvdata(img), -1, dx=dx, dy=dy, scale=scale, delta=delta)
    )


NODE_SHELF = fn.Shelf(
    name="Edge Gradient",
    nodes=[
        Canny,
        Laplacian,
        Sobel,
        Scharr,
    ],
    subshelves=[],
    description="Edge & Gradient operations.",
)
