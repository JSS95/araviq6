Processing arrays from video player
===================================

This example shows how to run the video player with :class:`NDArrayVideoPlayer` and ``ndarray``-based processing pipeline.

.. figure:: ./array.player.png
   :align: center

   Array-based video player widget with Canny edge detection process

.. tabs::

   .. tab:: PySide6

      .. include:: ./PySide6/array.player.py
         :code: python

   .. tab:: PyQt6

      .. include:: ./PyQt6/array.player.py
         :code: python
