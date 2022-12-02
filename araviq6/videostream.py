"""
Video frame pipeline
====================

:mod:`araviq6.videostream` provides video pipeline classes to handle
``QVideoFrame`` using numpy array processing.

There are two options to process a video frame.

1. :class:`VideoFrameProcessor` (QVideoFrame -> ndarray -> QVideoFrame)
2. :class:`FrameToArrayConverter` (QVideoFrame -> ndarray)

Convenience multimedia classes for the second option are also provided in this
module.

1. :class:`NDArrayVideoPlayer` (video file -> ndarray)
2. :class:`NDArrayMediaCaptureSession` (camera -> ndarray)

Pipeline classes
----------------

.. autoclass:: VideoFrameProcessor
   :members:
   :exclude-members: videoFrameProcessed

.. autoclass:: VideoProcessWorker
   :members:
   :exclude-members: videoFrameProcessed

.. autoclass:: FrameToArrayConverter
   :members:
   :exclude-members: arrayConverted

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
from typing import Optional


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
    """
    Worker to process ``QVideoFrame`` using :class:`numpy.ndarray` operation.

    :class:`VideoProcessWorker` converts ``QVideoFrame`` to numpy array, performs
    array processing and constructs a new ``QVideoFrame`` with the new array.
    Pass the input ``QVideoFrame`` to :meth:`processVideoFrame` slot and listen
    to :attr:`videoFrameProcessed` signal.

    Video frame is first converted to ``QImage``, and then to numpy array by
    :meth:`imageToArray`. Array processing is defined in :meth:`processArray`.
    """

    videoFrameProcessed = QtCore.Signal(QtMultimedia.QVideoFrame)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ready = True

    def ready(self) -> bool:
        """
        Returns true if the worker finished processing and can process the next
        video frame without being blocked.
        """
        return self._ready

    def processVideoFrame(self, frame: QtMultimedia.QVideoFrame):
        """
        Process *frame* and emit the result to :attr:`videoFrameProcessed`.

        Video frame is converted to ``QImage``, which is then converted to numpy
        array by :meth:`imageToArray`. The array is then processed by
        :meth:`processArray`, and new video frame is constructed from it.

        Note
        ====

        This method must *not* be Qt Slot to be multithreaded.
        """
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
        """
        Convert *image* to numpy array.

        *image* is ``QImage`` from ``QVidoeFrame``. By default this method
        uses ``qimage2ndarray.rgb_view`` for conversion. Subclass can redefine
        this method.
        """
        return qimage2ndarray.rgb_view(image, byteorder=None)

    def processArray(self, array: np.ndarray) -> np.ndarray:
        """
        Perform image processing on *array* and return the result.

        By default this method does not perform any processing. Subclass can
        redefine this method.
        """
        return array


class VideoFrameProcessor(QtCore.QObject):
    """
    Video pipeline component to process ``QVideoFrame``

    :class:`VideoFrameProcessor` runs :class:`VideoProcessWorker` in internal
    thread to process the incoming video frame. Pass the input ``QVideoFrame``
    to :meth:`processVideoFrame` slot and listen to :attr:`videoFrameProcessed`
    signal.

    """

    _processRequested = QtCore.Signal(QtMultimedia.QVideoFrame)
    videoFrameProcessed = QtCore.Signal(QtMultimedia.QVideoFrame)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None

        self._processorThread = QtCore.QThread()
        self._processorThread.start()

    def worker(self) -> Optional[VideoProcessWorker]:
        """
        Worker to process the video frame. If ``None``, frame is not processed.

        See also :meth:`setWorker`.
        """
        return self._worker

    def setWorker(self, worker: Optional[VideoProcessWorker]):
        """
        Set *worker* as video frame processor.

        See also :meth:`worker`.
        """
        oldWorker = self.worker()
        if oldWorker is not None:
            self._processRequested.disconnect(oldWorker.processVideoFrame)
            oldWorker.videoFrameProcessed.disconnect(self.videoFrameProcessed)
        self._worker = worker
        if worker is not None:
            self._processRequested.connect(worker.processVideoFrame)
            worker.videoFrameProcessed.connect(self.videoFrameProcessed)
            worker.moveToThread(self._processorThread)

    @QtCore.Slot(QtMultimedia.QVideoFrame)
    def processVideoFrame(self, frame: QtMultimedia.QVideoFrame):
        """
        Process *frame* and emit the result to :attr:`videoFrameProcessed`.

        """
        worker = self.worker()
        if worker is None:
            self.videoFrameProcessed.emit(frame)
        elif worker.ready():
            self._processRequested.emit(frame)
        else:
            return

    def stop(self):
        """Stop the worker thread."""
        self._processorThread.quit()
        self._processorThread.wait()


class FrameToArrayConverter(QtCore.QObject):
    """
    Video pipeline component which converts ``QVideoFrame`` to numpy array and
    emits to :attr:`arrayConverted`.

    ``QVideoFrame`` is first transformed to ``QImage`` and then converted to
    array by :meth:`converter`.

    ``QVideoPlayer`` sends empty video frame at the end of video.
    :meth:`ignoreNullFrame` determines whether null frame should be ignored or
    empty array should be emitted.

    """

    arrayConverted = QtCore.Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ignoreNullFrame = True
        self._converter = qimage2ndarray.rgb_view

    def ignoreNullFrame(self) -> bool:
        """
        If True, null ``QVideoFrame`` passed to :meth:`convertVideoFrame` is be
        ignored. Else, empty array with shape ``(0, 0, 0)`` is emitted.
        """
        return self._ignoreNullFrame

    @QtCore.Slot(bool)
    def setIgnoreNullFrame(self, ignore: bool):
        """Update :meth:`ignoreNullFrame`."""
        self._ignoreNullFrame = ignore

    @QtCore.Slot(QtMultimedia.QVideoFrame)
    def convertVideoFrame(self, frame: QtMultimedia.QVideoFrame):
        """
        Convert ``QVideoFrame`` to :class:`numpy.ndarray` and emit to
        :meth:`setArray`.
        """
        qimg = frame.toImage()
        if not qimg.isNull():
            array = self.imageToArray(qimg).copy()  # copy to detach reference
        elif not self.ignoreNullFrame():
            array = np.empty((0, 0, 0), dtype=np.uint8)
        else:
            return
        self.arrayConverted.emit(array)

    def imageToArray(self, image: QtGui.QImage) -> np.ndarray:
        """
        Convert *image* to numpy array.

        *image* is ``QImage`` from ``QVidoeFrame``. By default this method
        uses ``qimage2ndarray.rgb_view`` for conversion. Subclass can redefine
        this method.
        """
        return qimage2ndarray.rgb_view(image, byteorder=None)


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
        self._arrayConverter = FrameToArrayConverter(self)

        self.setVideoSink(self._videoSink)
        self._videoSink.videoFrameChanged.connect(
            self._arrayConverter.convertVideoFrame
        )
        self._arrayConverter.arrayConverted.connect(self.arrayChanged)


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
        self._arrayConverter = FrameToArrayConverter(self)

        self.setVideoSink(self._videoSink)
        self._videoSink.videoFrameChanged.connect(
            self._arrayConverter.convertVideoFrame
        )
        self._arrayConverter.arrayConverted.connect(self.arrayChanged)
