import cv2  # type: ignore[import]
import numpy as np
import qimage2ndarray  # type: ignore[import]
import pytest
from araviq6 import VideoProcessWorker, FrameToArrayConverter
from araviq6.util import VideoProcessWorkerTester, get_samples_path
from araviq6.qt_compat import QtCore, QtMultimedia


def test_VideoProcessWorker(qtbot):
    class BGRWorker(VideoProcessWorker):
        def processArray(self, array):
            return cv2.cvtColor(array, cv2.COLOR_RGB2BGR)

    worker = BGRWorker()
    tester = VideoProcessWorkerTester()
    tester.setWorker(worker)

    player = QtMultimedia.QMediaPlayer()
    sink = QtMultimedia.QVideoSink()
    player.setVideoSink(sink)
    sink.videoFrameChanged.connect(player.stop)

    player.setSource(QtCore.QUrl.fromLocalFile(get_samples_path("hello.mp4")))
    player.play()

    tester.testVideoFrame(sink.videoFrame())
    player.stop()


def test_FrameToArrayConverter(qtbot):
    bgr_array = cv2.imread(get_samples_path("hello.jpg"))
    gray_array = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2GRAY)
    rgb_array = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2RGB)

    gray_img = qimage2ndarray.gray2qimage(gray_array)
    rgb_img = qimage2ndarray.array2qimage(rgb_array)

    conv = FrameToArrayConverter()
    assert np.all(conv.convertQImageToArray(rgb_img) == rgb_array)
    with pytest.raises(ValueError):
        conv.convertQImageToArray(gray_img)

    conv.setConverter(qimage2ndarray.byte_view)
    assert np.all(conv.convertQImageToArray(gray_img) == gray_array[..., np.newaxis])
