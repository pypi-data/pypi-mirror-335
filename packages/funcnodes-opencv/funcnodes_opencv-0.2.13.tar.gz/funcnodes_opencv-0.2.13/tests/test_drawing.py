import numpy as np
import cv2
import pytest
import pytest_funcnodes
from funcnodes_opencv.drawing import (
    line,
    rectangle,
    circle,
    ellipse,
    putText,
    arrowedLine,
    polylines,
    fillPoly,
    fillConvexPoly,
    drawContours,
    drawMarker,
    MarkerTypes,
    labels_to_color,
)


def get_image_data(image_format):
    return image_format.data if hasattr(image_format, "data") else image_format


@pytest.fixture
def image1():
    return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)


@pytest_funcnodes.nodetest(line)
async def test_line(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await line.inti_call(
                img=image1,
                start_x=0,
                start_y=0,
                end_x=90,
                end_y=90,
                color="#FF0000",
                thickness=2,
            )
        ),
        cv2.line(image1, (0, 0), (90, 90), (0, 0, 255), 2, cv2.LINE_8),
    )


@pytest_funcnodes.nodetest(rectangle)
async def test_rectangle(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await rectangle.inti_call(
                img=image1,
                x=0,
                y=0,
                width=90,
                height=90,
                color="#FF0000",
                thickness=2,
            )
        ),
        cv2.rectangle(image1, (0, 0), (90, 90), (0, 0, 255), 2, cv2.LINE_8),
    )


@pytest_funcnodes.nodetest(circle)
async def test_circle(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await circle.inti_call(
                img=image1,
                center_x=50,
                center_y=50,
                radius=40,
                color="#FF0000",
                thickness=2,
            )
        ),
        cv2.circle(image1, (50, 50), 40, (0, 0, 255), 2, cv2.LINE_8),
    )


@pytest_funcnodes.nodetest(ellipse)
async def test_ellipse(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await ellipse.inti_call(
                img=image1,
                center_x=50,
                center_y=50,
                axes_x=40,
                axes_y=20,
                angle=0,
                start_angle=0,
                end_angle=360,
                color="#FF0000",
                thickness=2,
            )
        ),
        cv2.ellipse(image1, (50, 50), (40, 20), 0, 0, 360, (0, 0, 255), 2, cv2.LINE_8),
    )


@pytest_funcnodes.nodetest(putText)
async def test_putText(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await putText.inti_call(
                img=image1,
                text="Hello",
                org_x=10,
                org_y=10,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1,
                color="#FF0000",
                thickness=2,
            )
        ),
        cv2.putText(
            image1, "Hello", (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2
        ),
    )


@pytest_funcnodes.nodetest(arrowedLine)
async def test_arrowedLine(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await arrowedLine.inti_call(
                img=image1,
                start_x=0,
                start_y=0,
                end_x=90,
                end_y=90,
                color="#FF0000",
                thickness=2,
            )
        ),
        cv2.arrowedLine(image1, (0, 0), (90, 90), (0, 0, 255), 2, cv2.LINE_8),
    )


@pytest_funcnodes.nodetest(polylines)
async def test_polylines(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await polylines.inti_call(
                img=image1,
                pts=np.array([[10, 10], [20, 20], [30, 30]]),
                isClosed=True,
                color="#FF0000",
                thickness=2,
            )
        ),
        cv2.polylines(
            image1,
            [np.array([[10, 10], [20, 20], [30, 30]])],
            True,
            (0, 0, 255),
            2,
            cv2.LINE_8,
        ),
    )


@pytest_funcnodes.nodetest(fillPoly)
async def test_fillPoly(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await fillPoly.inti_call(
                img=image1,
                pts=np.array([[10, 10], [20, 20], [30, 30]]),
                color="#FF0000",
            )
        ),
        cv2.fillPoly(image1, [np.array([[10, 10], [20, 20], [30, 30]])], (0, 0, 255)),
    )


@pytest_funcnodes.nodetest(fillConvexPoly)
async def test_fillConvexPoly(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await fillConvexPoly.inti_call(
                img=image1,
                pts=np.array([[10, 10], [20, 20], [30, 30]]),
                color="#FF0000",
            )
        ),
        cv2.fillConvexPoly(
            image1, np.array([[10, 10], [20, 20], [30, 30]]), (0, 0, 255)
        ),
    )


@pytest_funcnodes.nodetest(drawContours)
async def test_drawContours(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await drawContours.inti_call(
                img=image1,
                contours=[np.array([[10, 10], [20, 20], [30, 30]])],
                color="#FF0000",
                thickness=2,
            )
        ),
        cv2.drawContours(
            image1,
            [np.array([[10, 10], [20, 20], [30, 30]])],
            -1,
            (0, 0, 255),
            2,
            cv2.LINE_8,
        ),
    )


@pytest_funcnodes.nodetest(drawMarker)
async def test_drawMarker(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await drawMarker.inti_call(
                img=image1,
                pos_x=10,
                pos_y=10,
                markerType=MarkerTypes.CROSS,
                markerSize=10,
                color="#FF0000",
                thickness=2,
            )
        ),
        cv2.drawMarker(
            image1,
            (10, 10),
            markerType=cv2.MARKER_CROSS,
            markerSize=10,
            color=(0, 0, 255),
            thickness=2,
            line_type=cv2.LINE_8,
        ),
    )


@pytest_funcnodes.nodetest(labels_to_color)
async def test_labels_to_color(image1):
    np.testing.assert_array_equal(
        get_image_data(
            await labels_to_color.inti_call(
                labels=np.array([[0, 1], [2, 0]]), mix=False
            )
        ),
        np.array(
            [[[128, 0, 0], [130, 255, 126]], [[0, 0, 128], [128, 0, 0]]], dtype=np.uint8
        ),
    )
