============
Installation
============

This document explains how to install AraViQ6.

If you just want quick installation, run the following command and forget about the rest of this document.

.. code-block:: bash

   $ pip install araviq6

This will install ``araviq6`` package in your environment.

Developers are encouraged to :ref:`download the source <download-source>` and :ref:`install from the source <install-from-source>`.

Downloading the source (Optional)
=================================

.. _download-source:

You can download full source code of AraViQ6 project from its repository.

.. code-block:: bash

   $ git clone git@github.com:JSS95/araviq6.git

Installing
==========

The package can be installed by

.. code-block:: bash

   $ pip install [-e] <PyPI name/url/path>[dependency options]

.. rubric:: Install options

.. _install-options:

There are two noticeable install options for developers.

* Install with editable option (``-e``)
* Install with optional dependencies (``[...]``)

The editable option allows changes made to the source code to be immediately reflected in the installed package.
For more information, refer to `pip documentation <https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs>`_.

Optional dependencies can be specified by adding them into brackets right after the package url/path.
When specified, additional module are installed to help accessing extra features of the package.

In AraViQ6, all optional dependencies are for package development.
Available specifications are:

* ``test``: installs modules to run tests.
* ``doc``: installs modules to build documentations.
* ``dev``: installs every additional dependency for developers.

With commas without trailing whitespaces, i.e. ``[A,B]``, you can pass multiple specifications.

Installing from repository
--------------------------

By passing the vcs url, ``pip`` command automatically clones the source code and installs the package.

.. code-block:: bash

   $ pip install git+ssh://git@github.com/JSS95/araviq6.git

If you want to pass install options, you need to specify the package name by ``#egg=``.
For example, the following code installs the package with development dependencies.

.. code-block:: bash

   $ pip install git+ssh://git@github.com/JSS95/araviq6.git#egg=araviq6[full]

.. note::

   If you pass ``-e`` option, source code of the project will be downloaded in your current location.

Installing from source
----------------------

.. _install-from-source:

If you have already downloaded the source, you can install it by passing its path to ``pip install``.
For example, in the path where ``pyproject.toml`` is located, the following command installs the package in editable mode, with full dependencies for developers.

.. code-block:: bash

   $ pip install -e .[dev]

Installing Qt binding
=====================

AraViQ6 needs Qt binding package installed in the environment, but it does not specify it as requirement.
Install any one of the supported Qt binding listed in :ref:`intro` before using AraViQ6.
