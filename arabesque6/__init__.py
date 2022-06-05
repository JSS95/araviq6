"""
Arabesque6: NDArray - QVideoFrame Converter for Qt6
===================================================

Arabesque6 is a package to get :class:`numpy.ndarray` from ``QVideoFrame`` with
Qt6 Python bindings - :mod:`PyQt6` and :mod:`PySide6`.

"""

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
    "get_data_path",
]
