# pytest-xvfb may fail by running this code in ubuntu.
# It's because for unknown reason, ``QVideoFrame.toImage()`` suffers memory issue
# when the video frame is manually constructed and modified.
# This issue happens only when any other test file is run before this one.
# Should the user encounter such error, run the test for this file separately.

import numpy as np
import qimage2ndarray  # type: ignore[import]
from araviq6 import (
    array2qvideoframe,
    FrameToArrayConverter,
    ArrayToFrameConverter,
    get_samples_path,
)
from araviq6.qt_compat import QtCore, QtMultimedia


def test_array2qvideoframe(qtbot):
    bgr_array1 = np.array([[[1]]], dtype=np.uint8)
    frame1 = array2qvideoframe(bgr_array1)
    assert np.all(
        qimage2ndarray.byte_view(frame1.toImage())
        == np.array([[[1, 1, 1, 255]]], dtype=np.uint8)
    )
    assert np.all(
        qimage2ndarray.rgb_view(frame1.toImage()) == np.array([[[1]]], dtype=np.uint8)
    )
    assert np.all(
        qimage2ndarray.alpha_view(frame1.toImage())
        == np.array([[[255]]], dtype=np.uint8)
    )

    bgr_array2 = np.array([[[1, 2]]], dtype=np.uint8)
    frame2 = array2qvideoframe(bgr_array2)
    assert np.all(
        qimage2ndarray.byte_view(frame2.toImage())
        == np.array([[[1, 1, 1, 2]]], dtype=np.uint8)
    )
    assert np.all(
        qimage2ndarray.rgb_view(frame2.toImage()) == np.array([[[1]]], dtype=np.uint8)
    )
    assert np.all(
        qimage2ndarray.alpha_view(frame2.toImage()) == np.array([[[2]]], dtype=np.uint8)
    )

    bgr_array3 = np.array([[[1, 2, 3]]], dtype=np.uint8)
    frame3 = array2qvideoframe(bgr_array3)
    assert np.all(
        qimage2ndarray.byte_view(frame3.toImage())
        == np.array([[[1, 2, 3, 255]]], dtype=np.uint8)
    )
    assert np.all(
        qimage2ndarray.rgb_view(frame3.toImage())
        == np.array([[[3, 2, 1]]], dtype=np.uint8)
    )
    assert np.all(
        qimage2ndarray.alpha_view(frame3.toImage())
        == np.array([[[255]]], dtype=np.uint8)
    )

    bgr_array4 = np.array([[[1, 2, 3, 4]]], dtype=np.uint8)
    frame4 = array2qvideoframe(bgr_array4)
    assert np.all(
        qimage2ndarray.byte_view(frame4.toImage())
        == np.array([[[1, 2, 3, 4]]], dtype=np.uint8)
    )
    assert np.all(
        qimage2ndarray.rgb_view(frame4.toImage())
        == np.array([[[3, 2, 1]]], dtype=np.uint8)
    )
    assert np.all(
        qimage2ndarray.alpha_view(frame4.toImage()) == np.array([[[4]]], dtype=np.uint8)
    )


def test_FrameToArrayConverter(qtbot):
    class ArraySink(QtCore.QObject):
        arrayChanged = QtCore.Signal()

        def setArray(self, array):
            if array.size != 0:
                self.array = array
                self.arrayChanged.emit()

    player = QtMultimedia.QMediaPlayer()
    playerSink = QtMultimedia.QVideoSink()
    converter = FrameToArrayConverter()
    arraySink = ArraySink()

    player.setVideoSink(playerSink)
    playerSink.videoFrameChanged.connect(converter.convertVideoFrame)
    converter.arrayConverted.connect(arraySink.setArray)
    arraySink.arrayChanged.connect(player.stop)

    with qtbot.waitSignal(arraySink.arrayChanged):
        player.setSource(QtCore.QUrl.fromLocalFile(get_samples_path("hello.mp4")))
        player.play()

    with qtbot.waitSignal(
        converter.arrayConverted, check_params_cb=lambda array, _: array.size == 0
    ):
        converter.convertVideoFrame(QtMultimedia.QVideoFrame())


def test_ArrayToFrameConverter(qtbot):
    class FrameSink(QtCore.QObject):
        frameChanged = QtCore.Signal()

        def setFrame(self, frame):
            if frame.isValid():
                self.frame = frame
                self.frameChanged.emit()

    player = QtMultimedia.QMediaPlayer()
    playerSink = QtMultimedia.QVideoSink()
    F2AConverter = FrameToArrayConverter()
    A2FConverter = ArrayToFrameConverter()
    frameSink = FrameSink()

    player.setVideoSink(playerSink)
    playerSink.videoFrameChanged.connect(F2AConverter.convertVideoFrame)
    F2AConverter.arrayConverted.connect(A2FConverter.convertArray)
    A2FConverter.frameConverted.connect(frameSink.setFrame)
    frameSink.frameChanged.connect(player.stop)

    with qtbot.waitSignal(frameSink.frameChanged):
        player.setSource(QtCore.QUrl.fromLocalFile(get_samples_path("hello.mp4")))
        player.play()
    assert frameSink.frame.startTime() != -1
    assert frameSink.frame.endTime() != -1

    sourceFrame = playerSink.videoFrame()
    with qtbot.waitSignal(
        A2FConverter.frameConverted,
        check_params_cb=lambda frame: not frame.isValid()
        and frame.surfaceFormat().pixelFormat()
        == sourceFrame.surfaceFormat().pixelFormat(),
    ):
        A2FConverter.convertArray(np.empty((0, 0, 0), dtype=np.uint8), sourceFrame)

    with qtbot.waitSignal(
        A2FConverter.frameConverted, check_params_cb=lambda frame: not frame.isValid()
    ):
        A2FConverter.convertArray(np.empty((0, 0, 0), dtype=np.uint8))
