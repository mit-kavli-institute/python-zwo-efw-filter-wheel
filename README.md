# ZWO EFW filter wheel library

This is a Python library for interacting with a ZWO EFW filter wheel over USB. The EFW family of filter wheels can only be communicated to via USB, and so this library wraps the official ZWO EFW dynamic library (`.dll` on Windows and `.so` on macOS and Linux) with Python's foreign-function interface, using the [built-in `ctypes`](https://docs.python.org/3/library/ctypes.html) library. From there, it exposes a clean interface for interacting with the filter wheel in Python that requires no underlying knowledge of the EFW's dynamic library wrapping and USB communication.

The library is configured as a Poetry library and can be pulled in directly from the GitHub repository by running the following command:

```console
poetry add git+https://github.com/mit-kavli-institute/python-zwo-efw-filter-wheel.git#main
```

This pulls in the latest revision from the `main` branch. See the [Poetry docs for adding a library](https://python-poetry.org/docs/cli/#add) for more information. The library is not currently published to a Python package server.
