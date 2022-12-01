from araviq6 import VideoProcessWorker
from araviq6.util import VideoProcessWorkerTester, get_samples_path
from araviq6.qt_compat import QtCore, QtMultimedia


def test_VideoProcessWorkerTester(qtbot):
    worker = VideoProcessWorker()
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
