.. _intro:

============
Introduction
============

.. currentmodule:: araviq6

AraViQ6 is a Python package which integrates NDArray-based image processing with video pipeline of Qt6.

Using AraViQ6, QVideoFrame can be processed with simple pipeline.
This is useful with the video supported by Qt Multimedia scheme.

.. figure:: ./_images/frame-pipeline.jpg
   :align: center

   QVideoFrame pipeline with AraViQ6

In third-party packages, video stream can be provided directly in NDArray instead of QVideoFrame.
AraViQ supports low-level pipeline and convenience classes to handle NDArray.

.. figure:: ./_images/array-pipeline.jpg
   :align: center

   NDArray pipeline with AraViQ6

Here is a sample which performs `Canny edge detection <https://en.wikipedia.org/wiki/Canny_edge_detector>`_ on the video.
The code can be found in :ref:`examples`.

.. figure:: examples/videoplayer.png
   :align: center

   Video player with canny edge detection.

Supported Qt bindings
=====================

AraViQ6 is compatible with the following Qt binding packages:

* `PySide6 <https://pypi.org/project/PySide6/>`_

When AraViQ6 is imported, available package is searched and selected in the order mentioned above.
To force a particular API, set environment variable ``ARAVIQ_QT_API`` with package name. Letter case does not matter.
