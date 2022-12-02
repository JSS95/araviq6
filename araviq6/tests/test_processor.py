from araviq6 import VideoProcessWorker
from araviq6.util import (
    get_samples_path,
    ValidVideoFrameSink,
    VideoProcessWorkerTester,
)
from araviq6.qt_compat import QtCore, QtMultimedia


def test_VideoProcessWorkerTester(qtbot):
    worker = VideoProcessWorker()
    tester = VideoProcessWorkerTester()
    tester.setWorker(worker)

    player = QtMultimedia.QMediaPlayer()
    playerSink = QtMultimedia.QVideoSink()
    validSink = ValidVideoFrameSink()
    player.setVideoSink(playerSink)
    playerSink.videoFrameChanged.connect(validSink.setVideoFrame)
    validSink.videoFrameChanged.connect(player.pause)

    player.setSource(QtCore.QUrl.fromLocalFile(get_samples_path("hello.mp4")))

    player.play()
    qtbot.waitUntil(lambda: player.playbackState() != player.PlaybackState.PlayingState)
    assert validSink.videoFrame().isValid()
    tester.testVideoFrame(validSink.videoFrame())

    player.play()
    qtbot.waitUntil(lambda: player.playbackState() != player.PlaybackState.PlayingState)
    assert validSink.videoFrame().isValid()
    tester.testVideoFrame(validSink.videoFrame())

    player.stop()
