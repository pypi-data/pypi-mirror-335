import numpy as np
import cv2
import pytest
import pytest_funcnodes
from funcnodes_opencv.image_processing.geometric_transformations import (
    flip,
    rotate,
    resize,
    warpAffine,
    perpectiveTransform,
    freeRotation,
    pyrDown,
    pyrUp,
    FreeRotationCropMode,
)


def get_image_data(image_format):
    return image_format.data if hasattr(image_format, "data") else image_format


@pytest.fixture
def image1():
    return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)


@pytest_funcnodes.nodetest(flip)
async def test_flip(image1):
    np.testing.assert_array_equal(
        (get_image_data(await flip.inti_call(img=image1))), cv2.flip(image1, 1)
    )


@pytest_funcnodes.nodetest(rotate)
async def test_rotate(image1):
    np.testing.assert_array_equal(
        (get_image_data(await rotate.inti_call(img=image1))),
        cv2.rotate(image1, cv2.ROTATE_90_CLOCKWISE),
    )


@pytest_funcnodes.nodetest(resize)
async def test_resize(image1):
    np.testing.assert_array_equal(
        (get_image_data(await resize.inti_call(img=image1, fh=2))),
        cv2.resize(image1, (100, 200)),
    )


@pytest_funcnodes.nodetest(warpAffine)
async def test_warpAffine(image1):
    M = cv2.getRotationMatrix2D((50, 50), 45, 1)
    np.testing.assert_array_equal(
        (get_image_data(await warpAffine.inti_call(img=image1, M=M))),
        cv2.warpAffine(image1, M, (100, 100)),
    )


@pytest_funcnodes.nodetest(perpectiveTransform)
async def test_perpectiveTransform(image1):
    M = cv2.getPerspectiveTransform(
        np.array([[0, 0], [0, 100], [100, 0], [100, 100]], dtype=np.float32),
        np.array([[0, 0], [0, 100], [100, 0], [100, 100]], dtype=np.float32),
    )
    np.testing.assert_array_equal(
        (get_image_data(await perpectiveTransform.inti_call(img=image1, M=M))),
        cv2.warpPerspective(image1, M, (100, 100)),
    )


@pytest_funcnodes.nodetest(freeRotation)
@pytest.mark.parametrize(
    "crop_mode",
    [FreeRotationCropMode.CROP, FreeRotationCropMode.KEEP, FreeRotationCropMode.NONE],
)
async def test_freeRotation(image1, crop_mode):
    results = await freeRotation.inti_call(img=image1, angle=45, mode=crop_mode)
    arr, M = get_image_data(results[0]), results[1]
    if crop_mode == FreeRotationCropMode.NONE:
        assert arr.shape == (100, 100, 3)
    elif crop_mode == FreeRotationCropMode.KEEP:
        assert arr.shape == (141, 141, 3)
    elif crop_mode == FreeRotationCropMode.CROP:
        assert arr.shape == (70, 70, 3)
    else:
        raise ValueError("Invalid crop mode")
    np.testing.assert_array_equal(arr, cv2.warpAffine(image1, M, arr.shape[:2][::-1]))


@pytest_funcnodes.nodetest(pyrDown)
async def test_pyrDown(image1):
    np.testing.assert_array_equal(
        (get_image_data(await pyrDown.inti_call(img=image1))),
        cv2.pyrDown(image1),
    )


@pytest_funcnodes.nodetest(pyrUp)
async def test_pyrUp(image1):
    np.testing.assert_array_equal(
        (get_image_data(await pyrUp.inti_call(img=image1))),
        cv2.pyrUp(image1),
    )
