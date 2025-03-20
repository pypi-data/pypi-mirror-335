from typing import Union, Optional, Tuple, List
import cv2
import numpy as np
import funcnodes as fn
from .imageformat import OpenCVImageFormat, ImageFormat
from .utils import assert_opencvdata


def rgb_from_hexstring(hexstring: str) -> Tuple[int, int, int]:
    if hexstring.startswith("#"):
        hexstring = hexstring[1:]
    return tuple(int(hexstring[i : i + 2], 16) for i in (0, 2, 4))


class LineTypes(fn.DataEnum):
    LINE_4 = cv2.LINE_4
    LINE_8 = cv2.LINE_8
    LINE_AA = cv2.LINE_AA
    FILLED = cv2.FILLED


@fn.NodeDecorator(
    "cv2.circle",
    name="circle",
    default_render_options={
        "io": {
            "color": {"type": "color"},
        },
        "data": {"src": "out"},
    },
    description="Draws a circle on an image.",
)
@fn.controlled_wrapper(cv2.circle, wrapper_attribute="__fnwrapped__")
def circle(
    img: ImageFormat,
    center_x: Union[float, List[float], int, List[int]],
    center_y: Union[float, List[float], int, List[int]],
    radius: Union[float, List[float], int, List[int]],
    color: Optional[str] = "00FF00",
    thickness: int = 1,
    lineType: LineTypes = LineTypes.LINE_8,
    shift: int = 0,
) -> OpenCVImageFormat:
    if isinstance(center_x, (float, int)):
        center_x = [center_x]
    if isinstance(center_y, (float, int)):
        center_y = [center_y]
    if isinstance(radius, (float, int)):
        radius = [radius]
    assert len(center_x) == len(center_y) == len(radius), (
        "center_x, center_y, and radius lists must have the same length"
    )
    color = rgb_from_hexstring(color)

    color = color[::-1]
    lineType = LineTypes.v(lineType)
    img = assert_opencvdata(img, 3)

    for i in range(len(center_x)):
        cent = (int(center_x[i]), int(center_y[i]))
        rad = int(radius[i])
        img = cv2.circle(
            img=img,
            center=cent,
            radius=rad,
            color=color,
            thickness=thickness,
            lineType=lineType,
            shift=int(shift),
        )
    return OpenCVImageFormat(img)


@fn.NodeDecorator(
    "cv2.ellipse",
    name="ellipse",
    default_render_options={
        "io": {
            "color": {"type": "color"},
        },
        "data": {"src": "out"},
    },
    description="Draws an ellipse on an image.",
)
@fn.controlled_wrapper(cv2.ellipse, wrapper_attribute="__fnwrapped__")
def ellipse(
    img: ImageFormat,
    center_x: Union[float, List[float], int, List[int]],
    center_y: Union[float, List[float], int, List[int]],
    axes_x: Union[float, List[float], int, List[int]],
    axes_y: Union[float, List[float], int, List[int]],
    angle: Union[float, List[float], int, List[int]],
    start_angle: int = 0,
    end_angle: int = 360,
    color: Optional[str] = "00FF00",
    thickness: int = 1,
    lineType: LineTypes = LineTypes.LINE_8,
    shift: int = 0,
) -> OpenCVImageFormat:
    if isinstance(center_x, (float, int)):
        center_x = [center_x]
    if isinstance(center_y, (float, int)):
        center_y = [center_y]
    if isinstance(axes_x, (float, int)):
        axes_x = [axes_x]
    if isinstance(axes_y, (float, int)):
        axes_y = [axes_y]
    if isinstance(angle, (float, int)):
        angle = [angle]

    assert len(center_x) == len(center_y) == len(axes_x) == len(axes_y) == len(angle), (
        "center_x, center_y, axes_x, axes_y, and angle lists must have the same length"
    )
    color = rgb_from_hexstring(color)
    color = color[::-1]
    lineType = LineTypes.v(lineType)
    img = assert_opencvdata(img, 3)
    for i in range(len(center_x)):
        center = (int(center_x[i]), int(center_y[i]))
        axes = (int(axes_x[i]), int(axes_y[i]))
        ang = int(angle[i])
        OpenCVImageFormat(
            cv2.ellipse(
                img=img,
                center=center,
                axes=axes,
                angle=ang,
                startAngle=start_angle,
                endAngle=end_angle,
                color=color,
                thickness=thickness,
                lineType=lineType,
                shift=int(shift),
            )
        )
    return img


@fn.NodeDecorator(
    node_id="cv2.line",
    name="line",
    default_render_options={
        "io": {
            "color": {"type": "color"},
        },
        "data": {"src": "out"},
    },
    description="Draws a line on an image.",
)
@fn.controlled_wrapper(cv2.line, wrapper_attribute="__fnwrapped__")
def line(
    img: ImageFormat,
    start_x: Union[float, List[float], int, List[int]],
    start_y: Union[float, List[float], int, List[int]],
    end_x: Union[float, List[float], int, List[int]],
    end_y: Union[float, List[float], int, List[int]],
    color: Optional[str] = "00FF00",
    thickness: int = 1,
    lineType: LineTypes = LineTypes.LINE_8,
    shift: int = 0,
) -> OpenCVImageFormat:
    if isinstance(start_x, (float, int)):
        start_x = [start_x]
    if isinstance(start_y, (float, int)):
        start_y = [start_y]
    if isinstance(end_x, (float, int)):
        end_x = [end_x]
    if isinstance(end_y, (float, int)):
        end_y = [end_y]
    assert len(start_x) == len(start_y) == len(end_x) == len(end_y), (
        "start_x, start_y, end_x, and end_y lists must have the same length"
    )
    color = rgb_from_hexstring(color)
    color = color[::-1]
    lineType = LineTypes.v(lineType)
    img = assert_opencvdata(img, 3)
    for i in range(len(start_x)):
        start = (int(start_x[i]), int(start_y[i]))
        end = (int(end_x[i]), int(end_y[i]))
        img = cv2.line(
            img=img,
            pt1=start,
            pt2=end,
            color=color,
            thickness=thickness,
            lineType=lineType,
            shift=int(shift),
        )
    return OpenCVImageFormat(img)


@fn.NodeDecorator(
    node_id="cv2.rectangle",
    name="rectangle",
    default_render_options={
        "io": {
            "color": {"type": "color"},
        },
        "data": {"src": "out"},
    },
    description="Draws a rectangle on an image.",
)
@fn.controlled_wrapper(cv2.rectangle, wrapper_attribute="__fnwrapped__")
def rectangle(
    img: ImageFormat,
    x: Union[float, List[float], int, List[int]],
    y: Union[float, List[float], int, List[int]],
    width: Union[float, List[float], int, List[int]],
    height: Union[float, List[float], int, List[int]],
    color: Optional[str] = "00FF00",
    thickness: int = 1,
    lineType: LineTypes = LineTypes.LINE_8,
    shift: int = 0,
) -> OpenCVImageFormat:
    if isinstance(x, (float, int)):
        x = [x]
    if isinstance(y, (float, int)):
        y = [y]
    if isinstance(width, (float, int)):
        width = [width]
    if isinstance(height, (float, int)):
        height = [height]
    assert len(x) == len(y) == len(width) == len(height), (
        "x, y, width, and height lists must have the same length"
    )
    color = rgb_from_hexstring(color)
    color = color[::-1]
    lineType = LineTypes.v(lineType)
    img = assert_opencvdata(img, 3)
    for i in range(len(x)):
        start = (int(x[i]), int(y[i]))
        end = (int(x[i] + width[i]), int(y[i] + height[i]))
        img = cv2.rectangle(
            img=img,
            pt1=start,
            pt2=end,
            color=color,
            thickness=thickness,
            lineType=lineType,
            shift=int(shift),
        )
    return OpenCVImageFormat(img)


@fn.NodeDecorator(
    node_id="cv2.polylines",
    name="polylines",
    default_render_options={
        "io": {
            "color": {"type": "color"},
        },
        "data": {"src": "out"},
    },
    description="Draws a polyline on an image.",
)
@fn.controlled_wrapper(cv2.polylines, wrapper_attribute="__fnwrapped__")
def polylines(
    img: ImageFormat,
    pts: List[np.ndarray],
    isClosed: bool = True,
    color: Optional[str] = "00FF00",
    thickness: int = 1,
    lineType: LineTypes = LineTypes.LINE_8,
    shift: int = 0,
) -> OpenCVImageFormat:
    color = rgb_from_hexstring(color)
    color = color[::-1]
    lineType = LineTypes.v(lineType)

    if isinstance(pts, np.ndarray):
        if pts.ndim == 2:
            pts = [pts]

    img = cv2.polylines(
        img=assert_opencvdata(img, 3),
        pts=pts,
        isClosed=isClosed,
        color=color,
        thickness=thickness,
        lineType=lineType,
        shift=int(shift),
    )
    return OpenCVImageFormat(img)


@fn.NodeDecorator(
    node_id="cv2.fillPoly",
    name="fillPoly",
    default_render_options={
        "io": {
            "color": {"type": "color"},
        },
        "data": {"src": "out"},
    },
    description="Fills a polygon on an image.",
)
@fn.controlled_wrapper(cv2.fillPoly, wrapper_attribute="__fnwrapped__")
def fillPoly(
    img: ImageFormat,
    pts: List[np.ndarray],
    color: Optional[str] = "00FF00",
    lineType: LineTypes = LineTypes.LINE_8,
    shift: int = 0,
) -> OpenCVImageFormat:
    color = rgb_from_hexstring(color)
    color = color[::-1]
    lineType = LineTypes.v(lineType)

    if isinstance(pts, np.ndarray):
        if pts.ndim == 2:
            pts = [pts]

    img = cv2.fillPoly(
        img=assert_opencvdata(img, 3),
        pts=pts,
        color=color,
        lineType=lineType,
        shift=int(shift),
    )
    return OpenCVImageFormat(img)


class FontTypes(fn.DataEnum):
    """
    Enum for font types.

    """

    FONT_HERSHEY_SIMPLEX = cv2.FONT_HERSHEY_SIMPLEX
    FONT_HERSHEY_PLAIN = cv2.FONT_HERSHEY_PLAIN
    FONT_HERSHEY_DUPLEX = cv2.FONT_HERSHEY_DUPLEX
    FONT_HERSHEY_COMPLEX = cv2.FONT_HERSHEY_COMPLEX
    FONT_HERSHEY_TRIPLEX = cv2.FONT_HERSHEY_TRIPLEX
    FONT_HERSHEY_COMPLEX_SMALL = cv2.FONT_HERSHEY_COMPLEX_SMALL
    FONT_HERSHEY_SCRIPT_SIMPLEX = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
    FONT_HERSHEY_SCRIPT_COMPLEX = cv2.FONT_HERSHEY_SCRIPT_COMPLEX


@fn.NodeDecorator(
    node_id="cv2.putText",
    name="putText",
    default_render_options={
        "io": {
            "color": {"type": "color"},
        },
        "data": {"src": "out"},
    },
    description="Draws text on an image.",
)
@fn.controlled_wrapper(cv2.putText, wrapper_attribute="__fnwrapped__")
def putText(
    img: ImageFormat,
    text: str,
    org_x: Union[float, List[float], int, List[int]],
    org_y: Union[float, List[float], int, List[int]],
    fontFace: FontTypes = FontTypes.FONT_HERSHEY_SIMPLEX,
    fontScale: float = 1,
    color: Optional[str] = "00FF00",
    thickness: int = 1,
    lineType: LineTypes = LineTypes.LINE_8,
    bottomLeftOrigin: bool = False,
) -> OpenCVImageFormat:
    if isinstance(org_x, (float, int)):
        org_x = [org_x]
    if isinstance(org_y, (float, int)):
        org_y = [org_y]
    assert len(org_x) == len(org_y), "org_x and org_y lists must have the same length"
    color = rgb_from_hexstring(color)
    color = color[::-1]
    lineType = LineTypes.v(lineType)
    img = assert_opencvdata(img, 3)
    for i in range(len(org_x)):
        org = (int(org_x[i]), int(org_y[i]))
        img = cv2.putText(
            img=img,
            text=text,
            org=org,
            fontFace=FontTypes.v(fontFace),
            fontScale=fontScale,
            color=color,
            thickness=thickness,
            lineType=lineType,
            bottomLeftOrigin=bottomLeftOrigin,
        )
    return OpenCVImageFormat(img)


@fn.NodeDecorator(
    node_id="cv2.arrowedLine",
    name="arrowedLine",
    default_render_options={
        "io": {
            "color": {"type": "color"},
        },
        "data": {"src": "out"},
    },
    description="Draws an arrowed line on an image.",
)
@fn.controlled_wrapper(cv2.arrowedLine, wrapper_attribute="__fnwrapped__")
def arrowedLine(
    img: ImageFormat,
    start_x: Union[float, List[float], int, List[int]],
    start_y: Union[float, List[float], int, List[int]],
    end_x: Union[float, List[float], int, List[int]],
    end_y: Union[float, List[float], int, List[int]],
    color: Optional[str] = "00FF00",
    thickness: int = 1,
    lineType: LineTypes = LineTypes.LINE_8,
    shift: int = 0,
    tipLength: float = 0.1,
) -> OpenCVImageFormat:
    if isinstance(start_x, (float, int)):
        start_x = [start_x]
    if isinstance(start_y, (float, int)):
        start_y = [start_y]
    if isinstance(end_x, (float, int)):
        end_x = [end_x]
    if isinstance(end_y, (float, int)):
        end_y = [end_y]
    assert len(start_x) == len(start_y) == len(end_x) == len(end_y), (
        "start_x, start_y, end_x, and end_y lists must have the same length"
    )
    color = rgb_from_hexstring(color)
    color = color[::-1]
    lineType = LineTypes.v(lineType)
    img = assert_opencvdata(img, 3)
    for i in range(len(start_x)):
        start = (int(start_x[i]), int(start_y[i]))
        end = (int(end_x[i]), int(end_y[i]))
        img = cv2.arrowedLine(
            img=img,
            pt1=start,
            pt2=end,
            color=color,
            thickness=thickness,
            line_type=lineType,
            shift=int(shift),
            tipLength=tipLength,
        )
    return OpenCVImageFormat(img)


@fn.NodeDecorator(
    node_id="cv2.fillConvexPoly",
    name="fillConvexPoly",
    default_render_options={
        "io": {
            "color": {"type": "color"},
        },
        "data": {"src": "out"},
    },
    description="Fills a convex polygon on an image.",
)
@fn.controlled_wrapper(cv2.fillConvexPoly, wrapper_attribute="__fnwrapped__")
def fillConvexPoly(
    img: ImageFormat,
    pts: List[np.ndarray],
    color: Optional[str] = "00FF00",
    lineType: LineTypes = LineTypes.LINE_8,
    shift: int = 0,
) -> OpenCVImageFormat:
    color = rgb_from_hexstring(color)
    color = color[::-1]
    lineType = LineTypes.v(lineType)

    img = cv2.fillConvexPoly(
        img=assert_opencvdata(img, 3),
        points=pts,
        color=color,
        lineType=lineType,
        shift=int(shift),
    )
    return OpenCVImageFormat(img)


class MarkerTypes(fn.DataEnum):
    """
    Enum for marker types.

    """

    CROSS = cv2.MARKER_CROSS
    TILTED_CROSS = cv2.MARKER_TILTED_CROSS
    STAR = cv2.MARKER_STAR
    DIAMOND = cv2.MARKER_DIAMOND
    SQUARE = cv2.MARKER_SQUARE
    TRIANGLE_UP = cv2.MARKER_TRIANGLE_UP
    TRIANGLE_DOWN = cv2.MARKER_TRIANGLE_DOWN


@fn.NodeDecorator(
    "cv2.drawMarker",
    name="drawMarker",
    default_render_options={
        "io": {
            "color": {"type": "color"},
        },
        "data": {"src": "out"},
    },
    description="Draws a marker on an image.",
)
@fn.controlled_wrapper(cv2.drawMarker, wrapper_attribute="__fnwrapped__")
def drawMarker(
    img: ImageFormat,
    pos_x: Union[float, List[float], int, List[int]],
    pos_y: Union[float, List[float], int, List[int]],
    color: Optional[str] = "00FF00",
    markerType: MarkerTypes = MarkerTypes.CROSS,
    markerSize: int = 20,
    thickness: int = 1,
    lineType: LineTypes = LineTypes.LINE_8,
) -> OpenCVImageFormat:
    color = rgb_from_hexstring(color)
    color = color[::-1]
    lineType = LineTypes.v(lineType)
    markerType = MarkerTypes.v(markerType)

    if isinstance(pos_x, (float, int)):
        pos_x = [pos_x]
    if isinstance(pos_y, (float, int)):
        pos_y = [pos_y]
    assert len(pos_x) == len(pos_y), "pos_x and pos_y lists must have the same length"

    img = assert_opencvdata(img, 3)
    for i in range(len(pos_x)):
        position = (int(pos_x[i]), int(pos_y[i]))
        img = cv2.drawMarker(
            img=img,
            position=position,
            color=color,
            markerType=markerType,
            markerSize=int(markerSize),
            thickness=thickness,
            line_type=lineType,
        )
    return OpenCVImageFormat(img)


@fn.NodeDecorator(
    "cv2.drawContours",
    name="drawContours",
    default_render_options={
        "io": {
            "color": {"type": "color"},
        },
        "data": {"src": "out"},
    },
)
@fn.controlled_wrapper(cv2.drawContours, wrapper_attribute="__fnwrapped__")
def drawContours(
    img: ImageFormat,
    contours: np.ndarray,
    contourIdx: int = -1,
    color: Optional[str] = "00FF00",
    thickness: int = 1,
    lineType: LineTypes = LineTypes.LINE_8,
    offset_dx: int = 0,
    offset_dy: int = 0,
) -> OpenCVImageFormat:
    color = rgb_from_hexstring(color)

    color = color[::-1]

    offset = (offset_dx, offset_dy)
    lineType = LineTypes.v(lineType)

    return OpenCVImageFormat(
        cv2.drawContours(
            image=assert_opencvdata(img, 3),
            contours=contours,
            contourIdx=contourIdx,
            color=color,
            thickness=thickness,
            lineType=lineType,
            offset=offset,
        )
    )


class ColorMap(fn.DataEnum):
    """
    Enum for color maps.

    """

    AUTUMN = cv2.COLORMAP_AUTUMN
    BONE = cv2.COLORMAP_BONE
    JET = cv2.COLORMAP_JET
    WINTER = cv2.COLORMAP_WINTER
    RAINBOW = cv2.COLORMAP_RAINBOW
    OCEAN = cv2.COLORMAP_OCEAN
    SUMMER = cv2.COLORMAP_SUMMER
    SPRING = cv2.COLORMAP_SPRING
    COOL = cv2.COLORMAP_COOL
    HSV = cv2.COLORMAP_HSV
    PINK = cv2.COLORMAP_PINK
    HOT = cv2.COLORMAP_HOT
    PARULA = cv2.COLORMAP_PARULA
    MAGMA = cv2.COLORMAP_MAGMA
    INFERNO = cv2.COLORMAP_INFERNO
    PLASMA = cv2.COLORMAP_PLASMA
    VIRIDIS = cv2.COLORMAP_VIRIDIS
    CIVIDIS = cv2.COLORMAP_CIVIDIS
    TWILIGHT = cv2.COLORMAP_TWILIGHT
    TWILIGHT_SHIFTED = cv2.COLORMAP_TWILIGHT_SHIFTED
    TURBO = cv2.COLORMAP_TURBO
    DEEPGREEN = cv2.COLORMAP_DEEPGREEN


@fn.NodeDecorator(
    node_id="cv2.labels_to_color",
    default_render_options={"data": {"src": "out"}},
)
def labels_to_color(
    labels: np.ndarray, colormap: ColorMap = ColorMap.JET, mix: bool = True
) -> OpenCVImageFormat:
    """
    Takes an 2d array of labels and converts it to a color image.
    Apply a colormap to the labels.

    Args:
        labels: 2d array of labels.
        colormap: Colormap to use.
        mix: bool, if True, mix the numerical values of the labels to prevent a spread of colors.
    """

    if labels.ndim != 2:
        raise ValueError("labels must be a 2D array")
    unique_labels = np.unique(labels)
    if mix:
        unique_labels = np.random.permutation(unique_labels)
    n_colors = min(len(unique_labels), 256)
    colors = cv2.applyColorMap(
        np.linspace(0, 255, n_colors).reshape(n_colors, 1).astype(np.uint8),
        ColorMap.v(colormap),
    )

    img = np.zeros(labels.shape + (3,)) * np.nan
    for i, label in enumerate(unique_labels):
        img[labels == label] = colors[i % n_colors]

    return OpenCVImageFormat(img.astype(np.uint8))


NODE_SHELF = fn.Shelf(
    nodes=[
        circle,
        ellipse,
        line,
        rectangle,
        polylines,
        fillPoly,
        putText,
        arrowedLine,
        drawContours,
        labels_to_color,
    ],
    subshelves=[],
    name="Drawing",
    description="Nodes for drawing shapes and text on images.",
)
