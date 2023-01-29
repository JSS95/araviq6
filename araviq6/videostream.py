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
   :exclude-members: videoFrameProcessed

.. autoclass:: VideoFrameWorker
   :members:
   :exclude-members: videoFrameProcessed

.. autoclass:: QVideoFrameProperty
   :members:

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

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias


__all__ = [
    "VideoFrameWorker",
    "VideoFrameProcessor",
    "QVideoFrameProperty",
    "FrameToArrayConverter",
    "ArrayToFrameConverter",
    "ArrayWorker",
    "ArrayProcessor",
    "NDArrayVideoPlayer",
    "NDArrayMediaCaptureSession",
]


QVideoFrame: TypeAlias = QtMultimedia.QVideoFrame
MapMode: TypeAlias = QtMultimedia.QVideoFrame.MapMode
RotationAngle: TypeAlias = QtMultimedia.QVideoFrame.RotationAngle
QVideoFrameFormat: TypeAlias = QtMultimedia.QVideoFrameFormat


class VideoFrameWorker(QtCore.QObject):
    """
    Worker to process ``QVideoFrame`` using :class:`numpy.ndarray` operation.

    To perform processing, pass the input frame to :meth:`runProcess` and listen
    to :attr:`videoFrameProcessed` signal which emits two objects; processed
    QVideoFrame and processed NDArray.

    :meth:`ready` is set to ``False`` when the processing is running. This
    property can be utilized in multithreading.
    """

    videoFrameProcessed = QtCore.Signal(QVideoFrame, np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ready = True

    def ready(self) -> bool:
        """
        Returns true if the worker finished processing and can process the next
        video frame without being blocked.
        """
        return self._ready

    def runProcess(self, frame: QVideoFrame):
        """
        Process *frame* and emit the results to :attr:`videoFrameProcessed`.

        When a video frame is passed, it is first converted to ``QImage`` by
        ``QVideoFrame.toImage()`` and then to array by :meth:`imageToArray`.
        Array processing is done by :meth:`processArray`, and the result is
        converted back to ``QVideoFrame`` by :meth:`arrayToVideoFrame`.

        Processed QVideoFrame and processed array are emitted by
        :attr:`videoFrameProcessed`.

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

        self.videoFrameProcessed.emit(processedFrame, processedArray)
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

        See also :meth:`runProcess`.
        """
        return array

    def arrayToVideoFrame(
        self, array: npt.NDArray[np.uint8], hintFrame: QVideoFrame
    ) -> QVideoFrame:
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
    Video pipeline component to process ``QVideoFrame``.

    .. figure:: ../_images/frame-processor.jpg
       :align: center

       QVideoFrame processing structure

    :class:`VideoFrameProcessor` runs :class:`VideoFrameWorker` in an internal
    thread to process the incoming video frame. To perform processing, pass the
    input frame to :meth:`processVideoFrame` slot and listen to
    :attr:`videoFrameProcessed` signal which emits two objects; processed
    QVideoFrame and processed NDArray.

    :meth:`skipIfRunning` defines whether the incoming video frames should be
    skipped when the worker is running.

    """

    _processRequested = QtCore.Signal(QVideoFrame)
    videoFrameProcessed = QtCore.Signal(QVideoFrame, np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._skipIfRunning = True

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
            oldWorker.videoFrameProcessed.disconnect(self.videoFrameProcessed)
            oldWorker.videoFrameProcessed.disconnect(self.videoFrameProcessed)
        self._worker = worker
        if worker is not None:
            self._processRequested.connect(worker.runProcess)
            worker.videoFrameProcessed.connect(self.videoFrameProcessed)
            worker.videoFrameProcessed.connect(self.videoFrameProcessed)
            worker.moveToThread(self._processorThread)

    def skipIfRunning(self) -> bool:
        """
        If True, incoming frames to :meth:`processVideoFrame` are skipped if
        :meth:`worker` is running.

        If False, every incoming frame is queued if worker is not ready. This may
        consume a significant amount of memory and cause laggy displaying, thus
        should be used with discretion.

        See also :meth:`setSkipIfRunning`.
        """
        return self._skipIfRunning

    def setSkipIfRunning(self, flag: bool):
        """
        Set :meth:`skipIfRunning` to *flag*.

        See also :meth:`skipIfRunning`.
        """
        self._skipIfRunning = flag

    @QtCore.Slot(QVideoFrame)
    def processVideoFrame(self, frame: QVideoFrame):
        """
        Request :meth:`worker` to process *frame*.

        Processed QVideoFrame and processed array are emitted by
        :attr:`videoFrameProcessed`.

        If worker is running and :meth:`skipIfRunning` is True, *frame* is
        skipped without being emitted. If :meth:`skipIfRunning` is False,
        incoming frames are queued when worker is running.

        """
        worker = self.worker()
        if worker is not None:
            if worker.ready() or not self.skipIfRunning():
                self._processRequested.emit(frame)
        else:
            self.videoFrameProcessed.emit(frame)

    def stop(self):
        """Stop the worker thread."""
        self._processorThread.quit()
        self._processorThread.wait()


class QVideoFrameProperty:
    """Wrapper for the properties of QVideoFrame."""

    __slots__ = (
        "mapMode",
        "startTime",
        "endTime",
        "mirrored",
        "rotationAngle",
        "subtitleText",
    )

    def __init__(
        self,
        mapMode: MapMode = MapMode.NotMapped,
        startTime: int = -1,
        endTime: int = -1,
        mirrored: bool = False,
        rotationAngle: RotationAngle = RotationAngle.Rotation0,
        subtitleText: str = "",
    ):
        self.mapMode = mapMode
        self.startTime = startTime
        self.endTime = endTime
        self.mirrored = mirrored
        self.rotationAngle = rotationAngle
        self.subtitleText = subtitleText

    @classmethod
    def fromVideoFrame(cls, frame: QVideoFrame):
        """Construct :class:`QVideoFrameProperty` instance from *frame*."""
        return cls(*[getattr(frame, attr)() for attr in cls.__slots__])

    def setToVideoFrame(self, frame: QVideoFrame):
        """Set the properties of *frame* to the values in *self*."""
        frame.map(self.mapMode)
        frame.setStartTime(self.startTime)
        frame.setEndTime(self.endTime)
        frame.setMirrored(self.mirrored)
        frame.setRotationAngle(self.rotationAngle)
        frame.setSubtitleText(self.subtitleText)


class FrameToArrayConverter(QtCore.QObject):
    """
    Video pipeline component which converts ``QVideoFrame`` to numpy array.

    .. figure:: ../_images/frame-array-converter.jpg
       :align: center

       FrameToArrayConverter structure

    When video frame is passed to :meth:`convertVideoFrame`,
    :class:`FrameToArrayConverter` first converts it to ``QImage`` and then
    to numpy array using :meth:`imageToArray`. :attr:`arrayConverted` emits
    resulting array and :class:`QVideoFrameProperty`.

    Invalid video frame is converted to 3D empty array.

    """

    arrayConverted = QtCore.Signal(np.ndarray, QVideoFrameProperty)

    @QtCore.Slot(QVideoFrame)
    def convertVideoFrame(self, frame: QVideoFrame):
        """
        Convert *frame* to numpy array and emit to :attr:`arrayConverted`.

        Video frame is converted using using :meth:`imageToArray`, and its
        properties are wrapped by :class:`QVideoFrameProperty`. Converted array
        frame property are emitted to :meth:`arrayConverted`.

        """
        qimg = frame.toImage()
        if not qimg.isNull():
            array = self.imageToArray(qimg).copy()  # copy to detach reference
        else:
            array = np.empty((0, 0, 0), dtype=np.uint8)
        self.arrayConverted.emit(array, QVideoFrameProperty.fromVideoFrame(frame))

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

    .. figure:: ../_images/array-frame-converter.jpg
       :align: center

       ArrayToFrameConverter structure

    Conversion is done by passing an array to :meth:`convertArray` slot and
    listening to :attr:`frameConverted` signal. Frame properties can be set by
    passing optional :class:`QVideoFrameProperty` with the array.

    """

    frameConverted = QtCore.Signal(QVideoFrame)

    @QtCore.Slot(np.ndarray, QVideoFrame)
    def convertArray(
        self,
        array: npt.NDArray[np.uint8],
        frameProperty: QVideoFrameProperty = QVideoFrameProperty(),
    ):
        """
        Convert *array* to ``QvideoFrame`` and emit to :attr:`frameConverted`.

        Valid array is converted using :meth:`arrayToFrame` with properties
        defined by *frameProperty*. Empty array is converted to invalid video
        frame.

        """
        if array.size != 0:
            frame = self.arrayToFrame(array)
        else:
            frameFormat = QVideoFrameFormat(
                QtCore.QSize(-1, -1), QVideoFrameFormat.PixelFormat.Format_Invalid
            )
            frame = QVideoFrame(frameFormat)
        frameProperty.setToVideoFrame(frame)
        self.frameConverted.emit(frame)

    def arrayToFrame(self, array: npt.NDArray[np.uint8]) -> QVideoFrame:
        """
        Converts *array* to ``QVideoFrame``.

        By default this method uses :func:`array2qvideoframe` for conversion.
        Subclass can redefine this method.
        """
        return array2qvideoframe(array)


class ArrayWorker(QtCore.QObject):
    """
    Worker to process numpy array.

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

    .. figure:: ../_images/array-processor.jpg
       :align: center

       NDArray processing structure

    :class:`ArrayProcessor` runs :class:`ArrayWorker` in internal an thread t
    process the incoming array. To perform processing, pass the input array to
    :meth:`processArray` slot and listen to :attr:`arrayProcessed` signal.

    :meth:`skipIfRunning` defines whether the incoming arrays should be skipped
    when the worker is running.

    """

    _processRequested = QtCore.Signal(np.ndarray)
    arrayProcessed = QtCore.Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._skipIfRunning = True

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

    def skipIfRunning(self) -> bool:
        """
        If True, incoming arrays to :meth:`processArray` are skipped if
        :meth:`worker` is not ready.

        If False, incoming arrays are queued if worker is not ready. This may
        consume a significant amount of memory and cause laggy displaying, thus
        should be used with discretion.

        See also :meth:`setSkipIfRunning`.
        """
        return self._skipIfRunning

    def setSkipIfRunning(self, flag: bool):
        """
        Set :meth:`skipIfRunning` to *flag*.

        See also :meth:`skipIfRunning`.
        """
        self._skipIfRunning = flag

    @QtCore.Slot(np.ndarray)
    def processArray(self, array: npt.NDArray[np.uint8]):
        """
        Request :meth:`worker` to process *array*.

        The result is emitted to :attr:`arrayProcessed`.

        If worker is running and :meth:`skipIfRunning` is True, *array* is
        skipped without being emitted. If :meth:`skipIfRunning` is False,
        incoming arrays are queued when worker is running.

        """
        worker = self.worker()
        if worker is not None:
            if worker.ready() or not self.skipIfRunning():
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

    When playing, :class:`NDArrayVideoPlayer` converts the frame to numpy array
    and :class:`QVideoFrameProperty`, and emits them to :attr:`arrayChanged`
    signal.

    User may use this class for convenience, or define own pipeline.
    """

    arrayChanged = QtCore.Signal(np.ndarray, QVideoFrameProperty)

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

    When capturing, :class:`NDArrayMediaCaptureSession` converts the frame to
    numpy array and :class:`QVideoFrameProperty`, and emits them to
    :attr:`arrayChanged` signal.

    User may use this class for convenience, or define own pipeline.
    """

    arrayChanged = QtCore.Signal(np.ndarray, QVideoFrameProperty)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._videoSink = QtMultimedia.QVideoSink()
        self._arrayConverter = FrameToArrayConverter(self)

        self.setVideoSink(self._videoSink)
        self._videoSink.videoFrameChanged.connect(
            self._arrayConverter.convertVideoFrame
        )
        self._arrayConverter.arrayConverted.connect(self.arrayChanged)
