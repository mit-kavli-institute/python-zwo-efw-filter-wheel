# Core dependencies
import time

# Project dependencies
from zwo_efw import EFW


efw = EFW()

try:
    efw.initialize()

    print(f"Filter wheel information: {efw.filter_wheel_information}")

finally:
    efw.close()
