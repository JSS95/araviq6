============
Installation
============

This document explains how to install Arabesque6 package.

Making virtual environment
==========================

It is recommended to make a dedicated virtual environment to avoid any possible collision with external libraries with different Qt dependencies.
The easiest way is to use `Anaconda <https://www.anaconda.com/>`_:

.. code-block:: bash

   $ conda create -n my-env pip
   $ conda activate my-env

You are now in a new environment "my-env", with only `pip <https://pip.pypa.io/en/stable/>`_ package installed.
Ready to go!

Downloading the source (Optional)
=================================

You can download full source code of Arabesque6 project without installing it by git.

.. code-block:: bash

   $ git clone git@github.com:JSS95/arabesque6.git

Note that you can download the source with ``pip`` command, but it will install the package at the same time.
It will be explaned in the next section.

Installing
==========

The package can be installed by

.. code-block:: bash

   $ pip install [-e] <PyPI name/url/path>[dependency options]

For example, the following code downloads the latest release from PyPI.

.. code-block:: bash

   $ pip install arabesque6

.. rubric:: install options

There are two types of install options for developers.

* Install with editable option (``-e``)
* Install with dependency specification (``[...]``)

Editable option installs the package as link to the original location.
Change to the source directly reflects to your environment.

Dependency specification installs additional modules which are required to access extra features of the package.
You may add them in brackets right after the package argument.

Available specifications for Arabesque6 are:

* ``test``: installs modules to run tests
* ``test-ci``: installs modules to run tests in headless environment.
* ``doc``: installs modules to build documentations
* ``full``: installs every additional dependency

With commas without trailing whitespaces, i.e. ``[A,B]``, you can pass multiple specifications.

Installing from repository
--------------------------

By passing the vcs url, ``pip`` command automatically clones the source code and installs the package.

.. code-block:: bash

   $ pip install git+ssh://git@github.com/JSS95/arabesque6.git

If you want to pass install options, you need to specify the package name by ``#egg=``.
For example, the following code installs the package with every additional dependency.

.. code-block:: bash

   $ pip install git+ssh://git@github.com/JSS95/arabesque6.git#egg=arabesque6[full]

.. note::

   If you pass ``-e`` option, full source code of the project will be downloaded under ``src/`` directory in your current location.

Installing from source
----------------------

If you have already downloaded the source, you can install it by passing its path to ``pip install``.
For example, in the path where ``setup.py`` is located the following command installs the package in editable mode, with full dependencies.

.. code-block:: bash

   $ pip install -e .[full]
