"""Camera example with multithreaded Gaussian blurring process."""

import cv2  # type: ignore
import numpy as np
from PySide6.QtCore import QObject, Signal, Slot, Qt, QThread
from PySide6.QtMultimedia import QMediaCaptureSession, QVideoSink, QVideoFrame
from PySide6.QtWidgets import QMainWindow
from arabesque6 import FrameToArrayConverter, NDArrayLabel


class FrameSender(QObject):
    """Object to sent the array to processor thread."""

    frameChanged = Signal(QVideoFrame)


class BlurringProcessor(QObject):
    """Video pipeline component for Gaussian blurring on numpy array."""

    arrayChanged = Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ready = True

    def ready(self) -> bool:
        return self._ready

    @Slot(np.ndarray)
    def setArray(self, array: np.ndarray):
        self._ready = False
        self.arrayChanged.emit(cv2.GaussianBlur(array, (0, 0), 25))
        self._ready = True


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._captureSession = QMediaCaptureSession()
        self._frameSender = FrameSender()
        self._processorThread = QThread()
        self._frame2Arr = FrameToArrayConverter()
        self._arrayProcessor = BlurringProcessor()
        self._arrayLabel = NDArrayLabel()

        self.frameToArrayConverter().moveToThread(self.processorThread())
        self.arrayProcessor().moveToThread(self.processorThread())
        self.processorThread().start()

        self.captureSession().setVideoSink(QVideoSink(self))
        self.captureSession().videoSink().videoFrameChanged.connect(
            self.onFramePassedFromCamera
        )
        self._frameSender.frameChanged.connect(
            self.frameToArrayConverter().setVideoFrame
        )
        self.frameToArrayConverter().arrayChanged.connect(
            self.arrayProcessor().setArray
        )
        self.arrayProcessor().arrayChanged.connect(self.arrayLabel().setArray)

        self.arrayLabel().setAlignment(Qt.AlignCenter)  # type: ignore[arg-type]
        self.setCentralWidget(self.arrayLabel())

        camera = QCamera(self)
        self.captureSession().setCamera(camera)
        camera.start()

    def captureSession(self) -> QMediaCaptureSession:
        return self._captureSession

    def processorThread(self) -> QThread:
        return self._processorThread

    def frameToArrayConverter(self) -> FrameToArrayConverter:
        return self._frame2Arr

    def arrayProcessor(self) -> BlurringProcessor:
        return self._arrayProcessor

    def arrayLabel(self) -> NDArrayLabel:
        return self._arrayLabel

    @Slot(QVideoFrame)
    def onFramePassedFromCamera(self, frame: QVideoFrame):
        if self.arrayProcessor().ready():
            self._frameSender.frameChanged.emit(frame)

    def closeEvent(self, event):
        self.processorThread().quit()
        self.processorThread().wait()
        super().closeEvent(event)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    from PySide6.QtMultimedia import QCamera
    import sys

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()
    app.quit()
