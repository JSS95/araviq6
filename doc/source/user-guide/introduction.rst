============
Introduction
============

.. currentmodule:: arabesque6

.. figure:: ../_images/pipeline.png
   :align: center

   Video display pipeline with Arabesque6

Arabesque6 is a Python package which converts :class:`PySide6.QVideoFrame` to :class:`numpy.ndarray` and displays it on GUI.
This task is very common in scientific visualizing, especially in the field of image analysis.

:class:`.FrameToArrayConverter` converts the video frame to numpy array.
After any desired processing is done, the resulting array can be passed to :class:`.NDArrayLabel` to be displayed.
:class:`.NDArrayVideoPlayerWidget` and :class:`.NDArrayCameraWidget` are convenience classes with pre-built pipelines.

For more information, see :ref:`Reference <reference>` and :ref:`Examples <examples>` pages.
