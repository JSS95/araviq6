"""
Arabesque6: NDArray - QVideoFrame Converter for Qt6
===================================================

Arabesque6 is a package to get :class:`numpy.ndarray` from ``QVideoFrame`` with
Qt6 Python bindings - :mod:`PyQt6` and :mod:`PySide6`.

"""

from .version import __version__  # noqa

from .labels import ScalableQLabel, NDArrayLabel


__all__ = [
    "ScalableQLabel",
    "NDArrayLabel",
]
