# ZWO EFW filter wheel library

This is a Python library for interacting with a ZWO EFW filter wheel over USB. The EFW family of filter wheels can only be communicated to via USB, and so this library wraps the official ZWO EFW dynamic library (`.dll` on Windows and `.so` on macOS and Linux) with Python's foreign-function interface, using the [built-in `ctypes`](https://docs.python.org/3/library/ctypes.html) library. From there, it exposes a clean interface for interacting with the filter wheel in Python that requires no underlying knowledge of the EFW's dynamic library wrapping and USB communication. For an example of how to use the library, see the [Example use](#example-use) section.

The library is configured as a Poetry library and can be pulled in directly from the GitHub repository by running the following command:

```console
poetry add git+https://github.com/mit-kavli-institute/python-zwo-efw-filter-wheel.git#main
```

This pulls in the latest revision from the `main` branch. See the [Poetry docs for adding a library](https://python-poetry.org/docs/cli/#add) for more information. The library is not currently published to a Python package server.

## Example use

The following is a shortened example, in order to highlight just the main library interface, from the more complete [`example.py` script](./zwo_efw/scripts/example.py).

```python
import time
from zwo_efw import EFW, EFWInformation

efw = EFW()

try:
    # Initialize communication to any EFW filter wheels that are connected
    efw.initialize()

    # Get the information for all the filter wheels that were identified
    filter_wheel_information: list[EFWInformation] = efw.filter_wheel_information

    # Get the first available filter wheel
    filter_wheel: EFWInformation = filter_wheel_information[0]

    # Cycle through all the slots in the filter wheel once
    for current_slot in range(1, filter_wheel.NumberOfSlots + 1):
        efw.move(filter_wheel.ID, current_slot)

        # Wait until the filter wheel has finished moving to the commanded slot
        while efw.is_moving(filter_wheel.ID):
            time.sleep(0.5)

        # Wait 1 second before the next move
        time.sleep(1)

finally:
    efw.close()
```

## Dependencies

### Windows

There are no additional dependencies needed on Windows.

### Linux

On Linux, the `libudev` library must be installed. For Ubuntu, this can be installed via:

```console
sudo apt-get install libudev-dev -y
```

For other distributions, you will need to find the package that needs to be installed to make the `libudev.so` library be available on the system `$PATH`.

### macOS

Unknown at this time. File an issue if you find that there are missing dependencies that need to be loaded or if just to report that the library works fine on macOS.

## Supported operating systems and platforms

In general, this library is intended to support every operating system and platform that the ZWO EFW SDK supports. However, there are limitations in the amount of platforms that can be easily tested since virtual machines and Docker containers are not enough since we need to be able to test the OS and platform against a real filter wheel. Also, some platforms, namely Linux, are incredibly difficult to test across the various permutations. So, the table below lists off the platforms that this library has been tested against. The table does not exhaustively list all platforms that are intended to be supported.

| OS         | Platform      | Intention to support | Tested             |
| ---------- | ------------- | -------------------- | ------------------ |
| Windows 11 | 64-bit x86    | :heavy_check_mark:   | :heavy_check_mark: |
| macOS      | Apple silicon | :heavy_check_mark:   | :x:                |
| macOS      | x86           | :x:                  | -                  |
| Ubuntu     | 64-bit x86    | :heavy_check_mark:   | :heavy_check_mark: |

If you are encountering issues with a platform that is supported by the ZWO EFW SDK, then please file a GitHub issue. In that issue, please provide what the function `debug_efw_sdk_library_loading` in the `zwo_efw.debug` module prints out to the console. This will help more quickly narrow down the source of the issue.
