import numpy as np
import cv2
import pytest
import pytest_funcnodes
from funcnodes_opencv.image_operations.arithmetic_operations import (
    add,
    subtract,
    multiply,
    divide,
    addWeighted,
    where,
    brighten,
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


# --- Tests for arithmetic nodes ---


@pytest_funcnodes.nodetest(add)
async def test_add(image1, image2):
    # cv2.add performs pixel-wise saturated addition.
    np.testing.assert_array_equal(
        get_image_data(await add.inti_call(img1=image1, img2=image2)),
        cv2.add(image1, image2),
    )


@pytest_funcnodes.nodetest(subtract)
async def test_subtract(image1, image2):
    # Test subtraction: subtract image1 from image2 (100-50 = 50) with saturation.
    np.testing.assert_array_equal(
        get_image_data(await subtract.inti_call(img1=image1, img2=image2)),
        cv2.subtract(image1, image2),
    )


@pytest_funcnodes.nodetest(multiply)
async def test_multiply(image1, image2):
    # Test pixel-wise multiplication.
    np.testing.assert_array_equal(
        get_image_data(await multiply.inti_call(img1=image1, img2=image2)),
        cv2.multiply(image1, image2),
    )


@pytest_funcnodes.nodetest(divide)
async def test_divide(image2, image1):
    # Ensure no division by zero; here image2 divided by image1 (100/50 = 2).
    np.testing.assert_array_equal(
        get_image_data(await divide.inti_call(img1=image1, img2=image2)),
        cv2.divide(image1, image2),
    )


@pytest_funcnodes.nodetest(addWeighted)
async def test_addWeighted(image1, image2):
    # Test weighted addition: 0.7*image1 + 0.3*image2 + 10.
    np.testing.assert_array_equal(
        get_image_data(await addWeighted.inti_call(img1=image1, img2=image2)),
        cv2.addWeighted(image1, 0.7, image2, 0.3, 10),
    )


@pytest_funcnodes.nodetest(where)
async def test_where_with_int(image1, mask):
    # For positions where mask is nonzero, set the pixel value to 200.
    result = await where.inti_call(img=image1, mask=mask, value=200)
    expected = image1.copy()
    expected[mask != 0] = 200
    np.testing.assert_array_equal(get_image_data(result), expected)


@pytest_funcnodes.nodetest(where)
async def test_where_with_image(image1, mask, image2):
    # Use image2 as the source for replacement where mask is nonzero.
    result = await where.inti_call(img=image1, mask=mask, value=image2)
    expected = image1.copy()
    expected[mask != 0] = image2[mask != 0]
    np.testing.assert_array_equal(get_image_data(result), expected)


@pytest_funcnodes.nodetest(brighten)
async def test_brighten(image1):
    # Brighten the image by adding a value (e.g. 30) and then clipping to [0, 255].
    result = await brighten.inti_call(img=image1, value=30)
    expected = np.clip(image1 + 30, 0, 255)
    np.testing.assert_array_equal(get_image_data(result), expected)
