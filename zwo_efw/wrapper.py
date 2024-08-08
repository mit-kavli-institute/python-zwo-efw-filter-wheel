# Core dependencies
from ctypes import *

# Project dependencies
from zwo_efw.bindings import load_zwo_efw_library, EFW_ERROR_CODE, EFW_INFO


############################################################
#### Exceptions ############################################
############################################################


class FilterWheelError(Exception):
    """A custom exception that wraps the EFW error code that is returned by the communication
    library
    """

    def __init__(self, efw_error_code: EFW_ERROR_CODE):
        super().__init__(
            "An error occurred while communicating with the ZWO EFW filter wheel. "
            f"Error code: {efw_error_code.name}"
        )


############################################################
#### Helper functions ######################################
############################################################


def _handle_function_result(result: EFW_ERROR_CODE) -> None:
    """Processes the result of a function call to the ZWO EFW SDK library when the return type is
    `EFW_ERROR_CODE`. If the result is `EFW_SUCCESS`, then the function call was successful and
    this function becomes just a pass-through by returning none. If any other error code is found,
    then a `FilterWheelError` exception is raised with the error code included in the message.
    """

    match result:
        case EFW_ERROR_CODE.EFW_SUCCESS:
            return None

        case _:
            raise FilterWheelError(result)


############################################################
#### Python wrapper of the low-level library bindings ######
############################################################


class EFWWrapper:
    """A Python wrapper around the ZWO EFW SDK C dynamic library. This class provides a
    higher-level interface to the filter wheel, and its methods map one to one to the available
    library functions. The main difference is that the details of how data is passed to and from
    and converted between Python and the C library are handled by this wrapper class.
    """

    def __init__(self):
        self.__efw_library = load_zwo_efw_library()

    def get_number_of_connected_filter_wheels(self) -> int:
        """Gets the number of connected filter wheels. This should always be the first thing called
        in a session using the EFW library.
        """
        return self.__efw_library.EFWGetNum()

    # Note: This function doesn't appear to actually be available in the EFW SDK library
    # def get_product_ids(self) -> list[int]:
    #     product_ids_pointer = None
    #     array_length = self.__efw_library.EFWGetProductIds(product_ids_pointer)
    #     return product_ids_pointer.contents

    def get_filter_wheel_id(self, filter_wheel_index: int) -> int:
        """Given the filter wheel's index as returned by `get_number_of_connected_filter_wheels`,
        returns the filter wheel's unique ID. This ID is what must be used to communicate with the
        filter wheel, so this should be the second method called after getting the number of
        connected filter wheels.
        """
        id = c_int()
        result = self.__efw_library.EFWGetID(filter_wheel_index, id)
        _handle_function_result(result)
        return id.value

    def open_filter_wheel(self, filter_wheel_id: int) -> None:
        """Opens up communication to a specific filter wheel"""
        result = self.__efw_library.EFWOpen(filter_wheel_id)
        _handle_function_result(result)

    def close_filter_wheel(self, filter_wheel_id: int) -> None:
        """Closes communication to a specific filter wheel"""
        result = self.__efw_library.EFWClose(filter_wheel_id)
        _handle_function_result(result)

    def get_filter_wheel_information(self, filter_wheel_id: int) -> EFW_INFO:
        """Gets information about a specific filter wheel. This should be called after opening
        communication to the filter wheel.
        """
        information = pointer(EFW_INFO(0, b"", 0))
        result = self.__efw_library.EFWGetProperty(filter_wheel_id, information)
        _handle_function_result(result)
        return information.contents

    def get_position(self, filter_wheel_id: int) -> int:
        """Gets the current position of the filter wheel. This is a zero-based index of the
        position, whereas the actual filter wheel slots are 1-based indexed, as written on
        the filter wheel itself.
        """
        position = c_int()
        result = self.__efw_library.EFWGetPosition(filter_wheel_id, position)
        _handle_function_result(result)
        return position.value

    def set_position(self, filter_wheel_id: int, position: int) -> None:
        """Sets the filter wheel to a specific position. This is a zero-based index of the
        position, whereas the actual filter wheel slots are 1-based indexed, as written on
        the filter wheel itself.
        """
        result = self.__efw_library.EFWSetPosition(filter_wheel_id, position)
        _handle_function_result(result)
