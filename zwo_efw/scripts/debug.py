# Core dependencies
from pathlib import Path
import platform

# Project dependencies
from zwo_efw.bindings import _get_library_path, load_zwo_efw_library
from zwo_efw.utilities import get_operating_system, get_platform_bitness


def debug_efw_sdk_library_loading() -> None:
    """A debug function for users and developers to see all the relevant information
    for the platform they are trying to use this library on. The information is printed
    out to the console.
    """
    operating_system = get_operating_system()
    bitness = get_platform_bitness()
    library_path = _get_library_path()
    bindings_file_path = Path(__file__).resolve()

    # Test to see if there's an exception when loading the EFW SDK library
    exception_during_loading = None
    try:
        load_zwo_efw_library()
    except Exception as exception:
        exception_during_loading = exception

    print(
        f"""
        ****************************************************
        ********** Resolved platform information ***********
        ****************************************************
        Operating system: {operating_system}
        Bitness: {bitness}

        ****************************************************
        ********** Raw platform information ****************
        ****************************************************
        Platform: {platform.platform()}
        Architecture: {platform.architecture()}
        Processor: {platform.processor()}
        Machine: {platform.machine()}

        ****************************************************
        ********** Python information **********************
        ****************************************************
        Python version: {platform.python_version()}
        Python implementation: {platform.python_implementation()}

        ****************************************************
        ********** EFW SDK library information *************
        ****************************************************
        ZWO EFW SDK library path: {library_path}
        bindings.py file path: {bindings_file_path}
        Exception when loading: {exception_during_loading}
        ****************************************************
        """
    )
