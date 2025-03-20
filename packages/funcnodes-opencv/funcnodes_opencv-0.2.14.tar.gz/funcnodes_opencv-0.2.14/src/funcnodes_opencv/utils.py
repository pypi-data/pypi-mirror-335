import numpy as np
from typing import Literal
import cv2
from .imageformat import OpenCVImageFormat, ImageFormat, NumpyImageFormat


def normalize(img: np.ndarray, to_uint8: bool = True):
    img = img.astype(float)
    img -= img.min()
    img /= img.max()
    if to_uint8:
        img *= 255
        img = img.astype(np.uint8)
    return img


def gen_lut():
    """
    Generate a label colormap compatible with opencv lookup table, based on
    Rick Szelski algorithm in `Computer Vision: Algorithms and Applications`,
    appendix C2 `Pseudocolor Generation`.
    :Returns:
      color_lut : opencv compatible color lookup table
    """

    def tobits(x, o):
        return np.array(list(np.binary_repr(x, 24)[o::-3]), np.uint8)

    arr = np.arange(256)
    r = np.concatenate([np.packbits(tobits(x, -3)) for x in arr])
    g = np.concatenate([np.packbits(tobits(x, -2)) for x in arr])
    b = np.concatenate([np.packbits(tobits(x, -1)) for x in arr])
    return np.concatenate([[[b]], [[g]], [[r]]]).T


LUT = gen_lut()


def assert_opencvimg(img) -> OpenCVImageFormat:
    if isinstance(img, OpenCVImageFormat):
        return img
    if isinstance(img, ImageFormat):
        return img.to_cv2()

    if isinstance(img, np.ndarray):
        return OpenCVImageFormat(img)

    raise TypeError("img must be an OpenCVImageFormat, ImageFormat or np.ndarray")


def assert_opencvdata(img, channel: Literal[1, 3, None] = None) -> np.ndarray:
    if isinstance(img, OpenCVImageFormat):
        arr = img.data
    elif isinstance(img, ImageFormat):
        arr = img.to_cv2().data
    elif isinstance(img, np.ndarray):
        arr = img.copy()
    else:
        arr = NumpyImageFormat(img).to_cv2().data

    if arr.ndim == 2:
        if channel == 1 or channel is None:
            return arr
        if channel == 3:
            return np.repeat(arr[:, :, np.newaxis], 3, axis=2)
    if arr.ndim == 3:
        if arr.shape[2] == 1:
            if channel == 1 or channel is None:
                return arr[:, :, 0]
            if channel == 3:
                return np.repeat(arr, 3, axis=2)
        if arr.shape[2] == 3:
            if channel == 3 or channel is None:
                return arr
            if channel == 1:
                return cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)

        raise ValueError(f"Image has {arr.shape[2]} channels, expected {channel}")

    raise ValueError(f"Image has {arr.ndim} dimensions, expected 2 or 3")
