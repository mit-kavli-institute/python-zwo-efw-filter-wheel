# Core dependencies
import time

# Project dependencies
from zwo_efw import EFW


efw = EFW()

try:
    efw.initialize()
    efw.set_position(0, 2)

    while efw.is_moving(0):
        print(f"Position: {efw.get_position(0)}")
        time.sleep(1)

    print(f"Position: {efw.get_position(0)}")

finally:
    efw.close()
