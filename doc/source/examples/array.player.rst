Processing arrays from video player
===================================

This example shows how to run a video player widget using ``ndarray``-based processing pipeline with :class:`.NDArrayVideoPlayer` and :class:`.NDArrayLabel`.

.. figure:: ./array.player.jpg
   :align: center

   Array-based video player widget with Canny edge detection process

.. tabs::

   .. tab:: PySide6

      .. include:: ./PySide6/array.player.py
         :code: python

   .. tab:: PyQt6

      .. include:: ./PyQt6/array.player.py
         :code: python
