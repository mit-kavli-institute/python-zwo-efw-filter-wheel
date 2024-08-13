# Core dependencies
import time

# Project dependencies
from zwo_efw import EFW


efw = EFW()

try:
    efw.initialize()
    efw.move(0, 2)

    while efw.is_moving(0):
        print(f"Position: {efw.get_current_slot(0)}")
        time.sleep(1)

    print(f"Position: {efw.get_current_slot(0)}")

finally:
    efw.close()
