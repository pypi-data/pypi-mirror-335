# Segmentation & Contour Analysis

from typing import Literal, Tuple, List, Union
import funcnodes as fn
import cv2
import numpy as np
from .imageformat import ImageFormat, NumpyImageFormat
from .utils import normalize, assert_opencvdata


class RetrievalModes(fn.DataEnum):
    """
    Mode of the contour retrieval algorithm.

    Attributes:
        EXTERNAL: cv2.RETR_EXTERNAL: retrieves only the extreme outer contours.
            It sets hierarchy[i][2]=hierarchy[i][3]=-1 for all the contours and leaves them as leaves of the
            outer contour list. It sets hierarchy[i][2]=hierarchy[i][3]=-1 for all the contours.
        LIST: cv2.RETR_LIST: retrieves all of the contours without establishing any hierarchical relationships.
        CCOMP: cv2.RETR_CCOMP: retrieves all of the contours and organizes them into a two-level hierarchy.
        TREE: cv2.RETR_TREE: retrieves all of the contours and reconstructs a full hierarchy of nested contours.
        FLOODFILL: cv2.RETR_FLOODFILL
    """

    EXTERNAL = cv2.RETR_EXTERNAL
    LIST = cv2.RETR_LIST
    CCOMP = cv2.RETR_CCOMP
    TREE = cv2.RETR_TREE
    FLOODFILL = cv2.RETR_FLOODFILL


class ContourApproximationModes(fn.DataEnum):
    """
    Approximation modes for the contour retrieval algorithm.

    Attributes:
        NONE: cv2.CHAIN_APPROX_NONE: stores absolutely all the contour points.
        SIMPLE: cv2.CHAIN_APPROX_SIMPLE: compresses horizontal, vertical, and diagonal segments
        TC89_L1: cv2.CHAIN_APPROX_TC89_L1: applies one of the flavors of the Teh-Chin chain approximation algorithm
        TC89_KCOS: cv2.CHAIN_APPROX_TC89_KCOS: applies one of the flavors of the Teh-Chin chain approximation algorithm
    """

    NONE = cv2.CHAIN_APPROX_NONE
    SIMPLE = cv2.CHAIN_APPROX_SIMPLE
    TC89_L1 = cv2.CHAIN_APPROX_TC89_L1
    TC89_KCOS = cv2.CHAIN_APPROX_TC89_KCOS


@fn.NodeDecorator(
    "cv2.findContours",
    name="findContours",
    outputs=[
        {"name": "contours"},
    ],
    description="Finds contours in a binary image.",
)
@fn.controlled_wrapper(cv2.findContours, wrapper_attribute="__fnwrapped__")
def findContours(
    img: ImageFormat,
    mode: RetrievalModes = RetrievalModes.EXTERNAL,
    method: ContourApproximationModes = ContourApproximationModes.SIMPLE,
    offset_dx: int = 0,
    offset_dy: int = 0,
) -> List[np.ndarray]:
    offset = (offset_dx, offset_dy)
    mode = RetrievalModes.v(mode)
    method = ContourApproximationModes.v(method)

    contours, hierarchy = cv2.findContours(
        image=assert_opencvdata(img, 1),
        mode=mode,
        method=method,
        offset=offset,
    )

    return list(contours)


class DistanceTypes(fn.DataEnum):
    """
    Distance transform types.

    Attributes:
        L1: cv2.DIST_L1: distance = |x1-x2| + |y1-y2|
        L2: cv2.DIST_L2: the Euclidean distance
        C: cv2.DIST_C: distance = max(|x1-x2|, |y1-y2|)
        L12: cv2.DIST_L12: L1-L2 metric: distance = 2 * (sqrt(1 + |x1-x2|^2/2) - 1)
        FAIR: cv2.DIST_FAIR: distance = c^2 * (sqrt(1 + |x1-x2|^2/c^2) - 1)
        WELSCH: cv2.DIST_WELSCH: distance = c^2/2 * (1 - exp(-|x1-x2|^2/c^2))
        HUBER: cv2.DIST_HUBER: distance = |x1-x2| if |x1-x2| <= c else c * (|x1-x2| - c/2)
    """

    L1 = cv2.DIST_L1
    L2 = cv2.DIST_L2
    C = cv2.DIST_C
    L12 = cv2.DIST_L12
    FAIR = cv2.DIST_FAIR
    WELSCH = cv2.DIST_WELSCH
    HUBER = cv2.DIST_HUBER


@fn.NodeDecorator(
    node_id="cv2.distance_transform",
    default_render_options={"data": {"src": "out"}},
    description="Calculates the distance to the closest zero pixel for each pixel of the source image.",
)
def distance_transform(
    img: ImageFormat,
    distance_type: DistanceTypes = DistanceTypes.L1,
    mask_size: Literal[0, 3, 5] = 3,
) -> NumpyImageFormat:
    return NumpyImageFormat(
        cv2.distanceTransform(
            assert_opencvdata(img, channel=1),
            DistanceTypes.v(distance_type),
            int(mask_size),
        )
    )


@fn.NodeDecorator(
    node_id="cv2.connectedComponents",
    outputs=[
        {"name": "retval", "type": int},
        {"name": "labels", "type": np.ndarray},
    ],
    description="Finds connected components in a binary image.",
)
def connectedComponents(
    img: ImageFormat,
    connectivity: Literal[4, 8] = 8,
) -> Tuple[int, np.ndarray]:
    connectivity = int(connectivity)
    data = assert_opencvdata(img, 1)
    img = normalize(data)
    retval, labels = cv2.connectedComponents(img, connectivity=connectivity)
    return retval, labels


@fn.NodeDecorator(
    node_id="cv2.watershed",
    description="Performs a marker-based image segmentation using the watershed algorithm.",
)
def watershed(
    img: ImageFormat,
    markers: Union[ImageFormat, np.ndarray],
) -> np.ndarray:
    markers: np.ndarray = assert_opencvdata(markers, 1)
    img = assert_opencvdata(img)
    markers = markers.astype(np.int32)

    return cv2.watershed(img, markers)


NODE_SHELF = fn.Shelf(
    name="Segmentation & Contour Analysis",
    nodes=[findContours, distance_transform, watershed],
    subshelves=[],
    description="Segmentation and contour analysis nodes.",
)
