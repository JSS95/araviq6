"""
AraViQ6: NDArray from QVideoFrame with Qt6
==========================================

AraViQ6 is a package to build video pipeline with :class:`numpy.ndarray` from
Qt6's ``QVideoFrame``.

"""

from .version import __version__  # noqa

from .labels import ScalableQLabel, NDArrayLabel
from .videostream import (
    qimage2qvideoframe,
    VideoProcessWorker,
    VideoFrameProcessor,
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
    "qimage2qvideoframe",
    "VideoProcessWorker",
    "VideoFrameProcessor",
    "FrameToArrayConverter",
    "NDArrayVideoPlayer",
    "NDArrayMediaCaptureSession",
    "NDArrayVideoPlayerWidget",
    "NDArrayCameraWidget",
    "ClickableSlider",
    "MediaController",
    "get_samples_path",
]
