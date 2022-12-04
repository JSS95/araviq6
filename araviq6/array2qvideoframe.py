"""
Array-frame conversion
======================

:mod:`araviq6.array2qvideoframe` provides functions to convert numpy array to
``QVideoFrame``.

To convert ``QVideoFrame`` to numpy array, convert the frame to ``QImage`` by
``QVideoFrame.toImage()`` and use :mod:`qimage2ndarray` package.

.. note::
   This module imitates https://github.com/hmeine/qimage2ndarray.

.. autofunction:: array2qvideoframe

"""

import numpy as np
import numpy.typing as npt
import sys
from qimage2ndarray import _normalize255  # type: ignore[import]
from araviq6.qt_compat import QtCore, QtMultimedia
from typing import Optional, Union, Tuple


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
    array: np.ndarray, normalize: Union[bool, int, Tuple[int, int]] = False
) -> QtMultimedia.QVideoFrame:
    """
    Convert a 2D or 3D numpy array into 32-bit ``QVideoFrame``.

    The dimensions of a 3D array are ``(width, height, channels)``, and the
    channels can be 1, 2, 3 or 4. 2D array with ``(width, height)`` dimension is
    converted to ``(width, height, 1)``.

    Number of the channels is interpreted as follows:

    ========= ===================
    #channels interpretation
    ========= ===================
            1 scalar/gray
            2 scalar/gray + alpha
            3 RGB
            4 RGB + alpha
    ========= ===================

    Note that the scalar data will be converted into gray RGB triples.

    The parameter *normalize* can be used to normalize an frame's value range
    to 0-255.

    If *normalize* = ``(nmin, nmax)``:
        Scale & clip frame values from ``nmin..nmax`` to ``0..255``

    If *normalize* = ``nmax``:
        Lets ``nmin`` default to zero, i.e. scale & clip the range ``0..nmax`` to
        ``0..255``
    If *normalize* = ``True``:
        Scale frame values to ``0..255``, except for boolean arays, where
        ``False`` and ``True`` are mapped to ``0`` and ``255``. Same as passing
        ``(gray.min(), gray.max())``

    If `array` contains masked values, the corresponding pixels will be
    transparent in the result. Thus, the result be of ``Format_BGRA8888`` if the
    input already contains an alhpa channel (i.e., has shape ``(H, W, 4)``) or
    if there are masked pixels, and ``Format_BGRX8888`` otherwise.

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
