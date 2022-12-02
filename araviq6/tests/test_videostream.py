import cv2  # type: ignore[import]
from araviq6 import VideoProcessWorker
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
