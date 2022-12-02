"""
Array label
===========

:mod:`araviq6.labels` provides ``QLabel`` subclasses to display numpy array.

.. autoclass:: ScalableQLabel
   :members:

.. autoclass:: NDArrayLabel
   :members:

"""

import enum
import numpy as np
import qimage2ndarray  # type: ignore[import]
from araviq6.qt_compat import QtCore, QtGui, QtWidgets

__all__ = [
    "ScalableQLabel",
    "NDArrayLabel",
]


# Monkeypatch qimage2ndarray until new version (> 1.9.0)
# https://github.com/hmeine/qimage2ndarray/issues/29
for name, qimage_format in qimage2ndarray.qimageview_python.FORMATS.items():
    if name in dir(QtGui.QImage.Format):
        qimage_format.code = getattr(QtGui.QImage, name)


class ScalableQLabel(QtWidgets.QLabel):
    """
    A label which can scale the pixmap before displaying.

    Pixmap can be downscaled or upscaled to fit to the label size, depending on
    :meth:`pixmapScaleMode`.

    :meth:`setPixmap` scales the input pixmap and update to label.
    :meth:`originalPixmap` returns current unscaled pixmap.

    Notes
    =====

    Do not modify the size policy and minimum size value. Changing them makes the
    label not shrinkable.

    """

    class PixmapScaleMode(enum.Enum):
        """
        This enum defines how the pixmap is scaled before being displayed.

        Attributes
        ==========

        PM_NoScale
            Pixmap is never scaled. If the label size is smaller than the pixmap
            size, only a part of the pixmap is displayed.

        PM_DownScaleOnly
            Pixmap is scaled, but never larger than its original size.

        PM_UpScaleOnly
            Pixmap is scaled, but never smaller than its original size.

        PM_AllScale
            Pixmap is scaled to any size.

        """

        PM_NoScale = 0
        PM_DownScaleOnly = 1
        PM_UpScaleOnly = 2
        PM_AllScale = 3

    PM_NoScale = PixmapScaleMode.PM_NoScale
    PM_DownScaleOnly = PixmapScaleMode.PM_DownScaleOnly
    PM_UpScaleOnly = PixmapScaleMode.PM_UpScaleOnly
    PM_AllScale = PixmapScaleMode.PM_AllScale

    def __init__(self, parent=None):
        super().__init__(parent)

        self._original_pixmap = QtGui.QPixmap()
        self._pixmapScaleMode = self.PM_DownScaleOnly
        # make label shrinkable
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.setMinimumSize(1, 1)  # (0, 0) prevents resizing

    def originalPixmap(self) -> QtGui.QPixmap:
        """Original pixmap before scaling."""
        return self._original_pixmap

    def pixmapScaleMode(self) -> PixmapScaleMode:
        """Mode to scale the pixmap. Default is :attr:`PM_DownScaleOnly`."""
        return self._pixmapScaleMode

    @QtCore.Slot(PixmapScaleMode)
    def setPixmapScaleMode(self, flag: PixmapScaleMode):
        """Set :meth:`pixmapScaleMode` to *flag* and update the label."""
        self._pixmapScaleMode = flag
        self.update()

    @QtCore.Slot(QtGui.QPixmap)
    def setPixmap(self, pixmap: QtGui.QPixmap):
        """Scale the pixmap and display."""
        self._original_pixmap = pixmap

        mode = self.pixmapScaleMode()
        if mode == self.PM_NoScale:
            flag = False
        else:
            w, h = pixmap.width(), pixmap.height()
            new_w = self.width()
            new_h = self.height()
            if mode == self.PM_DownScaleOnly:
                flag = new_w < w or new_h < h
            elif mode == self.PM_UpScaleOnly:
                flag = new_w > w or new_h > h
            elif mode == self.PM_AllScale:
                flag = True
            else:
                msg = "Unrecognized pixmap scale mode: %s" % mode
                raise TypeError(msg)

        if flag:
            pixmap = pixmap.scaled(new_w, new_h, QtCore.Qt.KeepAspectRatio)

        super().setPixmap(pixmap)

    def paintEvent(self, event):
        super().paintEvent(event)
        self.setPixmap(self.originalPixmap())


class NDArrayLabel(ScalableQLabel):
    """
    Scalable label which can receive and display :class:`numpy.ndarray` image.
    Image array can be set by :meth:`setArray`.

    Examples
    ========

    >>> import cv2
    >>> from PySide6.QtWidgets import QApplication
    >>> import sys
    >>> from araviq6 import NDArrayLabel, get_samples_path
    >>> img = cv2.imread(get_samples_path('hello.jpg'))
    >>> def runGUI():
    ...     app = QApplication(sys.argv)
    ...     label = NDArrayLabel()
    ...     label.setArray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    ...     label.show()
    ...     app.exec()
    ...     app.quit()
    >>> runGUI()  # doctest: +SKIP

    """

    @QtCore.Slot(np.ndarray)
    def setArray(self, array: np.ndarray):
        """
        Convert the array to pixmap using :func:`qimage2ndarray.array2qimage`,
        and display.
        """
        if array.size > 0:
            pixmap = QtGui.QPixmap.fromImage(qimage2ndarray.array2qimage(array))
        else:
            pixmap = QtGui.QPixmap()
        self.setPixmap(pixmap)
