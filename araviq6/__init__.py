"""
AraViQ6: NDArray from QVideoFrame with Qt6
==========================================

AraViQ6 is a package to get :class:`numpy.ndarray` from ``QVideoFrame`` with
Qt6 Python bindings - :mod:`PyQt6` or :mod:`PySide6`.

"""

from .qt_compat import qt_api  # noqa
from .version import __version__  # noqa

from .labels import ScalableQLabel, NDArrayLabel
from .videostream import (
    FrameToArrayConverter,
    NDArrayVideoPlayer,
    NDArrayMediaCaptureSession,
)
from .videowidgets import (
    ClickableSlider,
    MediaController,
    NDArrayVideoPlayerWidget,
    NDArrayCameraWidget,
)
from .util import get_data_path


__all__ = [
    "ScalableQLabel",
    "NDArrayLabel",
    "FrameToArrayConverter",
    "NDArrayVideoPlayer",
    "NDArrayMediaCaptureSession",
    "ClickableSlider",
    "MediaController",
    "NDArrayVideoPlayerWidget",
    "NDArrayCameraWidget",
    "get_data_path",
]
