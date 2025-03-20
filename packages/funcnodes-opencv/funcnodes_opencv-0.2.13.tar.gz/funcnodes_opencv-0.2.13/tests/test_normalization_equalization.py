import numpy as np
import cv2
import pytest
import pytest_funcnodes
from funcnodes_opencv.image_operations.normalization_equalization import (
    normalize,
    equalizeHist,
    CLAHE,
)


# Helper function to extract the underlying numpy array.
def get_image_data(image_format):
    # Adjust this if your OpenCVImageFormat stores the data differently.
    return image_format.data if hasattr(image_format, "data") else image_format


@pytest.fixture
def image1():
    return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)


@pytest_funcnodes.nodetest(normalize)
async def test_normalize(image1):
    result = (await normalize.inti_call(img=image1))[1]
    np.testing.assert_array_equal(
        result, cv2.normalize(image1, None, 0, 255, cv2.NORM_MINMAX)
    )


@pytest_funcnodes.nodetest(equalizeHist)
async def test_equalizeHist(image1):
    result = get_image_data(await equalizeHist.inti_call(img=image1))
    np.testing.assert_array_equal(
        result[:, :, 0], cv2.equalizeHist(cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY))
    )


@pytest_funcnodes.nodetest(CLAHE)
async def test_CLAHE(image1):
    result = get_image_data(await CLAHE.inti_call(img=image1))
    np.testing.assert_array_equal(
        result[:, :, 0],
        cv2.createCLAHE(clipLimit=40.0, tileGridSize=(8, 8)).apply(
            cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        ),
    )
