import cv2
import numpy as np
from funcnodes_images.imagecontainer import register_imageformat, ImageFormat  # noqa: F401
from funcnodes_images._numpy import NumpyImageFormat
from funcnodes_images._pillow import PillowImageFormat
from funcnodes_images.utils import calc_new_size


def _conv_colorspace(data: np.ndarray, from_: str, to: str) -> np.ndarray:
    if from_ == to:
        return data
    conv = f"COLOR_{from_}2{to}"
    if not hasattr(cv2, conv):
        raise ValueError(f"Conversion from {from_} to {to} not supported")
    return cv2.cvtColor(data, getattr(cv2, conv))


class OpenCVImageFormat(NumpyImageFormat):
    def __init__(self, arr: np.ndarray, colorspace: str = "BGR"):
        if not isinstance(arr, np.ndarray):
            raise TypeError("arr must be a numpy array")

        if arr.ndim == 2:
            colorspace = "GRAY"

        if colorspace != "BGR":
            arr = _conv_colorspace(arr, colorspace, "BGR")

        super().__init__(arr)

    def get_data_copy(self) -> np.ndarray:
        return self._data.copy()

    def to_colorspace(self, colorspace: str) -> np.ndarray:
        return _conv_colorspace(self.data, "BGR", colorspace)

    def to_jpeg(self, quality=0.75) -> bytes:
        return cv2.imencode(
            ".jpg", self.data, [int(cv2.IMWRITE_JPEG_QUALITY), int(quality * 100)]
        )[1].tobytes()

    def to_thumbnail(self, size: tuple) -> "OpenCVImageFormat":
        cur_y, cur_x = self.data.shape[:2]
        ratio = min(size[0] / cur_x, size[1] / cur_y)
        new_x, new_y = int(cur_x * ratio), int(cur_y * ratio)
        return OpenCVImageFormat(
            cv2.resize(
                self._data,
                (new_x, new_y),
            )
        )

    def resize(
        self,
        w: int = None,
        h: int = None,
    ) -> "OpenCVImageFormat":
        new_x, new_y = calc_new_size(*self.data.shape[:2], w, h)
        return OpenCVImageFormat(
            cv2.resize(
                self.data,
                (new_x, new_y),
            )
        )


register_imageformat(OpenCVImageFormat, "cv2")


def cv2_to_np(cv2_img: OpenCVImageFormat) -> NumpyImageFormat:
    return NumpyImageFormat(_conv_colorspace(cv2_img.data, "BGR", "RGB"))


def np_to_cv2(np_img: NumpyImageFormat) -> OpenCVImageFormat:
    return OpenCVImageFormat(np_img.to_rgb_uint8(), colorspace="RGB")


OpenCVImageFormat.add_to_converter(NumpyImageFormat, cv2_to_np)
NumpyImageFormat.add_to_converter(OpenCVImageFormat, np_to_cv2)


def cv2_to_pil(cv2_img: OpenCVImageFormat) -> PillowImageFormat:
    return cv2_img.to_np().to_img()


def pil_to_cv2(pil_img: PillowImageFormat) -> OpenCVImageFormat:
    return pil_img.to_np().to_cv2()


OpenCVImageFormat.add_to_converter(PillowImageFormat, cv2_to_pil)
PillowImageFormat.add_to_converter(OpenCVImageFormat, pil_to_cv2)
