"""
AraViQ6: NDArray from QVideoFrame with Qt6
==========================================

AraViQ6 is a package to get :class:`numpy.ndarray` from ``QVideoFrame`` with
Qt6 Python bindings - :mod:`PyQt6` or :mod:`PySide6`.

"""

from .version import __version__  # noqa

from .labels import ScalableQLabel, NDArrayLabel
from .videostream import (
    FrameToArrayConverter,
    NDArrayVideoPlayer,
    NDArrayMediaCaptureSession,
)
from .videowidgets import (
    NDArrayVideoPlayerWidget,
    NDArrayCameraWidget,
)
from .util import (
    ClickableSlider,
    MediaController,
    get_samples_path,
)


__all__ = [
    "ScalableQLabel",
    "NDArrayLabel",
    "FrameToArrayConverter",
    "NDArrayVideoPlayer",
    "NDArrayMediaCaptureSession",
    "NDArrayVideoPlayerWidget",
    "NDArrayCameraWidget",
    "ClickableSlider",
    "MediaController",
    "get_samples_path",
]
