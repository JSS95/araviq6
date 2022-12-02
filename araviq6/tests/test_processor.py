import cv2  # type: ignore[import]
from araviq6 import VideoProcessWorker
from araviq6.util import (
    get_samples_path,
    ValidVideoFrameSink,
    VideoProcessWorkerTester,
)
from araviq6.qt_compat import QtCore, QtMultimedia


def test_VideoProcessWorker(qtbot):
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

    class BGRWorker(VideoProcessWorker):
        def processArray(self, array):
            return cv2.cvtColor(array, cv2.COLOR_RGB2BGR)

    worker = BGRWorker()
    tester.setWorker(worker)

    player.play()
    qtbot.waitUntil(lambda: player.playbackState() != player.PlaybackState.PlayingState)
    assert validSink.videoFrame().isValid()
    tester.testVideoFrame(validSink.videoFrame())
    player.play()
    qtbot.waitUntil(lambda: player.playbackState() != player.PlaybackState.PlayingState)
    assert validSink.videoFrame().isValid()
    tester.testVideoFrame(validSink.videoFrame())

    player.stop()
