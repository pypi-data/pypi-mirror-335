import numpy as np
import pytest
import pytest_funcnodes
from funcnodes_opencv.image_operations.matrix_operations import (
    merge,
    split,
    transpose,
    repeat,
    getAffineTransform,
    getPerspectiveTransform,
    getPerspectiveTransform_points,
    getAffineTransform_points,
)


# Helper function to extract the underlying numpy array.
def get_image_data(image_format):
    # Adjust this if your OpenCVImageFormat stores the data differently.
    return image_format.data if hasattr(image_format, "data") else image_format


@pytest.fixture
def image1():
    return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)


@pytest.fixture
def image2():
    return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)


@pytest_funcnodes.nodetest(merge)
async def test_merge(image1, image2):
    result = get_image_data(
        await merge.inti_call(
            channels=[image1[:, :, 0], image2[:, :, 1], image1[:, :, 1]]
        )
    )
    assert result.shape == (100, 100, 3)
    np.testing.assert_array_equal(result[:, :, 0], image1[:, :, 0])
    np.testing.assert_array_equal(result[:, :, 1], image2[:, :, 1])
    np.testing.assert_array_equal(result[:, :, 2], image1[:, :, 1])


@pytest_funcnodes.nodetest(split)
async def test_split(image1):
    result = await split.inti_call(img=image1)
    assert len(result) == 3
    np.testing.assert_array_equal(get_image_data(result[0])[:, :, 0], image1[:, :, 0])
    np.testing.assert_array_equal(get_image_data(result[1])[:, :, 0], image1[:, :, 1])
    np.testing.assert_array_equal(get_image_data(result[2])[:, :, 0], image1[:, :, 2])


@pytest_funcnodes.nodetest(transpose)
async def test_transpose(image1):
    result = get_image_data(await transpose.inti_call(img=image1))
    assert result.shape == (100, 100, 3)
    np.testing.assert_array_equal(result[:, :, 0], image1[:, :, 0].T)
    np.testing.assert_array_equal(result[:, :, 1], image1[:, :, 1].T)
    np.testing.assert_array_equal(result[:, :, 2], image1[:, :, 2].T)


@pytest_funcnodes.nodetest(repeat)
async def test_repeat(image1):
    result = get_image_data(await repeat.inti_call(img=image1, ny=2, nx=3))
    assert result.shape == (200, 300, 3)
    np.testing.assert_array_equal(result[:100, :100, :], image1)
    np.testing.assert_array_equal(result[100:, :100, :], image1)
    np.testing.assert_array_equal(result[:100, 100:200, :], image1)
    np.testing.assert_array_equal(result[:100, 200:, :], image1)


@pytest_funcnodes.nodetest(getAffineTransform)
async def test_getAffineTransform():
    result = await getAffineTransform.inti_call(
        src=np.array([[0, 0], [0, 100], [100, 0]]),
        dst=np.array([[0, 0], [0, 100], [100, 0]]),
    )
    assert result.shape == (2, 3)


@pytest_funcnodes.nodetest(getPerspectiveTransform)
async def test_getPerspectiveTransform():
    result = await getPerspectiveTransform.inti_call(
        src=np.array([[0, 0], [0, 100], [100, 0], [100, 100]]),
        dst=np.array([[0, 0], [0, 100], [100, 0], [100, 100]]),
    )
    assert result.shape == (3, 3)


@pytest_funcnodes.nodetest(getPerspectiveTransform_points)
async def test_getPerspectiveTransform_points():
    result = await getPerspectiveTransform_points.inti_call(
        i1x1=0,
        i1y1=0,
        i1x2=0,
        i1y2=100,
        i1x3=100,
        i1y3=0,
        i1x4=100,
        i1y4=100,
        i2x1=0,
        i2y1=0,
        i2x2=0,
        i2y2=100,
        i2x3=100,
        i2y3=0,
        i2x4=100,
        i2y4=100,
    )
    assert result.shape == (3, 3)


@pytest_funcnodes.nodetest(getAffineTransform_points)
async def test_getAffineTransform_points():
    result = await getAffineTransform_points.inti_call(
        i1x1=0,
        i1y1=0,
        i1x2=0,
        i1y2=100,
        i1x3=100,
        i1y3=0,
        i2x1=0,
        i2y1=0,
        i2x2=0,
        i2y2=100,
        i2x3=100,
        i2y3=0,
    )
    assert result.shape == (2, 3)
