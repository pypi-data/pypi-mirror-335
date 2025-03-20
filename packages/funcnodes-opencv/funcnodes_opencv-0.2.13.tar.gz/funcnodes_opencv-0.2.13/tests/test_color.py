import numpy as np
import cv2
import pytest
import pytest_funcnodes
from funcnodes_opencv.colornodes import (
    color_convert,
    ColorCodes,
)


def get_image_data(image_format):
    return image_format.data if hasattr(image_format, "data") else image_format


@pytest.fixture
def image1():
    return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)


@pytest_funcnodes.nodetest(color_convert)
@pytest.mark.parametrize(
    "code",
    [
        ColorCodes.GRAY,
        # ColorCodes.BGR,
        ColorCodes.RGB,
        ColorCodes.HSV,
        ColorCodes.LAB,
        ColorCodes.YUV,
        ColorCodes.YCrCb,
        ColorCodes.XYZ,
        ColorCodes.HLS,
        ColorCodes.LUV,
    ],
)
async def test_color_convert(image1, code):
    data = get_image_data(await color_convert.inti_call(img=image1, code=code))
    np.testing.assert_array_equal(
        data[..., 0] if code == ColorCodes.GRAY else data,
        cv2.cvtColor(image1, getattr(cv2, f"COLOR_BGR2{ColorCodes.v(code)}")),
    )
