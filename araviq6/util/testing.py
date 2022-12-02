"""
Testing helpers
===============

:mod:`araviq6.util.testing` provides utilities to help writing unit tests.

"""

import os
import araviq6


__all__ = [
    "get_samples_path",
]


def get_samples_path(*paths: str) -> str:
    """
    Get the absolute path to the directory where the sample data are stored.

    Parameters
    ==========

    paths
        Subpaths under ``araviq6/samples/`` directory.

    Returns
    =======

    path
        Absolute path to the sample depending on the user's system.

    """
    module_path = os.path.abspath(araviq6.__file__)
    module_path = os.path.split(module_path)[0]
    sample_dir = os.path.join(module_path, "samples")
    sample_dir = os.path.normpath(sample_dir)
    sample_dir = os.path.normcase(sample_dir)

    path = os.path.join(sample_dir, *paths)
    return path
