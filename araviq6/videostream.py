"""
Video frame pipeline
====================

:mod:`araviq6.videostream` provides pipeline component to convert video stream
into numpy array, and convenience classes with internal video pipelines.

Converter
---------

.. autoclass:: FrameToArrayConverter
   :members:
   :exclude-members: arrayChanged

Convenience classes
-------------------

.. autoclass:: NDArrayVideoPlayer
   :members:
   :exclude-members: arrayChanged

.. autoclass:: NDArrayMediaCaptureSession
   :members:
   :exclude-members: arrayChanged

"""

import numpy as np
import qimage2ndarray  # type: ignore[import]
from araviq6.qt_compat import QtCore, QtGui, QtMultimedia
from typing import Optional, Callable


__all__ = [
    "VideoProcessWorker",
    "VideoFrameProcessor",
    "FrameToArrayConverter",
    "NDArrayVideoPlayer",
    "NDArrayMediaCaptureSession",
]


# Monkeypatch qimage2ndarray until new version (> 1.9.0)
# https://github.com/hmeine/qimage2ndarray/issues/29
for name, qimage_format in qimage2ndarray.qimageview_python.FORMATS.items():
    if name in dir(QtGui.QImage.Format):
        qimage_format.code = getattr(QtGui.QImage, name)


class VideoProcessWorker(QtCore.QObject):

    videoFrameProcessed = QtCore.Signal(QtMultimedia.QVideoFrame)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ready = True

    def ready(self) -> bool:
        return self._ready

    @QtCore.Slot(QtMultimedia.QVideoFrame)
    def setVideoFrame(self, frame: QtMultimedia.QVideoFrame):
        self._ready = False

        qimg = frame.toImage()  # must assign to avoid crash
        if not qimg.isNull():
            array = self.imageToArray(qimg)
            newarray = self.processArray(array)
            newimg = qimage2ndarray.array2qimage(newarray)
            pixelFormat = QtMultimedia.QVideoFrameFormat.pixelFormatFromImageFormat(
                newimg.format()
            )
            frameFormat = QtMultimedia.QVideoFrameFormat(newimg.size(), pixelFormat)
            processedFrame = QtMultimedia.QVideoFrame(frameFormat)
            mapped = processedFrame.map(QtMultimedia.QVideoFrame.MapMode.WriteOnly)
            if mapped:
                processedFrame.bits(0)[:] = newimg.bits()  # type: ignore[index]
                processedFrame.unmap()

            # set *processedFrame* properties same to *frame*
            processedFrame.map(frame.mapMode())
            processedFrame.setStartTime(frame.startTime())
            processedFrame.setEndTime(frame.endTime())
        else:
            processedFrame = frame

        self.videoFrameProcessed.emit(processedFrame)
        self._ready = True

    def imageToArray(self, image: QtGui.QImage) -> np.ndarray:
        return qimage2ndarray.rgb_view(image, byteorder=None)

    def processArray(self, array: np.ndarray) -> np.ndarray:
        return array


class VideoFrameProcessor(QtCore.QObject):

    _processRequested = QtCore.Signal(QtMultimedia.QVideoFrame)
    videoFrameChanged = QtCore.Signal(QtMultimedia.QVideoFrame)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None

        self._processorThread = QtCore.QThread()
        self._processorThread.start()

    def worker(self) -> Optional[VideoProcessWorker]:
        return self._worker

    def setWorker(self, worker: Optional[VideoProcessWorker]):
        oldWorker = self.worker()
        if oldWorker is not None:
            self._processRequested.disconnect(oldWorker.setVideoFrame)
            oldWorker.videoFrameProcessed.disconnect(self.videoFrameChanged)
        self._worker = worker
        if worker is not None:
            self._processRequested.connect(worker.setVideoFrame)
            worker.videoFrameProcessed.connect(self.videoFrameChanged)
            worker.moveToThread(self._processorThread)

    @QtCore.Slot(QtMultimedia.QVideoFrame)
    def setVideoFrame(self, frame: QtMultimedia.QVideoFrame):
        worker = self.worker()
        if worker is None or not worker.ready():
            self.videoFrameChanged.emit(frame)
        else:
            self._processRequested.emit(frame)

    def stop(self):
        self._processorThread.quit()
        self._processorThread.wait()


class FrameToArrayConverter(QtCore.QObject):
    """
    Video pipeline component which converts ``QVideoFrame`` to numpy array and
    emits to :attr:`arrayChanged`.

    ``QVideoFrame`` is first transformed to ``QImage`` and then converted to
    array by :meth:`converter`.

    ``QVideoPlayer`` sends empty video frame at the end of video.
    :meth:`ignoreNullFrame` determines whether null frame should be ignored or
    empty array should be emitted.

    """

    arrayChanged = QtCore.Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ignoreNullFrame = True
        self._converter = qimage2ndarray.rgb_view

    def ignoreNullFrame(self) -> bool:
        """
        If True, null ``QVideoFrame`` passed to :meth:`setVideoFrame` is be
        ignored. Else, empty array with shape ``(0, 0, 0)`` is emitted.
        """
        return self._ignoreNullFrame

    @QtCore.Slot(bool)
    def setIgnoreNullFrame(self, ignore: bool):
        """Update :meth:`ignoreNullFrame`."""
        self._ignoreNullFrame = ignore

    @QtCore.Slot(QtMultimedia.QVideoFrame)
    def setVideoFrame(self, frame: QtMultimedia.QVideoFrame):
        """
        Convert ``QVideoFrame`` to :class:`numpy.ndarray` and emit to
        :meth:`setArray`.
        """
        qimg = frame.toImage()
        if qimg.isNull() and self.ignoreNullFrame():
            pass
        else:
            array = self.convertQImageToArray(qimg)
            self.arrayChanged.emit(array)

    def converter(self) -> Callable[[QtGui.QImage], np.ndarray]:
        """
        Callable object to convert ``QImage`` instance to numpy array. Default is
        ``qimage2ndarray.rgb_view``.
        """
        return self._converter

    def setConverter(self, func: Callable[[QtGui.QImage], np.ndarray]):
        self._converter = func

    def convertQImageToArray(self, qimg: QtGui.QImage) -> np.ndarray:
        """
        Convert *qimg* to numpy array. Null image is converted to empty array.
        """
        converter = self.converter()
        if not qimg.isNull():
            array = converter(qimg).copy()  # copy to detach reference
        else:
            array = np.empty((0, 0, 0))
        return array


class NDArrayVideoPlayer(QtMultimedia.QMediaPlayer):
    """
    Minimal implementation of video player which emits frames as numpy arrays to
    :attr:`arrayChanged` signal.

    User may use this class for convenience, or define own pipeline.
    """

    arrayChanged = QtCore.Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._videoSink = QtMultimedia.QVideoSink()
        self._frame2Arr = FrameToArrayConverter(self)

        self.setVideoSink(self._videoSink)
        self._videoSink.videoFrameChanged.connect(self._frame2Arr.setVideoFrame)
        self._frame2Arr.arrayChanged.connect(self.arrayChanged)


class NDArrayMediaCaptureSession(QtMultimedia.QMediaCaptureSession):
    """
    Minimal implementation of media capture session which emits frames as
    numpy arrays to :attr:`arrayChanged` signal.

    User may use this class for convenience, or define own pipeline.
    """

    arrayChanged = QtCore.Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._videoSink = QtMultimedia.QVideoSink()
        self._frame2Arr = FrameToArrayConverter(self)

        self.setVideoSink(self._videoSink)
        self._videoSink.videoFrameChanged.connect(self._frame2Arr.setVideoFrame)
        self._frame2Arr.arrayChanged.connect(self.arrayChanged)
