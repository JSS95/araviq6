from araviq6.qt_compat import QtCore, QtMultimedia
from araviq6 import VideoProcessWorker, get_samples_path
from araviq6.util import VideoProcessWorkerTester


def test_VideoProcessWorkerTester(qtbot):
    player = QtMultimedia.QMediaPlayer()
    sink = QtMultimedia.QVideoSink()
    worker = VideoProcessWorker()
    tester = VideoProcessWorkerTester()

    player.setVideoSink(sink)
    sink.videoFrameChanged.connect(tester.setVideoFrame)
    tester.maximumReached.connect(player.stop)

    tester.setWorker(worker)
    player.setSource(QtCore.QUrl.fromLocalFile(get_samples_path("hello.mp4")))
    player.play()
    qtbot.waitUntil(lambda: player.playbackState() != player.PlaybackState.PlayingState)
