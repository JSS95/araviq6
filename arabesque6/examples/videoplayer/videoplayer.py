"""Video player example with multithreaded canny edge detection process."""

import cv2  # type: ignore[import]
import numpy as np
from PySide6.QtCore import QObject, Signal, Slot, QThread, Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QVideoSink, QVideoFrame
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout
from arabesque6 import FrameToArrayConverter, MediaController, NDArrayLabel


class FrameSender(QObject):
    """Object to sent the array to processor thread."""

    frameChanged = Signal(QVideoFrame)


class CannyEdgeDetector(QObject):
    """
    Video pipeline component for Canny edge detection on numpy array.
    """

    arrayChanged = Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._currentArray = np.empty((0, 0, 0))
        self._canny_mode = False
        self._ready = True

    def currentArray(self) -> np.ndarray:
        """Last array passed to :meth:`setArray`."""
        return self._currentArray

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
        self._currentArray = array
        if array.size > 0 and self.cannyMode():
            gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
            canny = cv2.Canny(gray, 50, 200)
            ret = cv2.cvtColor(canny, cv2.COLOR_GRAY2RGB)
        else:
            ret = array
        self.arrayChanged.emit(ret)
        self._ready = True

    def refreshCurrentArray(self):
        """Re-process and emit :meth:`currentArray`."""
        self.setArray(self.currentArray())


class CannyVideoPlayerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._videoPlayer = QMediaPlayer(self)
        self._frameSender = FrameSender()
        self._processorThread = QThread()
        self._frame2Arr = FrameToArrayConverter()
        self._arrayProcessor = CannyEdgeDetector()
        self._arrayLabel = NDArrayLabel()
        self._mediaController = MediaController()
        self._cannyButton = QPushButton()

        self.frameToArrayConverter().moveToThread(self.processorThread())
        self.arrayProcessor().moveToThread(self.processorThread())
        self.processorThread().start()

        self.videoPlayer().setVideoSink(QVideoSink(self))
        self.videoPlayer().videoSink().videoFrameChanged.connect(
            self.onFramePassedFromCamera
        )
        self._frameSender.frameChanged.connect(
            self.frameToArrayConverter().setVideoFrame
        )
        self.frameToArrayConverter().arrayChanged.connect(
            self.arrayProcessor().setArray
        )
        self.arrayProcessor().arrayChanged.connect(self.arrayLabel().setArray)

        self.arrayLabel().setAlignment(Qt.AlignCenter)
        self.mediaController().setPlayer(self.videoPlayer())
        self.cannyButton().setCheckable(True)
        self.cannyButton().toggled.connect(self.onCannyButtonToggle)

        self.cannyButton().setText("Toggle edge detection")

        layout = QVBoxLayout()
        layout.addWidget(self.arrayLabel())
        layout.addWidget(self.mediaController())
        layout.addWidget(self.cannyButton())
        self.setLayout(layout)

    def videoPlayer(self) -> QMediaPlayer:
        return self._videoPlayer

    def processorThread(self) -> QThread:
        return self._processorThread

    def frameToArrayConverter(self) -> FrameToArrayConverter:
        return self._frame2Arr

    def arrayProcessor(self) -> CannyEdgeDetector:
        return self._arrayProcessor

    def arrayLabel(self) -> NDArrayLabel:
        return self._arrayLabel

    def mediaController(self) -> MediaController:
        return self._mediaController

    def cannyButton(self) -> QPushButton:
        return self._cannyButton

    @Slot(QVideoFrame)
    def onFramePassedFromCamera(self, frame: QVideoFrame):
        if self.arrayProcessor().ready():
            self._frameSender.frameChanged.emit(frame)

    @Slot(bool)
    def onCannyButtonToggle(self, state: bool):
        self.arrayProcessor().setCannyMode(state)
        if self.videoPlayer().playbackState() != self.videoPlayer().PlayingState:
            self.arrayProcessor().refreshCurrentArray()

    def closeEvent(self, event):
        self.processorThread().quit()
        self.processorThread().wait()
        super().closeEvent(event)


if __name__ == "__main__":
    from cv2PySide6 import get_data_path
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    widget = CannyVideoPlayerWidget()
    url = QUrl.fromLocalFile(get_data_path("hello.mp4"))
    widget.videoPlayer().setSource(url)
    widget.show()
    app.exec()
    app.quit()
