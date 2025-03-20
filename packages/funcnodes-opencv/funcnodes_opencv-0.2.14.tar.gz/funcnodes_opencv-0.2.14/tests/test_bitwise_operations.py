import numpy as np
import cv2
import pytest
import pytest_funcnodes
from funcnodes_opencv.image_operations.bitwise_operations import (
    bitwise_and,
    bitwise_or,
    bitwise_xor,
    bitwise_not,
)


# Helper function to extract the underlying numpy array.
def get_image_data(image_format):
    # Adjust this if your OpenCVImageFormat stores the data differently.
    return image_format.data if hasattr(image_format, "data") else image_format


# --- Fixtures: Create sample images and masks ---
@pytest.fixture
def image1():
    # Create a 3x3 image (3 channels) with all pixel values 50
    return np.full((3, 3, 3), 50, dtype=np.uint8)


@pytest.fixture
def image2():
    # Create a 3x3 image (3 channels) with all pixel values 100
    return np.full((3, 3, 3), 100, dtype=np.uint8)


@pytest.fixture
def mask():
    # Create a single channel 3x3 mask with alternating 255 and 0 values
    return np.array([[255, 0, 255], [0, 255, 0], [255, 0, 255]], dtype=np.uint8)


# --- Tests for bitwise nodes ---
@pytest_funcnodes.nodetest(bitwise_and)
async def test_bitwise_and(image1, image2, mask):
    # cv2.bitwise_and performs pixel-wise bitwise AND operation.
    np.testing.assert_array_equal(
        get_image_data(
            await bitwise_and.inti_call(img1=image1, img2=image2, mask=mask)
        ),
        cv2.bitwise_and(image1, image2, mask=mask),
    )


@pytest_funcnodes.nodetest(bitwise_or)
async def test_bitwise_or(image1, image2, mask):
    # cv2.bitwise_or performs pixel-wise bitwise OR operation.
    np.testing.assert_array_equal(
        get_image_data(await bitwise_or.inti_call(img1=image1, img2=image2, mask=mask)),
        cv2.bitwise_or(image1, image2, mask=mask),
    )


@pytest_funcnodes.nodetest(bitwise_xor)
async def test_bitwise_xor(image1, image2, mask):
    # cv2.bitwise_xor performs pixel-wise bitwise XOR operation.
    np.testing.assert_array_equal(
        get_image_data(
            await bitwise_xor.inti_call(img1=image1, img2=image2, mask=mask)
        ),
        cv2.bitwise_xor(image1, image2, mask=mask),
    )


@pytest_funcnodes.nodetest(bitwise_not)
async def test_bitwise_not(image1, mask):
    # cv2.bitwise_not performs pixel-wise bitwise NOT operation.
    np.testing.assert_array_equal(
        get_image_data(await bitwise_not.inti_call(img=image1, mask=mask)),
        cv2.bitwise_not(image1, mask=mask),
    )
