# Core dependencies
from ctypes import *
from enum import IntEnum, auto, verify, UNIQUE
from pathlib import Path

# Project dependencies
from zwo_efw.utilities import Bitness, Platform, get_platform_bitness, get_platform


############################################################
#### Constants #############################################
############################################################


SDK_VERSION = "1.7"


############################################################
#### Helper functions ######################################
############################################################


def _get_library_path() -> str:
    """Gets the path to the EFW filter wheel dynamic library. This function handles the differences
    in library paths between the various operating systems and their bitnesses.
    """

    base_sdk_path = Path(__file__).resolve().parent / "efw_sdk" / "EFW_SDK"

    platform = get_platform()
    bitness = get_platform_bitness()

    match platform:
        case Platform.WINDOWS:
            bitness_string = "64" if bitness == Bitness.BITS_64 else "32"

            return (
                base_sdk_path
                / f"EFW_Windows_SDK_V{SDK_VERSION}"
                / "EFW SDK"
                / "lib"
                / f"Win{bitness_string}"
                / "EFW_filter.dll"
            )

        case Platform.LINUX:
            bitness_string = "x64" if bitness == Bitness.BITS_64 else "x86"

            return (
                base_sdk_path
                / f"EFW_linux_mac_SDK_V{SDK_VERSION}"
                / "lib"
                / bitness_string
                / f"libEFWFilter.so.{SDK_VERSION}"
            )

        case Platform.MACOS:
            bitness_string = "x64" if bitness == Bitness.BITS_64 else "x86"

            return (
                base_sdk_path
                / f"EFW_linux_mac_SDK_V{SDK_VERSION}"
                / "lib"
                / "mac"
                / f"libEFWFilter.dylib.{SDK_VERSION}"
            )


############################################################
#### Data types ############################################
############################################################


class EFW_INFO(Structure):
    """Represents the `EFW_INFO` struct in the `EFWQ_filter.h` header file"""

    _fields_ = [
        ("ID", c_int),
        ("Name", c_char * 64),
        ("slotNum", c_int),
    ]


# Note: The `EFW_ERROR_CODE` enum is used as the return type of many of the library functions.
# So we use a feature of `ctypes` that allows us to declare the return type with a Python type
# that can be called on the actual returned value. In this case, the actual returned value is
# some C enum, which is just an integer, and because of the way `IntEnum` works, we can simply
# use `EFW_ERROR_CODE` to specify the return type, as calling it on an integer will select the
# correct enum name.


@verify(UNIQUE)
class EFW_ERROR_CODE(IntEnum):
    """Represents the `EFW_ERROR_CODE` enum in the `EFWQ_filter.h` header file"""

    EFW_ERROR_END = -1
    EFW_SUCCESS = 0
    EFW_ERROR_INVALID_INDEX = auto()
    EFW_ERROR_INVALID_ID = auto()
    EFW_ERROR_INVALID_VALUE = auto()

    EFW_ERROR_REMOVED = auto()
    """Failed to find the filter wheel, maybe the filter wheel has been removed"""

    EFW_ERROR_MOVING = auto()
    """Filter wheel is moving"""

    EFW_ERROR_ERROR_STATE = auto()
    """Filter wheel is in error state"""

    EFW_ERROR_GENERAL_ERROR = auto()
    """Other error"""

    EFW_ERROR_NOT_SUPPORTED = auto()
    EFW_ERROR_CLOSED = auto()


class EFW_ID(Structure):
    """Represents the `EFW_ID` struct in the `EFWQ_filter.h` header file"""

    _fields_ = [
        ("id", c_ubyte * 8),
    ]


class EFW_SN(Structure):
    """Represents the `EFW_SN` struct in the `EFWQ_filter.h` header file"""

    _fields_ = [
        ("id", c_ubyte * 8),
    ]


############################################################
#### Library loading and bindings ##########################
############################################################


def load_zwo_efw_library() -> CDLL:
    """Loads the ZWO EFW filter wheel library and returns the library object. The library object
    can then be used to call into the library's exported functions. Care needs to be taken to
    ensure that the data is marshalled back and forth between Python and the C library correctly.
    """

    # Note: View the `EFW_filter.h` header file for the source of this information. See the `ctypes`
    # Python documentation for more information on how to declare types and how to convert data
    # types. https://docs.python.org/3/library/ctypes.html

    cdll.LoadLibrary(name=_get_library_path())
    efw_sdk_library = CDLL(name="EFW_filter.dll")

    # Suggested call order by ZWO:
    # --> EFWGetNum
    # --> EFWGetID for each filter wheel
    #
    # --> EFWGetProperty
    # --> EFWOpen
    # --> EFWGetPosition
    # --> EFWSetPosition
    #     ...
    # --> EFWClose

    # /***************************************************************************
    # Descriptions:
    # this should be the first API to be called
    # get number of connected EFW filter wheel, call this API to refresh device list if EFW is connected # pylint: disable=line-too-long
    # or disconnected
    #
    # Return: number of connected EFW filter wheel. 1 means 1 filter wheel is connected.
    # ***************************************************************************/
    # EFW_API int EFWGetNum();
    efw_sdk_library.EFWGetNum.restype = c_int
    efw_sdk_library.EFWGetNum.argtypes = []

    # /***************************************************************************
    # Descriptions:
    # get the product ID of each wheel, at first set pPIDs as 0 and get length and then malloc a buffer to load the PIDs # pylint: disable=line-too-long
    #
    # Paras:
    # int* pPIDs: pointer to array of PIDs
    #
    # Return: length of the array.
    # ***************************************************************************/
    # EFW_API int EFWGetProductIDs(int* pPIDs);
    # efw_sdk_library.EFWGetProductIDs.restype = c_int
    # efw_sdk_library.EFWGetProductIDs.argtypes = [POINTER(c_int)]
    # Note: This function doesn't appear to actually be available in the EFW SDK library

    # /***************************************************************************
    # Descriptions:
    # get ID of filter wheel
    #
    # Paras:
    # int index: the index of filter wheel, from 0 to N - 1, N is returned by GetNum()
    #
    # int* ID: pointer to ID. the ID is a unique integer, between 0 to EFW_ID_MAX - 1, after opened,
    # all the operation is base on this ID, the ID will not change.
    #
    #
    # Return:
    # EFW_ERROR_INVALID_INDEX: index value is invalid
    # EFW_SUCCESS:  operation succeeds
    #
    # ***************************************************************************/
    # EFW_API EFW_ERROR_CODE EFWGetID(int index, int* ID);
    efw_sdk_library.EFWGetID.restype = EFW_ERROR_CODE
    efw_sdk_library.EFWGetID.argtypes = [c_int, POINTER(c_int)]

    # /***************************************************************************
    # Descriptions:
    # open filter wheel
    #
    # Paras:
    # int ID: the ID of filter wheel
    #
    # Return:
    # EFW_ERROR_INVALID_ID: invalid ID value
    # EFW_ERROR_GENERAL_ERROR: number of opened filter wheel reaches the maximum value.
    # EFW_ERROR_REMOVED: the filter wheel is removed.
    # EFW_SUCCESS: operation succeeds
    # ***************************************************************************/
    # EFW_API    EFW_ERROR_CODE EFWOpen(int ID);
    efw_sdk_library.EFWOpen.restype = EFW_ERROR_CODE
    efw_sdk_library.EFWOpen.argtypes = [c_int]

    # /***************************************************************************
    # Descriptions:
    # get property of filter wheel. SlotNum is 0 if not opened.
    #
    # Paras:
    # int ID: the ID of filter wheel
    #
    # EFW_INFO *pInfo:  pointer to structure containing the property of EFW
    #
    # Return:
    # EFW_ERROR_INVALID_ID: invalid ID value
    # EFW_ERROR_MOVING: slot number detection is in progress, generally this error will happen soon after filter wheel is connected. # pylint: disable=line-too-long
    # EFW_SUCCESS: operation succeeds
    # EFW_ERROR_REMOVED: filter wheel is removed
    #
    # ***************************************************************************/
    # EFW_API    EFW_ERROR_CODE EFWGetProperty(int ID, EFW_INFO *pInfo);
    efw_sdk_library.EFWGetProperty.restype = EFW_ERROR_CODE
    efw_sdk_library.EFWGetProperty.argtypes = [c_int, POINTER(EFW_INFO)]

    # /***************************************************************************
    # Descriptions:
    # get position of slot
    #
    # Paras:
    # int ID: the ID of filter wheel
    #
    # int *pPosition:  pointer to slot position, this value is between 0 to M - 1, M is slot number
    # this value is -1 if filter wheel is moving
    #
    # Return:
    # EFW_ERROR_INVALID_ID: invalid ID value
    # EFW_ERROR_CLOSED: not opened
    # EFW_SUCCESS: operation succeeds
    # EFW_ERROR_ERROR_STATE: filter wheel is in error state
    # EFW_ERROR_REMOVED: filter wheel is removed
    #
    # ***************************************************************************/
    # EFW_API    EFW_ERROR_CODE EFWGetPosition(int ID, int *pPosition);
    efw_sdk_library.EFWGetPosition.restype = EFW_ERROR_CODE
    efw_sdk_library.EFWGetPosition.argtypes = [c_int, POINTER(c_int)]

    # /***************************************************************************
    # Descriptions:
    # set position of slot
    #
    # Paras:
    # int ID: the ID of filter wheel
    #
    # int Position:  slot position, this value is between 0 to M - 1, M is slot number
    #
    # Return:
    # EFW_ERROR_INVALID_ID: invalid ID value
    # EFW_ERROR_CLOSED: not opened
    # EFW_SUCCESS: operation succeeds
    # EFW_ERROR_INVALID_VALUE: Position value is invalid
    # EFW_ERROR_MOVING: filter wheel is moving, should wait until idle
    # EFW_ERROR_ERROR_STATE: filter wheel is in error state
    # EFW_ERROR_REMOVED: filter wheel is removed
    #
    # ***************************************************************************/
    # EFW_API    EFW_ERROR_CODE EFWSetPosition(int ID, int Position);
    efw_sdk_library.EFWSetPosition.restype = EFW_ERROR_CODE
    efw_sdk_library.EFWSetPosition.argtypes = [c_int, c_int]

    # /***************************************************************************
    # Descriptions:
    # set unidirection of filter wheel
    #
    # Paras:
    # int ID: the ID of filter wheel
    #
    # bool bUnidirectional: if set as true, the filter wheel will rotate along one direction
    #
    # Return:
    # EFW_ERROR_INVALID_ID: invalid ID value
    # EFW_ERROR_CLOSED: not opened
    # EFW_SUCCESS: operation succeeds
    # ***************************************************************************/
    # EFW_API    EFW_ERROR_CODE EFWSetDirection(int ID, bool bUnidirectional);
    efw_sdk_library.EFWSetDirection.restype = EFW_ERROR_CODE
    efw_sdk_library.EFWSetDirection.argtypes = [c_int, c_bool]

    # /***************************************************************************
    # Descriptions:
    # get unidirection of filter wheel
    #
    # Paras:
    # int ID: the ID of filter wheel
    #
    # bool *bUnidirectional: pointer to unidirection value .
    #
    # Return:
    # EFW_ERROR_INVALID_ID: invalid ID value
    # EFW_ERROR_CLOSED: not opened
    # EFW_SUCCESS: operation succeeds
    # ***************************************************************************/
    # EFW_API    EFW_ERROR_CODE EFWGetDirection(int ID, bool *bUnidirectional);
    efw_sdk_library.EFWGetDirection.restype = EFW_ERROR_CODE
    efw_sdk_library.EFWGetDirection.argtypes = [c_int, POINTER(c_bool)]

    # /***************************************************************************
    # Descriptions:
    # calibrate filter wheel
    #
    # Paras:
    # int ID: the ID of filter wheel
    #
    # Return:
    # EFW_ERROR_INVALID_ID: invalid ID value
    # EFW_ERROR_CLOSED: not opened
    # EFW_SUCCESS: operation succeeds
    # EFW_ERROR_MOVING: filter wheel is moving, should wait until idle
    # EFW_ERROR_ERROR_STATE: filter wheel is in error state
    # EFW_ERROR_REMOVED: filter wheel is removed
    # ***************************************************************************/
    # EFW_API    EFW_ERROR_CODE EFWCalibrate(int ID);
    efw_sdk_library.EFWCalibrate.restype = EFW_ERROR_CODE
    efw_sdk_library.EFWCalibrate.argtypes = [c_int]

    # /***************************************************************************
    # Descriptions:
    # close filter wheel
    #
    # Paras:
    # int ID: the ID of filter wheel
    #
    # Return:
    # EFW_ERROR_INVALID_ID: invalid ID value
    # EFW_SUCCESS: operation succeeds
    # ***************************************************************************/
    # EFW_API    EFW_ERROR_CODE EFWClose(int ID);
    efw_sdk_library.EFWClose.restype = EFW_ERROR_CODE
    efw_sdk_library.EFWClose.argtypes = [c_int]

    # /***************************************************************************
    # Descriptions:
    # get version string, like "0, 4, 0824"
    # ***************************************************************************/
    # EFW_API char* EFWGetSDKVersion();
    efw_sdk_library.EFWGetSDKVersion.restype = c_char_p
    efw_sdk_library.EFWGetSDKVersion.argtypes = []

    # /***************************************************************************
    # Descriptions:
    # get hardware error code of filter wheel
    #
    # Paras:
    # int ID: the ID of filter wheel
    #
    # bool *pErrCode: pointer to error code .
    #
    # Return:
    # EFW_ERROR_INVALID_ID: invalid ID value
    # EFW_ERROR_CLOSED: not opened
    # EFW_SUCCESS: operation succeeds
    # ***************************************************************************/
    # EFW_API EFW_ERROR_CODE EFWGetHWErrorCode(int ID, int *pErrCode);
    efw_sdk_library.EFWGetHWErrorCode.restype = EFW_ERROR_CODE
    efw_sdk_library.EFWGetHWErrorCode.argtypes = [c_int, POINTER(c_int)]

    # /***************************************************************************
    # Descriptions:
    # Get firmware version of filter wheel
    #
    # Paras:
    # int ID: the ID of filter wheel
    #
    # int *major, int *minor, int *build: pointer to value.
    #
    # Return:
    # EFW_ERROR_INVALID_ID: invalid ID value
    # EFW_ERROR_CLOSED: not opened
    # EFW_SUCCESS: operation succeeds
    # ***************************************************************************/
    # EFW_API    EFW_ERROR_CODE EFWGetFirmwareVersion(int ID, unsigned char *major, unsigned char *minor, unsigned char *build); # pylint: disable=line-too-long
    efw_sdk_library.EFWGetFirmwareVersion.restype = EFW_ERROR_CODE
    efw_sdk_library.EFWGetFirmwareVersion.argtypes = [
        c_int,
        POINTER(c_ubyte),
        POINTER(c_ubyte),
        POINTER(c_ubyte),
    ]

    # /***************************************************************************
    # Descriptions:
    # Get the serial number from a EFW
    #
    # Paras:
    # int ID: the ID of focuser
    #
    # EFW_SN* pSN: pointer to SN
    #
    # Return:
    # EFW_ERROR_INVALID_ID: invalid ID value
    # EFW_ERROR_CLOSED: not opened
    # EFW_ERROR_NOT_SUPPORTED: the firmware does not support serial number
    # EFW_SUCCESS: operation succeeds
    # ***************************************************************************/
    # EFW_API EFW_ERROR_CODE EFWGetSerialNumber(int ID, EFW_SN* pSN);
    efw_sdk_library.EFWGetSerialNumber.restype = EFW_ERROR_CODE
    efw_sdk_library.EFWGetSerialNumber.argtypes = [c_int, POINTER(EFW_SN)]

    # /***************************************************************************
    # Descriptions:
    # Set the alias to a EFW
    #
    # Paras:
    # int ID: the ID of filter
    #
    # EFW_ID alias: the struct which contains the alias
    #
    # Return:
    # EFW_ERROR_INVALID_ID: invalid ID value
    # EFW_ERROR_CLOSED: not opened
    # EFW_ERROR_NOT_SUPPORTED: the firmware does not support setting alias
    # EFW_SUCCESS: operation succeeds
    # ***************************************************************************/
    # EFW_API EFW_ERROR_CODE EFWSetID(int ID, EFW_ID alias);
    efw_sdk_library.EFWSetID.restype = EFW_ERROR_CODE
    efw_sdk_library.EFWSetID.argtypes = [c_int, EFW_ID]

    return efw_sdk_library
