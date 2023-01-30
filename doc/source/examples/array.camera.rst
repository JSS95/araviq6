Processing arrays from camera
=============================

This example shows how to run a camera widget using ``ndarray``-based processing pipeline with ``QMediaCaptureSession`` and :class:`.NDArrayLabel`.

.. figure:: ./array.camera.png
   :align: center

   Array-based camera widget with Gaussian blurring process

.. tabs::

   .. tab:: PySide6

      .. include:: ./PySide6/array.camera.py
         :code: python

   .. tab:: PyQt6

      .. include:: ./PyQt6/array.camera.py
         :code: python
