"""
Video frame pipeline
====================

:mod:`araviq6.videostream` provides video pipeline classes to handle
``QVideoFrame`` using numpy array processing.

There are two options to handle the pipeline.

1. Frame-based approach
2. Array-based approach

The first approach can be achieved by connecting :class:`VideoFrameProcessor`
with ``QVideoSink``. The second is more low-level, and consists of
:class:`FrameToArrayConverter`, :class:`ArrayProcessor` and
:class:`ArrayToFrameConverter`

Convenience multimedia classes for array-based pipeline are also provided in this
module. These classes can replace the :class:`FrameToArrayConverter` connected
to ``QVideoSink``.

1. :class:`NDArrayVideoPlayer` (video file -> ndarray)
2. :class:`NDArrayMediaCaptureSession` (camera -> ndarray)

Pipeline classes
----------------

.. autoclass:: VideoFrameProcessor
   :members:
   :exclude-members: arrayProcessed, videoFrameProcessed

.. autoclass:: VideoFrameWorker
   :members:
   :exclude-members: arrayProcessed, videoFrameProcessed

.. autoclass:: FrameToArrayConverter
   :members:
   :exclude-members: arrayConverted

.. autoclass:: ArrayToFrameConverter
   :members:
   :exclude-members: frameConverted

.. autoclass:: ArrayProcessor
   :members:
   :exclude-members: arrayProcessed

.. autoclass:: ArrayWorker
   :members:
   :exclude-members: arrayProcessed

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
    "VideoFrameWorker",
    "VideoFrameProcessor",
    "FrameToArrayConverter",
    "ArrayToFrameConverter",
    "ArrayWorker",
    "ArrayProcessor",
    "NDArrayVideoPlayer",
    "NDArrayMediaCaptureSession",
]


# Monkeypatch qimage2ndarray until new version (> 1.9.0)
# https://github.com/hmeine/qimage2ndarray/issues/29
for name, qimage_format in qimage2ndarray.qimageview_python.FORMATS.items():
    if name in dir(QtGui.QImage.Format):
        qimage_format.code = getattr(QtGui.QImage, name)


class VideoFrameWorker(QtCore.QObject):
    """
    Worker to process ``QVideoFrame`` using :class:`numpy.ndarray` operation.

    To perform processing, pass the input frame to :meth:`runProcess` and listen
    to :attr:`arrayProcessed` or :attr:`videoFrameProcessed` signals.

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

    def runProcess(self, frame: QtMultimedia.QVideoFrame):
        """
        Process *frame* and emit the result to :attr:`arrayProcessed` and
        :attr:`videoFrameProcessed`.

        When a video frame is passed, it is first converted to ``QImage`` by
        ``QVideoFrame.toImage()`` and then to array by :meth:`imageToArray`.
        Array processing is done by :meth:`processArray`, and the result is
        converted back to ``QVideoFrame`` by :meth:`arrayToVideoFrame`.

        During the processing :meth:`ready` is set to False.

        Notes
        =====

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

    :class:`VideoFrameProcessor` runs :class:`VideoFrameWorker` in internal
    thread to process the incoming video frame. Pass the input ``QVideoFrame``
    to :meth:`processVideoFrame` slot and listen to :attr:`arrayProcessed` and
    :attr:`videoFrameProcessed` signal.

    """

    _processRequested = QtCore.Signal(QtMultimedia.QVideoFrame)
    arrayProcessed = QtCore.Signal(np.ndarray)
    videoFrameProcessed = QtCore.Signal(QtMultimedia.QVideoFrame)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._queueToWorker = False

        self._processorThread = QtCore.QThread()
        self._processorThread.start()

    def worker(self) -> Optional[VideoFrameWorker]:
        """
        Worker to process the video frame.

        See also :meth:`setWorker`.
        """
        return self._worker

    def setWorker(self, worker: Optional[VideoFrameWorker]):
        """
        Set *worker* as video frame processor.

        See also :meth:`worker`.
        """
        oldWorker = self.worker()
        if oldWorker is not None:
            self._processRequested.disconnect(oldWorker.runProcess)
            oldWorker.arrayProcessed.disconnect(self.arrayProcessed)
            oldWorker.videoFrameProcessed.disconnect(self.videoFrameProcessed)
        self._worker = worker
        if worker is not None:
            self._processRequested.connect(worker.runProcess)
            worker.arrayProcessed.connect(self.arrayProcessed)
            worker.videoFrameProcessed.connect(self.videoFrameProcessed)
            worker.moveToThread(self._processorThread)

    def queueToWorker(self) -> bool:
        """
        If False, incoming frames to :meth:`processVideoFrame` are aborted if
        :meth:`worker` is not ready.

        If True, incoming frames are queued if worker is not ready. This may
        consume a significant amount of memory and should be used with
        discretion.

        See also :meth:`setQueueToWorker`.
        """
        return self._queueToWorker

    def setQueueToWorker(self, flag: bool):
        """Set :meth:`queueToWorker` to *flag*."""
        self._queueToWorker = flag

    @QtCore.Slot(QtMultimedia.QVideoFrame)
    def processVideoFrame(self, frame: QtMultimedia.QVideoFrame):
        """
        Request :meth:`worker` to process *frame*.
        The result is emitted to :attr:`arrayProcessed` and
        :attr:`videoFrameProcessed`.

        If worker is not ready but :meth:`queueToWorker` is True, *frame* is
        put into the process queue.

        """
        worker = self.worker()
        if worker is not None:
            if worker.ready() or self.queueToWorker():
                self._processRequested.emit(frame)
        else:
            self.videoFrameProcessed.emit(frame)

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


class ArrayWorker(QtCore.QObject):
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

        Notes
        =====

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


class ArrayProcessor(QtCore.QObject):
    """
    Video pipeline component to process numpy array.

    :class:`ArrayProcessor` runs :class:`ArrayWorker` in internal thread
    to process the incoming array. Pass the input array to :meth:`processArray`
    slot and listen to :attr:`arrayProcessed` signal.

    """

    _processRequested = QtCore.Signal(np.ndarray)
    arrayProcessed = QtCore.Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._queueToWorker = False

        self._processorThread = QtCore.QThread()
        self._processorThread.start()

    def worker(self) -> Optional[ArrayWorker]:
        """
        Worker to process the array.

        See also :meth:`setWorker`.
        """
        return self._worker

    def setWorker(self, worker: Optional[ArrayWorker]):
        """
        Set *worker* as array processor.

        See also :meth:`worker`.
        """
        oldWorker = self.worker()
        if oldWorker is not None:
            self._processRequested.disconnect(oldWorker.runProcess)
            oldWorker.arrayProcessed.disconnect(self.arrayProcessed)
        self._worker = worker
        if worker is not None:
            self._processRequested.connect(worker.runProcess)
            worker.arrayProcessed.connect(self.arrayProcessed)
            worker.moveToThread(self._processorThread)

    def queueToWorker(self) -> bool:
        """
        If False, incoming arrays to :meth:`processArray` are aborted if
        :meth:`worker` is not ready.

        If True, incoming arrays are queued if worker is not ready. This may
        consume a significant amount of memory and should be used with
        discretion.

        See also :meth:`setQueueToWorker`.
        """
        return self._queueToWorker

    def setQueueToWorker(self, flag: bool):
        """Set :meth:`queueToWorker` to *flag*."""
        self._queueToWorker = flag

    @QtCore.Slot(np.ndarray)
    def processArray(self, array: npt.NDArray[np.uint8]):
        """
        Request :meth:`worker` to process *array*.
        The result is emitted to :attr:`arrayProcessed`.

        If worker is not ready but :meth:`queueToWorker` is True, *array* is
        put into the process queue.

        """
        worker = self.worker()
        if worker is not None:
            if worker.ready() or self.queueToWorker():
                self._processRequested.emit(array)
        else:
            self.arrayProcessed.emit(array)

    def stop(self):
        """Stop the worker thread."""
        self._processorThread.quit()
        self._processorThread.wait()


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
