"""
Data path
=========

:mod:`araviq6.util.path` provides access to data files at
runtime.

"""
from importlib_resources import files


__all__ = [
    "get_data_path",
    "get_samples_path",
]


def get_data_path(*paths: str) -> str:
    """
    Get path to data file.

    Parameters
    ----------
    paths : str
        Subpaths under ``araviq6/data/`` directory.

    Returns
    -------
    path
        Absolute path to the data.

    Examples
    ========

    >>> from araviq6 import get_data_path
    >>> get_data_path() # doctest: +SKIP
    'path/araviq6/data'
    >>> get_data_path("hello.jpg") # doctest: +SKIP
    'path/araviq6/data/hello.jpg'

    """
    data_path = files("araviq6.data")
    if not paths:
        return str(data_path._paths[0])
    return str(data_path.joinpath(*paths))


# backwards compatibility
get_samples_path = get_data_path
