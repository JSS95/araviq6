.. _guide-arraypipeline:

===================================
How to build NDArray-based pipeline
===================================

.. currentmodule:: araviq6

In :ref:`guide-processor`, we have built a processor and a pipline based on QVideoFrame.
Now let's learn how to build NDArray-based pipeline.

.. figure:: ../_images/array-pipeline.jpg
   :align: center

   NDArray-based pipeline design

Introduction
------------

Third party packages (e.g., Python binding of machine vision driver) often provide video frames as NDArray.
The user may also need the image processing result to be in numpy array for further tasks.
This is where we need a pipeline with NDArray.

AraViQ6 provides :class:`.ArrayToFrameConverter` and :class:`.FrameToArrayConverter` which converts NDArray to QVideoFrame and vice versa.
Although attaching these classes to QVideoFrame-based pipeline effectively acts as NDArray pipeline, there are several classes which directly handles NDArray.
