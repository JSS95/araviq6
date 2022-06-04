"""
General utilities
=================

"""

import arabesque6
import os


__all__ = [
    "get_data_path",
]


def get_data_path(*paths: str) -> str:
    """
    Get the absolute path to the directory where the sample data are stored.

    Parameters
    ==========

    paths
        Subpaths under ``arabesque6/data/`` directory.

    Returns
    =======

    path
        Absolute path to the sample depending on the user's system.

    """
    module_path = os.path.abspath(arabesque6.__file__)
    module_path = os.path.split(module_path)[0]
    sample_dir = os.path.join(module_path, "data")
    sample_dir = os.path.normpath(sample_dir)
    sample_dir = os.path.normcase(sample_dir)

    path = os.path.join(sample_dir, *paths)
    return path
