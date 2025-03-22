|pypi| |pyver|

hcli_problem_details
====================

A Python library providing RFC 9457 compliant problem detail exceptions for HCLI applications and other Python projects.

----

This package delivers a complete set of HTTP problem detail exceptions adhering to RFC 9457 (Problem Details for HTTP APIs). Built as part of the HCLI ecosystem, it offers reusable exception classes for HTTP 4xx and 5xx status codes, simplifying standardized error handling in HCLI applications and other Python projects. Each exception can be transformed into an RFC 9457 compliant problem detail dictionary for consistent API error responses.

Learn more about HCLI at hcli.io [1].

Help shape this library and the HCLI ecosystem by raising issues on GitHub!

[1] http://hcli.io

Related HCLI Projects
---------------------

- **huckle**: A generic HCLI client for interacting with HCLI applications. [2]
- **hcli_core**: An HCLI Connector exposing a REST API as a CLI via HCLI semantics. [3]

[2] https://github.com/cometaj2/huckle
[3] https://github.com/cometaj2/hcli_core

Installation
------------

hcli_problem_details requires a supported version of Python and pip.

.. code-block:: console

    pip install hcli-problem-details

Usage
-----

Import and raise exceptions in your Python application as needed. Each exception generates an RFC 9457 compliant problem detail representation.

.. code-block:: python

    from hcli_problem_details import NotFoundError, BadRequestError

    # Raise a 404 Not Found error
    raise NotFoundError(detail="Resource not found")
    # Output: {"type": "about:blank", "title": "Not Found", "status": 404, "detail": "Resource not found"}

    # Raise a 400 Bad Request error with custom extensions
    raise BadRequestError(detail="Invalid input", extensions={"field": "username"})
    # Output: {"type": "about:blank", "title": "Bad Request", "status": 400, "detail": "Invalid input", "field": "username"}

Integration with HCLI Core
--------------------------

HCLI Core utilizes this package to automatically recognize and relay its raised exceptions to HCLI clients (e.g., huckle) as problem details.

Versioning
----------

This project follows semantic versioning (http://semver.org). Development releases may use "devx", "prealphax", "alphax", "betax", or "rcx" extensions (e.g., 0.1.0-prealpha1) on GitHub. Only full major.minor.patch releases are published to PyPI.

Supports
--------

- Full coverage of HTTP 4xx client errors and 5xx server errors as exception classes.
- RFC 9457 problem detail structure with `type`, `title`, `status`, `detail`, `instance`, and extensible `extensions`.
- Compatibility with HCLI Core and any Python project requiring standardized HTTP error handling.

To Do
-----

- Add automated tests for all exception classes.
- Provide integration examples for common web frameworks (e.g., Flask, FastAPI, Falcon).
- Document advanced usage of extensions for custom problem details.

Bugs
----

- No known issues.

.. |pypi| image:: https://img.shields.io/pypi/v/hcli_problem_details?label=hcli_problem_details
   :target: https://pypi.org/project/hcli_problem_details
.. |pyver| image:: https://img.shields.io/pypi/pyversions/hcli_problem_details.svg
   :target: https://pypi.org/project/hcli_problem_details
