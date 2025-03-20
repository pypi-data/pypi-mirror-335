import numpy as np
import cv2
import pytest
import pytest_funcnodes
from funcnodes_opencv.image_processing.thresholding import (
    threshold,
    auto_threshold,
    adaptive_threshold,
    in_range_singel_channel,
    in_range,
    AutoThresholdTypes,
    AdaptiveThresholdMethods,
)


def get_image_data(image_format):
    return image_format.data if hasattr(image_format, "data") else image_format


@pytest.fixture
def image1():
    return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)


@pytest_funcnodes.nodetest(threshold)
async def test_threshold(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await threshold.inti_call(
                img=image1, thresh=127, maxval=255, type=cv2.THRESH_BINARY
            )
        ),
        cv2.threshold(image1, 127, 255, cv2.THRESH_BINARY)[1],
    )


@pytest_funcnodes.nodetest(auto_threshold)
async def test_auto_threshold(image1):
    np.testing.assert_array_equal(
        get_image_data(
            (
                await auto_threshold.inti_call(
                    img=image1, maxval=255, type=AutoThresholdTypes.OTSU
                )
            )[0]
        )[:, :, 0],
        cv2.threshold(
            cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY),
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )[1],
    )


@pytest_funcnodes.nodetest(adaptive_threshold)
async def test_adaptive_threshold(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await adaptive_threshold.inti_call(
                img=image1,
                maxval=255,
                method=AdaptiveThresholdMethods.MEAN_C,
                block_size=5,
                c=2,
            )
        )[:, :, 0],
        cv2.adaptiveThreshold(
            cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY),
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            2 * 5 + 1,
            2,
        ),
    )


@pytest_funcnodes.nodetest(in_range_singel_channel)
async def test_in_range_singel_channel(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await in_range_singel_channel.inti_call(img=image1, lower=100, upper=200)
        )[:, :, 0],
        cv2.inRange(cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY), 100, 200),
    )


@pytest_funcnodes.nodetest(in_range)
async def test_in_range(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await in_range.inti_call(
                img=image1,
                lower_c1=100,
                upper_c1=200,
                lower_c2=100,
                upper_c2=200,
                lower_c3=100,
                upper_c3=200,
            )
        )[:, :, 0],
        cv2.inRange(image1, np.array([100, 100, 100]), np.array([200, 200, 200])),
    )
