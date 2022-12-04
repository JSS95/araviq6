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

.. autoclass:: ArrayToFrameConverter
   :members:
   :exclude-members: frameConverted

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
import numpy.typing as npt
import qimage2ndarray  # type: ignore[import]
from araviq6.array2qvideoframe import array2qvideoframe
from araviq6.qt_compat import QtCore, QtGui, QtMultimedia
from typing import Optional


__all__ = [
    "VideoProcessWorker",
    "VideoFrameProcessor",
    "FrameToArrayConverter",
    "ArrayToFrameConverter",
    "ArrayProcessWorker",
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

    To perform processing, pass the input frame to :meth:`processVideoFrame` and
    listen to :attr:`arrayProcessed` or :attr:`videoFrameProcessed` signals.

    :meth:`ready` is set to ``False`` when the processing is being run. This
    property can be utilized in multithreading.
    """

    arrayProcessed = QtCore.Signal(np.ndarray)
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
        Process *frame* and emit the result to :attr:`arrayProcessed` and
        :attr:`videoFrameProcessed`.

        When a video frame is passed, it is first converted to ``QImage`` by
        ``QVideoFrame.toImage()`` and then to array by :meth:`imageToArray`.
        Array processing is done by :meth:`processArray`, and the result is
        converted back to ``QVideoFrame`` by :meth:`arrayToVideoFrame`.

        During the processing :meth:`ready` is set to False.

        Note
        ====

        This method must *not* be Qt Slot to be multithreaded.
        """
        self._ready = False

        qimg = frame.toImage()  # must assign to avoid crash
        array = self.imageToArray(qimg)
        processedArray = self.processArray(array)
        processedFrame = self.arrayToVideoFrame(processedArray, frame)

        self.arrayProcessed.emit(processedArray)
        self.videoFrameProcessed.emit(processedFrame)
        self._ready = True

    def imageToArray(self, image: QtGui.QImage) -> npt.NDArray[np.uint8]:
        """
        Convert *image* to numpy array.

        By default, this method uses ``qimage2ndarray.rgb_view`` for conversion.
        Null image is converted to 3D empty array. Subclass can redefine this
        method.
        """
        if image.isNull():
            ret = np.empty((0, 0, 0), dtype=np.uint8)
        else:
            ret = qimage2ndarray.rgb_view(image, byteorder=None)
        return ret

    def processArray(self, array: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
        """
        Perform image processing on *array* and return the result.

        By default this method does not perform any processing. Subclass can
        redefine this method.
        """
        return array

    def arrayToVideoFrame(
        self, array: npt.NDArray[np.uint8], hintFrame: QtMultimedia.QVideoFrame
    ) -> QtMultimedia.QVideoFrame:
        """
        Convert *array* to ``QVideoFrame``, using *hintFrame* as hint.

        By default this method uses :func:`array2qvideoframe` for conversion.
        Then, it updates ``mapMode()``, ``startTime()``, and ``endTime()``
        properties of the new frame with those of *hintFrame*. For empty array,
        *hintFrame* is just returned. Subclass can redefine this method.
        """
        if array.size == 0:
            ret = hintFrame
        else:
            ret = array2qvideoframe(array)
            ret.map(hintFrame.mapMode())
            ret.setStartTime(hintFrame.startTime())
            ret.setEndTime(hintFrame.endTime())
        return ret


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
    Video pipeline component which converts ``QVideoFrame`` to numpy array.

    When video frame is passed to :meth:`convertVideoFrame`,
    :class:`FrameToArrayConverter` first converts it to ``QImage`` and then
    to numpy array using :meth:`imageToArray`. Resulting array is emitted to
    :attr:`arrayConverted` with original frame.

    Invalid video frame is converted to 3D empty array.

    """

    arrayConverted = QtCore.Signal(np.ndarray, QtMultimedia.QVideoFrame)

    @QtCore.Slot(QtMultimedia.QVideoFrame)
    def convertVideoFrame(self, frame: QtMultimedia.QVideoFrame):
        """
        Convert *frame* to numpy array and emit to :attr:`arrayConverted`.

        Video frame is converted using using :meth:`imageToArray`. Result array
        and *frame* are emitted to :meth:`arrayConverted`.

        """
        qimg = frame.toImage()
        if not qimg.isNull():
            array = self.imageToArray(qimg).copy()  # copy to detach reference
        else:
            array = np.empty((0, 0, 0), dtype=np.uint8)
        self.arrayConverted.emit(array, frame)

    def imageToArray(self, image: QtGui.QImage) -> npt.NDArray[np.uint8]:
        """
        Convert *image* to numpy array.

        *image* is ``QImage`` from ``QVideoFrame``. By default this method
        uses ``qimage2ndarray.rgb_view`` for conversion. Subclass can redefine
        this method.
        """
        return qimage2ndarray.rgb_view(image, byteorder=None)


class ArrayToFrameConverter(QtCore.QObject):
    """
    Video pipeline component which converts numpy array to ``QVideoFrame``.

    When array (and optionally, its original video frame) is passed to
    :meth:`convertArray`, :class:`ArrayToFrameConverter` converts the array to
    the video frame using :meth:`arrayToFrame`. Resulting video frame is emitted
    to :attr:`frameConverted` with original frame.

    Empty array is converted to invalid video frame.

    """

    frameConverted = QtCore.Signal(QtMultimedia.QVideoFrame, QtMultimedia.QVideoFrame)

    @QtCore.Slot(np.ndarray, QtMultimedia.QVideoFrame)
    def convertArray(
        self,
        array: npt.NDArray[np.uint8],
        frame: Optional[QtMultimedia.QVideoFrame] = None,
    ):
        """
        Convert *array* to ``QvideoFrame`` and emit to :attr:`frameConverted`.

        Additional *frame* argument can be passed to set the properties (e.g.,
        starting time and ending time) of the converted frame. This is useful
        when *frame* is the original frame from the source and *array* is its
        image processing result.

        Array is converted using :meth:`arrayToFrame`. Result frame and original
        *frame* are emitted to :attr:`frameConverted`.
        """
        if frame is not None:
            if array.size != 0:
                newFrame = self.arrayToFrame(array)
            else:
                newFrameFormat = QtMultimedia.QVideoFrameFormat(
                    QtCore.QSize(-1, -1), frame.surfaceFormat().pixelFormat()
                )
                newFrame = QtMultimedia.QVideoFrame(newFrameFormat)
            newFrame.map(frame.mapMode())
            newFrame.setStartTime(frame.startTime())
            newFrame.setEndTime(frame.endTime())
        else:
            if array.size != 0:
                newFrame = self.arrayToFrame(array)
            else:
                newFrameFormat = QtMultimedia.QVideoFrameFormat(
                    QtCore.QSize(-1, -1),
                    QtMultimedia.QVideoFrameFormat.PixelFormat.Format_Invalid,
                )
                newFrame = QtMultimedia.QVideoFrame(newFrameFormat)
        self.frameConverted.emit(newFrame, frame)

    def arrayToFrame(self, array: npt.NDArray[np.uint8]) -> QtMultimedia.QVideoFrame:
        """
        Converts *array* to ``QVideoFrame``.

        By default this method uses :func:`array2qvideoframe` for conversion.
        Subclass can redefine this method.
        """
        return array2qvideoframe(array)


class ArrayProcessWorker(QtCore.QObject):
    """
    Worker to process image in numpy array.

    To perform processing, pass the input array to :meth:`runProcess` and
    listen to :attr:`arrayProcessed` signal.

    :meth:`ready` is set to ``False`` when the processing is being run. This
    property can be utilized in multithreading.
    """

    arrayProcessed = QtCore.Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ready = True

    def ready(self) -> bool:
        """
        Returns true if the worker finished processing and can process the next
        array without being blocked.
        """
        return self._ready

    def runProcess(self, array: npt.NDArray[np.uint8]):
        """
        Process *array* and emit the result to :attr:`arrayProcessed`.

        Array processing is done by :meth:`processArray`.

        During the processing :meth:`ready` is set to False.

        Note
        ====

        This method must *not* be Qt Slot to be multithreaded.
        """
        self._ready = False
        self.arrayProcessed.emit(self.processArray(array))
        self._ready = True

    def processArray(self, array: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
        """
        Perform image processing on *array* and return the result.

        By default this method does not perform any processing. Subclass can
        redefine this method.

        See also :meth:`runProcess`.
        """
        return array


class NDArrayVideoPlayer(QtMultimedia.QMediaPlayer):
    """
    Video player which emits numpy array.

    :class:`NDArrayVideoPlayer` emits the the numpy array and its original frame
    to :attr:`arrayChanged` signal. User may use this class for convenience, or
    define own pipeline.
    """

    arrayChanged = QtCore.Signal(np.ndarray, QtMultimedia.QVideoFrame)

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
    Capture session which emits numpy array.

    :class:`NDArrayMediaCaptureSession` emits the the numpy array and its
    original frame to :attr:`arrayChanged` signal. User may use this class for
    convenience, or define own pipeline.
    """

    arrayChanged = QtCore.Signal(np.ndarray, QtMultimedia.QVideoFrame)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._videoSink = QtMultimedia.QVideoSink()
        self._arrayConverter = FrameToArrayConverter(self)

        self.setVideoSink(self._videoSink)
        self._videoSink.videoFrameChanged.connect(
            self._arrayConverter.convertVideoFrame
        )
        self._arrayConverter.arrayConverted.connect(self.arrayChanged)
