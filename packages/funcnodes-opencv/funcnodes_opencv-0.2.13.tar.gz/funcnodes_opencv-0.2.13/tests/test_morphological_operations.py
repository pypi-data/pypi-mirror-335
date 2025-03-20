import numpy as np
import cv2
import pytest
import pytest_funcnodes
from funcnodes_opencv.image_processing.morphological_operations import (
    dilate,
    erode,
    morphologyEx,
    MorphologicalOperations,
)


def get_image_data(image_format):
    return image_format.data if hasattr(image_format, "data") else image_format


@pytest.fixture
def image1():
    return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)


@pytest_funcnodes.nodetest(dilate)
async def test_dilate(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await dilate.inti_call(
                img=image1, kernel=np.ones((5, 5), np.uint8), iterations=1
            )
        ),
        cv2.dilate(image1, np.ones((5, 5), np.uint8), iterations=1),
    )


@pytest_funcnodes.nodetest(erode)
async def test_erode(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await erode.inti_call(
                img=image1, kernel=np.ones((5, 5), np.uint8), iterations=1
            )
        ),
        cv2.erode(image1, np.ones((5, 5), np.uint8), iterations=1),
    )


@pytest.mark.parametrize(
    "operation",
    [
        MorphologicalOperations.OPEN,
        MorphologicalOperations.CLOSE,
        MorphologicalOperations.GRADIENT,
        MorphologicalOperations.TOPHAT,
        MorphologicalOperations.BLACKHAT,
        MorphologicalOperations.HITMISS,
    ],
)
@pytest_funcnodes.nodetest(morphologyEx)
async def test_morphologyEx(image1, operation):
    res = get_image_data(
        await morphologyEx.inti_call(
            img=image1,
            op=operation,
            kernel=np.ones((5, 5), np.uint8),
            iterations=1,
        )
    )
    np.testing.assert_array_equal(
        res if operation != MorphologicalOperations.HITMISS else res[..., 0],
        cv2.morphologyEx(
            image1
            if operation != MorphologicalOperations.HITMISS
            else cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY),
            operation.value,
            np.ones((5, 5), np.uint8),
            iterations=1,
        ),
    )
