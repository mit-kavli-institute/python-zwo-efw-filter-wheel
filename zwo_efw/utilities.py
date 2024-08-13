# Core dependencies
from enum import Enum, auto
import platform
import sys


class Bitness(Enum):
    """Represents the bitness of an operating system"""

    BITS_32 = auto()
    BITS_64 = auto()


class Platform(Enum):
    """Represents an operating system platform"""

    WINDOWS = auto()
    LINUX = auto()
    MACOS = auto()


def get_platform_bitness():
    """Gets the bitness of the current operating system platform"""
    if sys.maxsize > 2**32:
        return Bitness.BITS_64
    else:
        return Bitness.BITS_32


def get_operating_system():
    """Gets the operating system platform of the current system"""
    match platform.system():
        case "Windows":
            return Platform.WINDOWS

        case "Linux":
            return Platform.LINUX

        case "Darwin":
            return Platform.MACOS

        case _:
            raise NotImplementedError(f"Unsupported platform: {platform.system()}")
