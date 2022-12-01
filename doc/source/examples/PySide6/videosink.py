import cv2  # type: ignore[import]
import numpy as np
from PySide6.QtCore import QObject, Signal, Slot, QThread
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QMainWindow
from PySide6.QtMultimedia import (
    QCamera,
    QMediaCaptureSession,
    QVideoFrame,
    QVideoFrameFormat,
    QVideoSink,
)
from PySide6.QtMultimediaWidgets import QVideoWidget
import qimage2ndarray  # type: ignore[import]
from typing import Optional


# Monkeypatch qimage2ndarray until new version (> 1.9.0)
# https://github.com/hmeine/qimage2ndarray/issues/29
for name, qimage_format in qimage2ndarray.qimageview_python.FORMATS.items():
    if name in dir(QImage.Format):
        qimage_format.code = getattr(QImage, name)


class ProcessWorker(QObject):

    videoFrameChanged = Signal(QVideoFrame)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ready = True

    def ready(self) -> bool:
        return self._ready

    @Slot(QVideoFrame)
    def setVideoFrame(self, frame: QVideoFrame):
        self._ready = False

        qimg = frame.toImage()  # must assign to avoid crash
        array = self.imageToArray(qimg)
        newarray = self.processArray(array)
        newimg = qimage2ndarray.array2qimage(newarray)
        pixelFormat = QVideoFrameFormat.pixelFormatFromImageFormat(newimg.format())
        frameFormat = QVideoFrameFormat(newimg.size(), pixelFormat)
        processedFrame = QVideoFrame(frameFormat)
        processedFrame.map(QVideoFrame.MapMode.WriteOnly)
        processedFrame.bits(0)[:] = newimg.bits()  # type: ignore[index]
        processedFrame.unmap()

        self.videoFrameChanged.emit(processedFrame)
        self._ready = True

    def imageToArray(self, image: QImage) -> np.ndarray:
        return qimage2ndarray.rgb_view(image, byteorder=None)

    def processArray(self, array: np.ndarray) -> np.ndarray:
        return cv2.GaussianBlur(array, (0, 0), 25)


class VideoFrameProcessor(QObject):

    _processRequested = Signal(QVideoFrame)
    videoFrameChanged = Signal(QVideoFrame)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None

        self._processorThread = QThread()
        self._processorThread.start()

    def worker(self) -> Optional[ProcessWorker]:
        return self._worker

    def setWorker(self, worker: Optional[ProcessWorker]):
        oldWorker = self.worker()
        if oldWorker is not None:
            self._processRequested.disconnect(oldWorker.setVideoFrame)
            oldWorker.videoFrameChanged.disconnect(self.videoFrameChanged)
        self._worker = worker
        if worker is not None:
            self._processRequested.connect(worker.setVideoFrame)
            worker.videoFrameChanged.connect(self.videoFrameChanged)
            worker.moveToThread(self._processorThread)

    @Slot(QVideoFrame)
    def setVideoFrame(self, frame: QVideoFrame):
        worker = self._worker
        if not worker.ready():
            return
        self._processRequested.emit(frame)

    def stop(self):
        self._processorThread.quit()
        self._processorThread.wait()


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._camera = QCamera()
        self._captureSession = QMediaCaptureSession()
        self._cameraVideoSink = QVideoSink()
        self._frameProcessor = VideoFrameProcessor()
        self._videoWidget = QVideoWidget()

        # set up the pipeline
        self._captureSession.setCamera(self._camera)
        self._captureSession.setVideoSink(self._cameraVideoSink)
        self._cameraVideoSink.videoFrameChanged.connect(
            self._frameProcessor.setVideoFrame
        )
        self._frameProcessor.videoFrameChanged.connect(self.displayVideoFrame)

        self._frameProcessor.setWorker(ProcessWorker())
        self.setCentralWidget(self._videoWidget)

        self._camera.start()

    @Slot(QVideoFrame)
    def displayVideoFrame(self, frame: QVideoFrame):
        self._videoWidget.videoSink().setVideoFrame(frame)

    def closeEvent(self, event):
        self._frameProcessor.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()
    app.quit()
