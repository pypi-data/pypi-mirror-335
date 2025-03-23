darca-executor
==============

A secure and structured subprocess command executor for Python projects,
featuring rich logging, customizable execution parameters, and robust
exception handling.


Overview
--------

`darca-executor` wraps Python's `subprocess` with enhanced logging, structured
error reporting, and testability. It is designed to work securely in both
`use_shell=True` and `use_shell=False` modes.

Features
--------

- Shell and non-shell subprocess support
- Built-in timeout, working directory, and environment handling
- Captures stdout/stderr output
- Integrates with custom Darca logging facility
- Raises `DarcaExecError` with detailed metadata on failure
- 100% test coverage with Pytest

Quick Start
-----------

.. code-block:: python

    from darca_executor import DarcaExecutor

    executor = DarcaExecutor(use_shell=False)
    result = executor.run(["echo", "Hello, Darca!"])
    print(result.stdout)

Installation
------------

Install dependencies using `make` and Poetry:

.. code-block:: bash

    make install

Testing
-------

Run all unit tests and generate a coverage report:

.. code-block:: bash

    make test

Documentation
-------------

Build the documentation with:

.. code-block:: bash

    make docs

License
-------

This project is licensed under the MIT License.

Badges
------

.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://opensource.org/licenses/MIT
