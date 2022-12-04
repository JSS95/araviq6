"""
Video player example with array-based video player and canny edge detection
pipeline on numpy array.

The processor directly receives numpy array from the media player, and emits
processed array.

"""

import cv2  # type: ignore[import]
import numpy as np
from PySide6.QtCore import Signal, Qt, QUrl
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PySide6.QtMultimedia import QMediaPlayer
from araviq6 import (
    ArrayProcessWorker,
    ArrayProcessor,
    NDArrayVideoPlayer,
    MediaController,
    NDArrayLabel,
)


class CannyWorker(ArrayProcessWorker):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cannyMode = False

    def setCannyMode(self, mode: bool):
        self._cannyMode = mode

    def processArray(self, array: np.ndarray) -> np.ndarray:
        if self._cannyMode and array.size > 0:
            gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
            canny = cv2.Canny(gray, 50, 200)
            array = cv2.cvtColor(canny, cv2.COLOR_GRAY2RGB)
        return array


class CannyVideoPlayerWidget(QWidget):

    _processRequested = Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._lastVideoArray = np.empty((0, 0, 0), dtype=np.uint8)

        self._videoPlayer = NDArrayVideoPlayer(self)
        self._arrayProcessor = ArrayProcessor()
        self._cannyWorker = CannyWorker()
        self._arrayLabel = NDArrayLabel()
        self._mediaController = MediaController()
        self._cannyButton = QPushButton()

        # set up the pipeline
        self._videoPlayer.arrayChanged.connect(self._storeLastVideoArray)
        self._videoPlayer.arrayChanged.connect(self._arrayProcessor.processArray)
        self._arrayProcessor.arrayProcessed.connect(self._arrayLabel.setArray)

        self._arrayLabel.setAlignment(Qt.AlignCenter)
        self._mediaController.setPlayer(self._videoPlayer)
        self._arrayProcessor.setWorker(self._cannyWorker)
        self._cannyButton.setCheckable(True)
        self._cannyButton.toggled.connect(self._onCannyButtonToggle)

        self._cannyButton.setText("Toggle edge detection")

        layout = QVBoxLayout()
        layout.addWidget(self._arrayLabel)
        layout.addWidget(self._mediaController)
        layout.addWidget(self._cannyButton)
        self.setLayout(layout)

    def _onCannyButtonToggle(self, state: bool):
        self._cannyWorker.setCannyMode(state)
        if self._videoPlayer.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
            self._arrayProcessor.processArray(self._lastVideoArray)

    def _storeLastVideoArray(self, array: np.ndarray):
        self._lastVideoArray = array.copy()

    def setSource(self, url: QUrl):
        self._videoPlayer.setSource(url)

    def closeEvent(self, event):
        self._arrayProcessor.stop()
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
