import numpy as np
import cv2
import pytest
import pytest_funcnodes
from funcnodes_opencv.segmentation import (
    ContourApproximationModes,
    RetrievalModes,
    findContours,
    DistanceTypes,
    distance_transform,
    watershed,
)


def get_image_data(image_format):
    return image_format.data if hasattr(image_format, "data") else image_format


@pytest.fixture
def image1():
    return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)


@pytest_funcnodes.nodetest(findContours)
async def test_findContours(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await findContours.inti_call(
                img=image1,
                mode=RetrievalModes.EXTERNAL,
                method=ContourApproximationModes.SIMPLE,
            )
        ),
        cv2.findContours(
            cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )[0],
    )


@pytest_funcnodes.nodetest(distance_transform)
async def test_distance_transform(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await distance_transform.inti_call(
                img=image1, distance_type=DistanceTypes.L2
            )
        )[..., 0],
        cv2.distanceTransform(cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY), cv2.DIST_L2, 3),
    )


@pytest_funcnodes.nodetest(watershed)
async def test_watershed(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await watershed.inti_call(
                img=image1,
                markers=cv2.connectedComponents(
                    cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
                )[1],
            )
        ),
        cv2.watershed(
            image1,
            cv2.connectedComponents(cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY))[1],
        ),
    )
