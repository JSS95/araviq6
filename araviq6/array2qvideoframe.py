"""
Array-frame converter
=====================

:mod:`araviq6.array2qvideoframe` provides functions to convert the ndarray to
QVideoFrame and vice versa.

.. note::
   This module imitates https://github.com/hmeine/qimage2ndarray.

Frame -> Array
--------------

.. autofunction:: byte_view

.. autofunction:: rgb_view

.. autofunction:: alpha_view

Array -> Frame
--------------

.. autofunction:: array2qvideoframe

"""

import numpy as np
import numpy.typing as npt
import sys
from qimage2ndarray import _normalize255  # type: ignore[import]
from araviq6.qt_compat import QtCore, QtMultimedia
from typing import Optional


__all__ = [
    "array2qvideoframe",
]


class ArrayInterfaceAroundQVideoFrame(object):
    __slots__ = ("__qvideoframe", "__array_interface__")

    def __init__(self, frame: QtMultimedia.QVideoFrame, bytes_per_pixel: int):
        self.__qvideoframe = frame

        self.__array_interface__ = dict(
            shape=(frame.height(), frame.width()),
            typestr="|u%d" % bytes_per_pixel,
            data=frame.bits(0),
            strides=(frame.bytesPerLine(0), bytes_per_pixel),
            version=3,
        )


def qvideoframeview(frame: QtMultimedia.QVideoFrame) -> np.ndarray:
    pixelFormat = frame.surfaceFormat().pixelFormat()
    if pixelFormat == QtMultimedia.QVideoFrameFormat.Format_BGRA8888:
        bits = 32
    elif pixelFormat == QtMultimedia.QVideoFrameFormat.Format_BGRX8888:
        bits = 32
    else:
        raise TypeError(f"Invalid pixel format: {pixelFormat}")
    interface = ArrayInterfaceAroundQVideoFrame(frame, bits // 8)
    return np.asarray(interface)


def byte_view(
    frame: QtMultimedia.QVideoFrame, byteorder: Optional[str] = "little"
) -> npt.NDArray[np.uint8]:
    raw = qvideoframeview(frame)
    result = raw.view(np.uint8).reshape(raw.shape + (-1,))
    if byteorder is not None and byteorder != sys.byteorder:
        result = result[..., ::-1]
    return result


def rgb_view(
    frame: QtMultimedia.QVideoFrame, byteorder: Optional[str] = "big"
) -> npt.NDArray[np.uint8]:
    if byteorder is None:
        byteorder = sys.byteorder
    bytes = byte_view(frame, byteorder)

    if byteorder == "little":
        result = bytes[..., :3]  # strip A off BGRA
    else:
        result = bytes[..., 1:]  # strip A off ARGB
    return result


def alpha_view(frame: QtMultimedia.QVideoFrame) -> npt.NDArray[np.uint8]:
    bytes = byte_view(frame, byteorder=None)
    if sys.byteorder == "little":
        ret = bytes[..., 3]
    else:
        ret = bytes[..., 0]
    return ret


def array2qvideoframe(
    array: np.ndarray, normalize: bool = False
) -> QtMultimedia.QVideoFrame:
    """
    Convert a 2D or 3D numpy array into ``QVideoFrame``.
    """
    dim = np.ndim(array)
    if dim == 2:
        array = array[..., None]
    elif dim != 3:
        raise ValueError(
            f"invalid number of dimensions for array2qvideoframe (got {dim} dimensions)"
        )

    h, w, ch = array.shape
    if ch not in (1, 2, 3, 4):
        raise ValueError(
            f"invalid number of channels for array2qvideoframe: (got {ch} channels)"
        )

    hasAlpha = np.ma.is_masked(array) or ch in (2, 4)
    if hasAlpha:
        pixelFormat = QtMultimedia.QVideoFrameFormat.Format_BGRA8888
    else:
        pixelFormat = QtMultimedia.QVideoFrameFormat.Format_BGRX8888
    frameFormat = QtMultimedia.QVideoFrameFormat(QtCore.QSize(w, h), pixelFormat)
    frame = QtMultimedia.QVideoFrame(frameFormat)

    frame.map(QtMultimedia.QVideoFrame.MapMode.WriteOnly)

    array = _normalize255(array, normalize)
    rgb = rgb_view(frame)
    if ch >= 3:
        rgb[:] = array[..., :3]
    else:
        rgb[:] = array[..., :1]  # scalar data

    alpha = alpha_view(frame)
    if ch in (2, 4):
        alpha[:] = array[..., -1]
    else:
        alpha[:] = 255
    if np.ma.is_masked(array):
        alpha[:] *= np.logical_not(
            np.any(array.mask, axis=-1)  # type: ignore[attr-defined]
        )

    frame.unmap()  # save the modified memory to frame instance

    return frame
