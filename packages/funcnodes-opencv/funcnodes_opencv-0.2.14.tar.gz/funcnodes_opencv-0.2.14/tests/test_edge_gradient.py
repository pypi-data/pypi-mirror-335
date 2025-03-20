import numpy as np
import cv2
import pytest
import pytest_funcnodes
from funcnodes_opencv.image_processing.edge_gradient import (
    Canny,
    Laplacian,
    Sobel,
    Scharr,
)


def get_image_data(image_format):
    return image_format.data if hasattr(image_format, "data") else image_format


@pytest.fixture
def image1():
    return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)


@pytest_funcnodes.nodetest(Canny)
async def test_Canny(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await Canny.inti_call(img=image1, threshold1=100, threshold2=200)
        )[..., 0],
        cv2.Canny(image1, 100, 200),
    )


@pytest.mark.parametrize(
    "dx, dy, ksize",
    [
        (1, 0, 3),
        (0, 1, 3),
        (1, 1, 3),
        (1, 0, 5),
        (0, 1, 5),
        (1, 1, 5),
    ],
)
@pytest_funcnodes.nodetest(Sobel)
async def test_Sobel(image1, dx, dy, ksize):
    np.testing.assert_array_equal(
        get_image_data(await Sobel.inti_call(img=image1, dx=dx, dy=dy, ksize=ksize)),
        cv2.Sobel(image1, -1, dx, dy, ksize=ksize),
    )


@pytest.mark.parametrize(
    "dx, dy",
    [
        (1, 0),
        (0, 1),
    ],
)
@pytest_funcnodes.nodetest(Scharr)
async def test_Scharr(image1, dx, dy):
    np.testing.assert_array_equal(
        get_image_data(await Scharr.inti_call(img=image1, dx=dx, dy=dy)),
        cv2.Scharr(image1, -1, dx, dy),
    )


@pytest.mark.parametrize(
    "ksize",
    [
        1,
        3,
        5,
    ],
)
@pytest_funcnodes.nodetest(Laplacian)
async def test_Laplacian(image1, ksize):
    np.testing.assert_array_equal(
        get_image_data(await Laplacian.inti_call(img=image1, ksize=ksize)),
        cv2.Laplacian(image1, -1, ksize=ksize),
    )
