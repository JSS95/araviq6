"""
Video player example with array-based video player and canny edge detection
pipeline on numpy array.

The processor directly receives numpy array from the media player, and emits
processed array.

"""

import cv2  # type: ignore[import]
import numpy as np
from PySide6.QtCore import QObject, Signal, Slot, QThread, Qt, QUrl
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PySide6.QtMultimedia import QMediaPlayer
from araviq6 import NDArrayVideoPlayer, MediaController, NDArrayLabel


class CannyEdgeDetector(QObject):
    """
    Video pipeline component for Canny edge detection on numpy array.
    """

    arrayChanged = Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._canny_mode = False
        self._ready = True

    def cannyMode(self) -> bool:
        """If False, Canny edge detection is not performed."""
        return self._canny_mode

    def ready(self) -> bool:
        return self._ready

    @Slot(bool)
    def setCannyMode(self, mode: bool):
        self._canny_mode = mode

    def setArray(self, array: np.ndarray):
        self._ready = False
        if array.size == 0:
            ret = array
        elif self.cannyMode():
            gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
            canny = cv2.Canny(gray, 50, 200)
            ret = cv2.cvtColor(canny, cv2.COLOR_GRAY2RGB)
        else:
            ret = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
        self.arrayChanged.emit(ret)
        self._ready = True


class CannyVideoPlayerWidget(QWidget):

    _processRequested = Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._lastVideoFrame = np.empty((0, 0, 0), dtype=np.uint8)

        self._videoPlayer = NDArrayVideoPlayer(self)
        self._processorThread = QThread()
        self._arrayProcessor = CannyEdgeDetector()
        self._arrayLabel = NDArrayLabel()
        self._mediaController = MediaController()
        self._cannyButton = QPushButton()

        self._arrayProcessor.moveToThread(self._processorThread)
        self._processorThread.start()

        self._videoPlayer.arrayChanged.connect(self._displayImageFromPlayer)
        self._processRequested.connect(self._arrayProcessor.setArray)
        self._arrayProcessor.arrayChanged.connect(self._arrayLabel.setArray)

        self._arrayLabel.setAlignment(Qt.AlignCenter)
        self._mediaController.setPlayer(self._videoPlayer)
        self._cannyButton.setCheckable(True)
        self._cannyButton.toggled.connect(self._onCannyButtonToggle)

        self._cannyButton.setText("Toggle edge detection")

        layout = QVBoxLayout()
        layout.addWidget(self._arrayLabel)
        layout.addWidget(self._mediaController)
        layout.addWidget(self._cannyButton)
        self.setLayout(layout)

    def setSource(self, url: QUrl):
        self._videoPlayer.setSource(url)

    @Slot(np.ndarray)
    def _displayImageFromPlayer(self, array: np.ndarray):
        self._lastVideoFrame = array.copy()

        processor = self._arrayProcessor
        if processor.ready():
            self._processRequested.emit(array)

    @Slot(bool)
    def _onCannyButtonToggle(self, state: bool):
        processor = self._arrayProcessor
        processor.setCannyMode(state)
        state = self._videoPlayer.playbackState()
        if state != QMediaPlayer.PlaybackState.PlayingState:
            processor.setArray(self._lastVideoFrame)

    def closeEvent(self, event):
        self._processorThread.quit()
        self._processorThread.wait()
        super().closeEvent(event)


if __name__ == "__main__":
    from araviq6 import get_samples_path
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    widget = CannyVideoPlayerWidget()
    url = QUrl.fromLocalFile(get_samples_path("hello.mp4"))
    widget.setSource(url)
    widget.show()
    app.exec()
    app.quit()
