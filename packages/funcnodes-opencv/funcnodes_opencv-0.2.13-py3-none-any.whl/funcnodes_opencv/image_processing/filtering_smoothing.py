from typing import Optional, Tuple
import cv2
import numpy as np
import funcnodes as fn
from ..imageformat import OpenCVImageFormat, ImageFormat
from ..utils import assert_opencvdata


class BorderTypes(fn.DataEnum):
    """
    Border types for cv2.filter2D and cv2.blur

    Attributes:
        CONSTANT: cv2.BORDER_CONSTANT: Border is filled with the constant value
        REPLICATE: cv2.BORDER_REPLICATE: Border is replicated from the edge pixels
        REFLECT: cv2.BORDER_REFLECT: Border is reflectively mirrored
        REFLECT_101: cv2.BORDER_REFLECT_101: Border is reflectively mirrored with the edge pixels excluded
        WRAP: cv2.BORDER_WRAP: Border is wrapped around
    """

    CONSTANT = cv2.BORDER_CONSTANT
    REPLICATE = cv2.BORDER_REPLICATE
    REFLECT = cv2.BORDER_REFLECT
    REFLECT_101 = cv2.BORDER_REFLECT_101
    WRAP = cv2.BORDER_WRAP
    TRANSPARENT = cv2.BORDER_TRANSPARENT
    ISOLATED = cv2.BORDER_ISOLATED
    DEFAULT = cv2.BORDER_DEFAULT


@fn.NodeDecorator(
    node_id="cv2.blur",
    default_render_options={"data": {"src": "out"}},
    description="Apply a simple blur to an image.",
)
def blur(
    img: ImageFormat,
    kw: int = 5,
    kh: int = 0,
    borderType: BorderTypes = BorderTypes.DEFAULT,
) -> OpenCVImageFormat:
    if kh <= 0:
        kh = kw

    ksize = (kw, kh)
    return OpenCVImageFormat(
        cv2.blur(assert_opencvdata(img), ksize, borderType=BorderTypes.v(borderType))
    )


@fn.NodeDecorator(
    node_id="cv2.GaussianBlur",
    default_render_options={"data": {"src": "out"}},
    description="Apply a Gaussian blur to an image.",
)
def gaussianBlur(
    img: ImageFormat,
    kw: int = 5,
    kh: int = 0,
    sigmaX: float = 0,
    sigmaY: float = -1,
    borderType: BorderTypes = BorderTypes.DEFAULT,
) -> OpenCVImageFormat:
    if kh <= 0:
        kh = kw

    if kw % 2 == 0:
        kw += 1

    if kh % 2 == 0:
        kh += 1

    if sigmaY < 0:
        sigmaY = sigmaX

    ksize = (kw, kh)
    return OpenCVImageFormat(
        cv2.GaussianBlur(
            assert_opencvdata(img),
            ksize,
            sigmaX=sigmaX,
            sigmaY=sigmaY,
            borderType=BorderTypes.v(borderType),
        )
    )


@fn.NodeDecorator(
    node_id="cv2.medianBlur",
    default_render_options={"data": {"src": "out"}},
    description="Apply a median blur to an image.",
)
def medianBlur(
    img: ImageFormat,
    ksize: int = 5,
) -> OpenCVImageFormat:
    if ksize % 2 == 0:
        ksize += 1
    return OpenCVImageFormat(cv2.medianBlur(assert_opencvdata(img), ksize))


@fn.NodeDecorator(
    node_id="cv2.bilateralFilter",
    default_render_options={"data": {"src": "out"}},
    description="Apply a bilateral filter to an image. Use this filter to smooth an image while preserving edges.",
)
def bilateralFilter(
    img: ImageFormat,
    d: int = 9,
    sigmaColor: float = 75,
    sigmaSpace: float = 75,
    borderType: BorderTypes = BorderTypes.DEFAULT,
) -> OpenCVImageFormat:
    return OpenCVImageFormat(
        cv2.bilateralFilter(
            assert_opencvdata(img),
            d,
            sigmaColor,
            sigmaSpace,
            borderType=BorderTypes.v(borderType),
        )
    )


@fn.NodeDecorator(
    node_id="cv2.boxFilter",
    default_render_options={"data": {"src": "out"}},
    description="Apply a box filter to an image",
)
def boxFilter(
    img: ImageFormat,
    kw: int = 5,
    kh: Optional[int] = None,
    normalize: bool = True,
    borderType: BorderTypes = BorderTypes.DEFAULT,
) -> OpenCVImageFormat:
    if kh is None:
        kh = kw

    ksize = (kw, kh)
    return OpenCVImageFormat(
        cv2.boxFilter(
            assert_opencvdata(img),
            -1,
            ksize=ksize,
            normalize=normalize,
            borderType=BorderTypes.v(borderType),
        )
    )


@fn.NodeDecorator(
    node_id="cv2.filter2D",
    default_render_options={"data": {"src": "out"}},
    description="Apply a custom kernel to an image.",
)
def filter2D(
    img: ImageFormat,
    kernel: Optional[np.ndarray],
    ddepth: int = -1,
    anchor: Optional[Tuple[int, int]] = None,
    delta: int = 0,
    borderType: BorderTypes = BorderTypes.DEFAULT,
) -> OpenCVImageFormat:
    if anchor is None:
        anchor = (-1, -1)

    data = assert_opencvdata(img)

    return OpenCVImageFormat(
        cv2.filter2D(
            data,
            ddepth=ddepth,
            kernel=kernel,
            anchor=anchor,
            delta=delta,
            borderType=BorderTypes.v(borderType),
        )
    )


@fn.NodeDecorator(
    node_id="cv2.stackBlur",
    default_render_options={"data": {"src": "out"}},
)
def stackBlur(
    img: ImageFormat,
    kw: int = 5,
    kh: Optional[int] = None,
) -> OpenCVImageFormat:
    if kh is None:
        kh = kw
    if kw % 2 == 0:
        kw += 1
    if kh % 2 == 0:
        kh += 1
    ksize = (kw, kh)
    return OpenCVImageFormat(cv2.stackBlur(assert_opencvdata(img), ksize))


NODE_SHELF = fn.Shelf(
    nodes=[
        blur,
        gaussianBlur,
        medianBlur,
        bilateralFilter,
        stackBlur,
        boxFilter,
        filter2D,
    ],
    subshelves=[],
    name="Filtering and Smoothing",
    description="OpenCV image filtering and smoothing nodes.",
)
