# AraViQ6

Python package for converting `QVideoFrame` to `NDArray` with Qt6.

AraViQ is designed to be used with either [PySide6](https://pypi.org/project/PySide6/) or [PyQt6](https://pypi.org/project/PyQt6/).
However, PyQt6 is not available until the dependent package, [qimage2ndarray](https://pypi.org/project/qimage2ndarray/), supports it.

# Installation

Before you install, be careful for other Qt-dependent packages installed in your environment.
For example, non-headless `OpenCV-Python` modifies the Qt dependency thus can make other Qt bindings unavailable.

`araviq6` can be installed using `pip`.

```
$ pip install araviq6
```

# How to use

User can construct a pipeline which converts `QVideoFrame` to `ndarray`, performs any desired processing and displays to the widget.

<div align="center">
  <img src="https://github.com/JSS95/araviq6/raw/master/doc/source/_images/pipeline.png"/><br>
    Video display pipeline
</div>

## `QVideoFrame` to `ndarray`

`QVideoFrame` is acquired from media file (`QMediaPlayer`) or camera capture session (`QMediaCaptureSession`) by setting `QVideoSink` to them and listening to `QVideoSink.videoFrameChanged` signal.

To convert it, pass the video frame `araviq6.FrameToArrayConverter` and listen to `FrameToArrayConverter.arrayChanged` signal.

> (Note) If you want to convert a single `QImage` to `ndarray`, [qimage2ndarray](https://pypi.org/project/qimage2ndarray/) package provides handy functions.

## Displaying `ndarray`

`araviq6.NDArrayLabel` is a widget to directly display `ndarray`.
It can also scale the image with respect to the widget size, and user can select the scaling mode.

## Convenience classes

For convenience, `araviq6` provides `NDArrayVideoPlayer` and `NDArrayMediaCaptureSession` which inherits their Qt6 counterparts and emits `arrayChanged` signal.
`NDArrayVideoPlayerWidget` and `NDArrayCameraWidget` are the minimal implementation to display the video stream with them.

However, time-consuming image processing will block the GUI with these classes because they use a single thread.
To build multithread pipeline, refer to the examples and build the pipeline yourself.

# Examples

Use cases with multithreading are provided in [examples](https://github.com/JSS95/araviq6/tree/master/araviq6/examples) directory.
They can be found in documentation as well.

# Documentation

Documentation can be found on Read the Docs:

> https://araviq6.readthedocs.io/

If you want to build the document yourself, clone the source code and install with `[doc]` option.
Go to `doc` directory and build.

```
$ pip install araviq6[doc]
$ cd doc
$ make html
```

