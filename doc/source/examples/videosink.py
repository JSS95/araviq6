from PySide6.QtCore import QObject, Signal, Slot, QThread
from PySide6.QtWidgets import QMainWindow
from PySide6.QtMultimedia import QCamera, QMediaCaptureSession, QVideoFrame, QVideoSink
from PySide6.QtMultimediaWidgets import QVideoWidget
import time


class VideoFrameProcessor(QObject):

    _processRequested = Signal(QVideoFrame)
    videoFrameChanged = Signal(QVideoFrame)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = ProcessWorker()

        self._processRequested.connect(self._worker.setVideoFrame)
        self._worker.videoFrameChanged.connect(self.videoFrameChanged)

        self._processorThread = QThread()
        self._worker.moveToThread(self._processorThread)
        self._processorThread.start()

    def setVideoFrame(self, frame: QVideoFrame):
        worker = self._worker
        if not worker.ready():
            return
        self._processRequested.emit(frame)

    def stop(self):
        self._processorThread.quit()
        self._processorThread.wait()


class ProcessWorker(QObject):

    videoFrameChanged = Signal(QVideoFrame)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ready = True

    def ready(self) -> bool:
        return self._ready

    def setVideoFrame(self, frame: QVideoFrame):  # do not decorate with Slot
        self._ready = False
        time.sleep(0.1)  # TODO: implement video processing
        self.videoFrameChanged.emit(frame)
        self._ready = True


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
