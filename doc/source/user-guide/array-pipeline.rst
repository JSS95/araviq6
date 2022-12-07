.. _guide-arraypipeline:

===================================
How to build NDArray-based pipeline
===================================

.. currentmodule:: araviq6

In :ref:`guide-processor`, we have built a processor and a pipline based on QVideoFrame.
Now let's learn how to build NDArray-based pipeline.

.. figure:: ../_images/array-pipeline.jpg
   :align: center

   NDArray-based pipeline design

Introduction
------------

Third party packages (e.g., Python binding of machine vision driver) often provide video frames as NDArray.
Also the user may need the image processing result as numpy array for further tasks.
These are where we need a pipeline with NDArray.

AraViQ6 provides :class:`.ArrayToFrameConverter` and :class:`.FrameToArrayConverter` which converts NDArray to QVideoFrame and vice versa.
Although attaching these classes to QVideoFrame-based pipeline effectively acts as NDArray pipeline, there are several classes which directly handles NDArray.

1. :class:`.NDArrayVideoPlayer` and :class:`.NDArrayMediaCaptureSession` as array source
2. :class:`.ArrayProcessor` as array processor
3. :class:`.NDArrayLabel` to display array

Using the classes above, we will construct a video player which is identical to that of :ref:`guide-processor`.
Here is the complete code:

.. tabs::

    .. code-tab:: python PySide6

       import cv2  # type: ignore[import]
       import sys
       from PySide6.QtCore import Qt, QUrl
       from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication
       from PySide6.QtMultimedia import QMediaPlayer
       from araviq6 import (
           ArrayWorker,
           ArrayProcessor,
           NDArrayVideoPlayer,
           NDArrayLabel,
           MediaController,
           get_samples_path,
       )

       class BlurWorker(ArrayWorker):
           def processArray(self, array):
               if array.size != 0:
                   return cv2.GaussianBlur(array, (0, 0), 9)
               return array

       class BlurWidget(QWidget):
           def __init__(self, parent=None):
               super().__init__(parent)
               self.videoPlayer = NDArrayVideoPlayer(self)
               self.arrayProcessor = ArrayProcessor()
               self.arrayLabel = NDArrayLabel()
               self.mediaController = MediaController()

               self.videoPlayer.arrayChanged.connect(self.arrayProcessor.processArray)
               self.arrayProcessor.arrayProcessed.connect(self.arrayLabel.setArray)

               self.arrayProcessor.setWorker(BlurWorker())
               self.mediaController.setPlayer(self.videoPlayer)
               self.arrayLabel.setAlignment(Qt.AlignCenter)

               layout = QVBoxLayout()
               layout.addWidget(self.arrayLabel)
               layout.addWidget(self.mediaController)
               self.setLayout(layout)

           def closeEvent(self, event):
               self.arrayProcessor.stop()
               super().closeEvent(event)

       app = QApplication(sys.argv)
       w = BlurWidget()
       w.videoPlayer.setSource(QUrl.fromLocalFile(get_samples_path('hello.mp4')))
       w.show()
       app.exec()
       app.quit()

.. figure:: ./blurplayer.array.jpg
   :align: center

   Blurring player based on NDArray
