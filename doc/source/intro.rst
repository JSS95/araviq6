.. _intro:

============
Introduction
============

.. currentmodule:: araviq6

AraViQ6 is a Python package which provides NDArray-based video pipeline with Qt6.

Simple video pipeline can be built using AraViQ6, which can be useful to perform image processing on the video with other Python packages.


.. figure:: ./_images/pipeline.png
   :align: center

   Video display pipeline with AraViQ6

Here is a sample which performs `Canny edge detection <https://en.wikipedia.org/wiki/Canny_edge_detector>`_ on the video.
The code can be found in :ref:`examples`.

.. figure:: examples/videoplayer.png
   :align: center

   Video player with canny edge detection.

AraViQ6 also provides convenience classes with pre-built video pipelines.
See :ref:`Reference <reference>` and :ref:`Examples <examples>` pages for more information.

Supported Qt bindings
=====================

AraViQ6 is compatible with the following Qt binding packages:

* `PySide6 <https://pypi.org/project/PySide6/>`_

When AraViQ6 is imported, available package is searched and selected in the order mentioned above.
To force a particular API, set environment variable ``AraViQ_QT_API`` with package name. Letter case does not matter.
