# AraViQ6 - NDArray from QVideoFrame with Qt6

[![PyPI version](https://badge.fury.io/py/AraViQ6.svg)](https://badge.fury.io/py/AraViQ6)
[![Python Version](https://img.shields.io/pypi/pyversions/araviq6)](https://pypi.org/project/araviq6/)
[![Build Status](https://github.com/JSS95/araviq6/actions/workflows/ci.yml/badge.svg)](https://github.com/JSS95/araviq6/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/araviq6/badge/?version=latest)](https://araviq6.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/github/license/JSS95/araviq6)](https://github.com/JSS95/araviq6/blob/master/LICENSE)

AraViQ6 is a Python package which provides NDArray-based video pipeline with Qt6.

It provides:
- Converter to get NDArray from QVideoFrame
- QLabel to display image from NDArray
- Convenience classes and widgets with pre-built video pipelines

The following Qt bindings are supported:
- [PySide6](https://pypi.org/project/PySide6/)

# How to use

There are two ways to use AraViQ6; build the video pipeline yourself, or use the convenience classes with pre-built pipelines.

## Building the pipeline

Qt's `QVideoSink` class emits `QVideoFrame` from the video file or the camera.
Connect the signals to build a pipeline which consists of:
1. `FrameToArrayConverter`, which converts `QVideoFrame` to `ndarray`.
2. Any array processing, if required.
3. `NDArrayLabel` which displays `ndarray` on the screen.

<div align="center">
  <img src="https://github.com/JSS95/araviq6/raw/master/doc/source/_images/pipeline.png"/><br>
    Video display pipeline with AraViQ6
</div>

Note that you may want to run the processing in separate thread to avoid blocking the GUI thread.
See Examples to learn how to construct a multithreaded pipeline.

## Convenicence classes

The following classes have internal video sink and converter to emit `ndarray` from the video.
- `NDArrayVideoPlayer`
- `NDArrayMediaCaptureSession`

The following widgets implements full video streaming from source to display, albeit the array cannot be processed.
- `NDArrayVideoPlayerWidget`
- `NDArrayCameraWidget`

# Examples

Use cases are provided in [examples](https://github.com/JSS95/araviq6/tree/master/araviq6/examples) directory.
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
