"""
Video player example with canny edge detection pipeline on QVideoframe.

The processor receives video frame from the video sink of media player, and emits
processed video frame.

"""

import cv2  # type: ignore[import]
import numpy as np
from PyQt6.QtCore import pyqtSlot, QUrl
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PyQt6.QtMultimedia import QMediaPlayer, QVideoSink, QVideoFrame
from PyQt6.QtMultimediaWidgets import QVideoWidget
from araviq6 import VideoFrameWorker, VideoFrameProcessor, MediaController


class CannyWorker(VideoFrameWorker):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cannyMode = False

    def setCannyMode(self, mode: bool):
        self._cannyMode = mode

    def processArray(self, array: np.ndarray) -> np.ndarray:
        if self._cannyMode and array.size > 0:
            gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
            canny = ~cv2.Canny(gray, 50, 200)
            array = cv2.cvtColor(canny, cv2.COLOR_GRAY2RGB)
        return array


class Window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._videoPlayer = QMediaPlayer()
        self._playerVideoSink = QVideoSink()
        self._frameProcessor = VideoFrameProcessor()
        self._cannyWorker = CannyWorker()
        self._videoWidget = QVideoWidget()
        self._mediaController = MediaController()
        self._cannyButton = QPushButton()

        # set up the pipeline
        self._videoPlayer.setVideoSink(self._playerVideoSink)
        self._playerVideoSink.videoFrameChanged.connect(
            self._frameProcessor.processVideoFrame
        )
        self._frameProcessor.videoFrameProcessed.connect(self.displayVideoFrame)

        self._mediaController.setPlayer(self._videoPlayer)
        self._frameProcessor.setWorker(self._cannyWorker)
        self._cannyButton.setCheckable(True)
        self._cannyButton.toggled.connect(self._onCannyButtonToggle)

        self._cannyButton.setText("Toggle edge detection")

        layout = QVBoxLayout()
        layout.addWidget(self._videoWidget)
        layout.addWidget(self._mediaController)
        layout.addWidget(self._cannyButton)
        self.setLayout(layout)

    def _onCannyButtonToggle(self, state: bool):
        self._cannyWorker.setCannyMode(state)
        if self._videoPlayer.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
            self._frameProcessor.processVideoFrame(self._playerVideoSink.videoFrame())

    def setSource(self, url: QUrl):
        self._videoPlayer.setSource(url)

    @pyqtSlot(QVideoFrame)
    def displayVideoFrame(self, frame: QVideoFrame):
        self._videoWidget.videoSink().setVideoFrame(frame)

    def closeEvent(self, event):
        self._frameProcessor.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    from araviq6 import get_data_path
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = Window()
    url = QUrl.fromLocalFile(get_data_path("hello.mp4"))
    window.setSource(url)
    window.show()
    app.exec()
    app.quit()
