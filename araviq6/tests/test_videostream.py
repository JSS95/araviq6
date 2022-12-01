import cv2  # type: ignore[import]
import numpy as np
import pytest
from qimage2ndarray import byte_view, gray2qimage, array2qimage  # type: ignore[import]
from araviq6 import VideoProcessWorker, FrameToArrayConverter
from araviq6.util import VideoProcessWorkerTester, get_samples_path
from araviq6.qt_compat import QtCore, QtMultimedia


def test_VideoProcessWorker(qtbot):
    class BGRWorker(VideoProcessWorker):
        def processArray(self, array):
            return cv2.cvtColor(array, cv2.COLOR_RGB2BGR)

    player = QtMultimedia.QMediaPlayer()
    sink = QtMultimedia.QVideoSink()
    worker = BGRWorker()
    tester = VideoProcessWorkerTester()

    player.setVideoSink(sink)
    sink.videoFrameChanged.connect(tester.setVideoFrame)
    tester.maximumReached.connect(player.stop)

    tester.setWorker(worker)
    player.setSource(QtCore.QUrl.fromLocalFile(get_samples_path("hello.mp4")))
    player.play()
    qtbot.waitUntil(lambda: player.playbackState() != player.PlaybackState.PlayingState)


def test_FrameToArrayConverter(qtbot):
    bgr_array = cv2.imread(get_samples_path("hello.jpg"))
    gray_array = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2GRAY)
    rgb_array = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2RGB)

    gray_img = gray2qimage(gray_array)
    rgb_img = array2qimage(rgb_array)

    conv = FrameToArrayConverter()
    assert np.all(conv.convertQImageToArray(rgb_img) == rgb_array)
    with pytest.raises(ValueError):
        conv.convertQImageToArray(gray_img)

    conv.setConverter(byte_view)
    assert np.all(conv.convertQImageToArray(gray_img) == gray_array[..., np.newaxis])
