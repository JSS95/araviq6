# AraViQ6 - NDArray-based Video processing with Qt6

[![PyPI version](https://badge.fury.io/py/AraViQ6.svg)](https://badge.fury.io/py/AraViQ6)
[![Python Version](https://img.shields.io/pypi/pyversions/araviq6)](https://pypi.org/project/araviq6/)
[![Build Status](https://github.com/JSS95/araviq6/actions/workflows/ci.yml/badge.svg)](https://github.com/JSS95/araviq6/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/araviq6/badge/?version=latest)](https://araviq6.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/github/license/JSS95/araviq6)](https://github.com/JSS95/araviq6/blob/master/LICENSE)

AraViQ6 is a Python package which integrates NDArray-based image processing with video pipeline of Qt6.

It provides:
- QVideoFrame processor based on array processing
- Converters between NDArray and QVideoFrame
- Convenience classes and widgets for array displaying

The following Qt bindings are supported:
- [PySide6](https://pypi.org/project/PySide6/)
- [PyQt6](https://pypi.org/project/PyQt6/)

# How to use

There are two ways to use AraViQ6; using QVideoFrame-based pipeline, or using NDArray-based pipeline.

## Frame-based pipeline

Frame-based pipeline is a high-level approach that works well with Qt Multimedia scheme.

<div align="center">
  <img src="https://github.com/JSS95/araviq6/raw/master/doc/source/_images/frame-pipeline.jpg"/><br>
    QVideoFrame pipeline with AraViQ6
</div>

Frame-based pipeline consists of:
1. `VideoFrameWorker`
2. `VideoFrameProcessor`

QVideoFrame comes from and goes to Qt6's `QVideoSink`. AraViQ6's
`VideoFrameWorker` converts QVideoFrame to numpy array, performs processing, and sends the results to downstream in both QVideoFrame and NDArray. User may subclass the worker to define own processing.

`VideoFrameProcessor` wraps the worker and provides API around it.
Worker is mulithreaded in the processor.

## Array-based pipeline

Array-based pipeline is a low-level approach.
It can be useful when third-party package provides video frame in numpy array format.

<div align="center">
  <img src="https://github.com/JSS95/araviq6/raw/master/doc/source/_images/array-pipeline.jpg"/><br>
    NDArray pipeline with AraViQ6
</div>

Array-based pipeline consists of:

1. `FrameToArrayConverter`
2. `ArrayWorker`
3. `ArrayProcessor`
4. `ArrayToFrameConverter`

`FrameToArrayConverter` and `ArrayToFrameConverter` performs conversion between frame pipeline and array pipeline.
To retain the metadata (e.g., timestamp) of QVideoFrame, these classes includes the original frame for the array.

`ArrayWorker` performs processing on incoming array and sends the result to downstream in NDArray. User may subclass the worker to define own processing.

`ArrayProcessor` wraps the worker and provides API around it.
Worker is mulithreaded in the processor.

## Convenicence classes

AraViQ6 also provides various convenience classes to make building the pipeline easier.

The following classes help setting array pipeline with the video source and the display.
- `NDArrayVideoPlayer`
- `NDArrayMediaCaptureSession`
- `NDArrayLabel`

The following classes are plug-and-play widgets where user can process the video with minimal boilerplate.
- `PlayerProcessWidget`
- `CameraProcessWidget`

# Examples

Use cases are provided in [examples](https://github.com/JSS95/araviq6/tree/master/doc/source/examples) directory.
They can be found in documentation as well.

# Installation

Before you install, be careful for other Qt-dependent packages installed in your environment.
For example, non-headless OpenCV-Python modifies the Qt dependency thus can make other Qt bindings unavailable.

`araviq6` can be installed using `pip`.

```
$ pip install araviq6
```

# Documentation

AraViQ6 is documented with [Sphinx](https://pypi.org/project/Sphinx/).
Documentation can be found on Read the Docs:

> https://araviq6.readthedocs.io/

If you want to build the document yourself, clone the source code and install with `[doc]` option.
Go to `doc` directory and build the document.

```
$ pip install araviq6[doc]
$ cd doc
$ make html
```

Document will be generated in `build/html` directory. Open `index.html` to see the central page.
