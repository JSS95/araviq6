# pytest-xvfb may fail by running this code in ubuntu.
# It's because for unknown reason, ``QVideoFrame.toImage()`` suffers memory issue
# when the video frame is manually constructed and modified.
# This issue happens only when any other test file is run before this one.
# Should the user encounter such error, run the test for this file separately.

import numpy as np
import qimage2ndarray  # type: ignore[import]
from araviq6 import array2qvideoframe, byte_view, rgb_view, alpha_view, get_samples_path
from araviq6.qt_compat import QtCore, QtMultimedia


def test_views(qtbot):
    player = QtMultimedia.QMediaPlayer()
    sink = QtMultimedia.QVideoSink()
    player.setVideoSink(sink)
    sink.videoFrameChanged.connect(player.stop)
    with qtbot.waitSignal(sink.videoFrameChanged):
        player.setSource(QtCore.QUrl.fromLocalFile(get_samples_path("hello.mp4")))
        player.play()
    frame = sink.videoFrame()
    assert frame.isValid()
    frame.map(QtMultimedia.QVideoFrame.MapMode.ReadOnly)

    assert np.all(
        byte_view(frame)[0, 0] == np.array([157, 161, 167, 255], dtype=np.uint8)
    )
    assert np.all(rgb_view(frame)[0, 0] == np.array([167, 161, 157], dtype=np.uint8))
    assert np.all(alpha_view(frame)[0, 0] == np.array([255], dtype=np.uint8))


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
