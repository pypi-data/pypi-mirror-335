import numpy as np
import cv2
import pytest
import pytest_funcnodes
from funcnodes_opencv.image_processing.filtering_smoothing import (
    blur,
    gaussianBlur,
    medianBlur,
    bilateralFilter,
    stackBlur,
    boxFilter,
    filter2D,
)


# Helper function to extract the underlying numpy array.
def get_image_data(image_format):
    # Adjust this if your OpenCVImageFormat stores the data differently.
    return image_format.data if hasattr(image_format, "data") else image_format


@pytest.fixture
def image1():
    return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)


@pytest.mark.parametrize(
    "kw",
    np.arange(1, 5),
)
@pytest.mark.parametrize(
    "kh",
    np.arange(0, 5),
)
@pytest_funcnodes.nodetest(blur)
async def test_blur(image1, kw, kh):
    np.testing.assert_array_equal(
        get_image_data(await blur.inti_call(img=image1, kw=kw, kh=kh)),
        cv2.blur(image1, (kw, kh if kh > 0 else kw)),
    )


@pytest.mark.parametrize(
    "kw",
    np.arange(1, 5),
)
@pytest.mark.parametrize(
    "kh",
    np.arange(0, 5),
)
@pytest_funcnodes.nodetest(gaussianBlur)
async def test_gaussianBlur(image1, kw, kh):
    _kh = kh if kh > 0 else kw
    if _kh % 2 == 0:
        _kh += 1
    np.testing.assert_array_equal(
        get_image_data(await gaussianBlur.inti_call(img=image1, kw=kw, kh=kh)),
        cv2.GaussianBlur(image1, (kw + 1 if kw % 2 == 0 else kw, _kh), 0),
    )


@pytest.mark.parametrize(
    "ksize",
    np.arange(0, 5),
)
@pytest_funcnodes.nodetest(medianBlur)
async def test_medianBlur(image1, ksize):
    np.testing.assert_array_equal(
        get_image_data(await medianBlur.inti_call(img=image1, ksize=ksize)),
        cv2.medianBlur(image1, ksize if ksize % 2 != 0 else ksize + 1),
    )


@pytest.mark.parametrize(
    "d",
    np.arange(0, 5),
)
@pytest.mark.parametrize(
    "sigmaColor",
    np.arange(0, 5),
)
@pytest.mark.parametrize(
    "sigmaSpace",
    np.arange(0, 5),
)
@pytest_funcnodes.nodetest(bilateralFilter)
async def test_bilateralFilter(image1, d, sigmaColor, sigmaSpace):
    np.testing.assert_array_equal(
        get_image_data(
            await bilateralFilter.inti_call(
                img=image1, d=d, sigmaColor=sigmaColor, sigmaSpace=sigmaSpace
            )
        ),
        cv2.bilateralFilter(image1, d, sigmaColor, sigmaSpace),
    )


@pytest.mark.parametrize(
    "kw",
    np.arange(1, 5),
)
@pytest.mark.parametrize(
    "kh",
    np.arange(0, 5),
)
@pytest_funcnodes.nodetest(stackBlur)
async def test_stackBlur(image1, kw, kh):
    np.testing.assert_array_equal(
        get_image_data(await stackBlur.inti_call(img=image1, kw=kw, kh=kh)),
        cv2.stackBlur(
            image1, (kw + 1 if kw % 2 == 0 else kw, kh + 1 if kh % 2 == 0 else kh)
        ),
    )


@pytest.mark.parametrize(
    "kw",
    np.arange(1, 5),
)
@pytest.mark.parametrize(
    "kh",
    np.arange(1, 5),
)
@pytest_funcnodes.nodetest(boxFilter)
async def test_boxFilter(image1, kw, kh):
    np.testing.assert_array_equal(
        get_image_data(await boxFilter.inti_call(img=image1, kw=kw, kh=kh)),
        cv2.boxFilter(image1, -1, (kw, kh)),
    )


@pytest_funcnodes.nodetest(filter2D)
async def test_filter2D(image1):
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    np.testing.assert_array_equal(
        get_image_data(await filter2D.inti_call(img=image1, ddepth=-1, kernel=kernel)),
        cv2.filter2D(image1, -1, kernel),
    )
