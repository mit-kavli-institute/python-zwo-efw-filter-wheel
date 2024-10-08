# Core dependencies
from ctypes import Structure
import time
from typing import NamedTuple

# Project dependencies
from zwo_efw.wrapper import EFWWrapper


############################################################
#### Data types ############################################
############################################################


class EFWInformation(NamedTuple):
    """Represents the general information of the filter wheel. This is the information
    returned by the `EFWGetProperty` SDK function.
    """

    ID: int
    """The ID of the filter wheel as returned by the EFW SDK library. Note that the ID does not
    always match up to an index with respect to the number of filter wheels. It is simply a
    unique number to an EFW filter wheel.
    """

    Name: str
    """Some name assigned to the filter wheel, which appears to correspond to the model of the
    filter wheel. It isn't clear if this name can be set by a user.
    """

    NumberOfSlots: int
    """The number of filter slots in the filter wheel"""


class EFW:
    """Top-level class for interacting with ZWO EFW filter wheels. This class provides the highest
    level of interaction, so it should be used in almost all cases. The class wraps the official
    ZWO EFW SDK dynamic C library and provides a Python interface to any filter wheel connected to
    the system. This class can manage several filter wheels.
    """

    def __init__(self) -> None:
        self.__efw_wrapper = EFWWrapper()
        self.__filter_wheel_information: list[EFWInformation] = []

    @property
    def filter_wheel_information(self) -> list[EFWInformation]:
        """A list of all the filter wheels' information for filter wheels that were identified when
        the `initialize` method was called.
        """
        return self.__filter_wheel_information

    def initialize(self) -> None:
        number_of_connected_filter_wheels = (
            self.__efw_wrapper.get_number_of_connected_filter_wheels()
        )

        filter_wheel_ids = [
            self.__efw_wrapper.get_filter_wheel_id(i)
            for i in range(number_of_connected_filter_wheels)
        ]

        for filter_wheel_id in filter_wheel_ids:
            self.__efw_wrapper.open_filter_wheel(filter_wheel_id)

        filter_wheel_information_structs: list[Structure] = [
            self.__efw_wrapper.get_filter_wheel_information(filter_wheel_id)
            for filter_wheel_id in filter_wheel_ids
        ]

        # Convert the structs to a pure Python data type
        self.__filter_wheel_information = [
            EFWInformation(
                ID=int(info.ID),
                Name=bytes(info.Name).decode(),
                NumberOfSlots=int(info.slotNum),
            )
            for info in filter_wheel_information_structs
        ]

    def close(self) -> None:
        number_of_connected_filter_wheels = (
            self.__efw_wrapper.get_number_of_connected_filter_wheels()
        )

        filter_wheel_ids = [
            self.__efw_wrapper.get_filter_wheel_id(i)
            for i in range(number_of_connected_filter_wheels)
        ]

        for filter_wheel_id in filter_wheel_ids:
            self.__efw_wrapper.close_filter_wheel(filter_wheel_id)

    def get_position(self, filter_wheel_id: int) -> int | None:
        """Gets the position of the requested filter wheel. If the position returned is `None`,
        then the filter wheel is currently moving. (Note that in such cases, the `is_moving` method
        will return `True`.) Once the filter wheel has reached a set position, the position will be
        returned as a 1-indexed integer corresponding to one of the filter slot numbers labeled on
        the physical filter wheel itself.
        """
        position_index = self.__efw_wrapper.get_position(filter_wheel_id)

        if position_index == -1:
            return None
        else:
            # Note: The filter wheel slots are 1-indexed, while the underlying library positions
            # are 0-indexed. So here, we convert from position index to slow by adding 1.
            return position_index + 1

    def set_position(
        self,
        filter_wheel_id: int,
        slot: int,
        wait_until_done: bool = False,
        timeout_seconds: int = 10,
    ) -> None:
        """Sets the position of the requested filter wheel. The slot should be a 1-indexed integer
        corresponding to the labels on the physical filter wheel itself.
        """
        # Note: The filter wheel slots are 1-indexed, while the underlying library positions
        # are 0-indexed. So here, we convert from slot to position index by subtracting 1.
        self.__efw_wrapper.set_position(filter_wheel_id, slot - 1)

        if wait_until_done:
            start_time = time.monotonic()
            while self.is_moving(filter_wheel_id) == True:
                if time.monotonic() - start_time > timeout_seconds:
                    raise TimeoutError(
                        "ZWO EFW filter wheel ID {filter_wheel_id} did not reach slot {slot} "
                        f"within the requested timeout period of {timeout_seconds} seconds."
                    )

                # Sleep to yield to other threads
                time.sleep(0.100)

    def is_moving(self, filter_wheel_id: int) -> bool:
        return self.get_position(filter_wheel_id) is None
