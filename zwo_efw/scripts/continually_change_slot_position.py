# Core dependencies
import itertools
import time

# Project dependencies
from zwo_efw import EFW


efw = EFW()

try:
    efw.initialize()

    filter_wheel_information = efw.filter_wheel_information

    for filter_wheel in filter_wheel_information:
        print("The following filter wheels are present:")
        print(filter_wheel)

    # Get the first available filter wheel
    filter_wheel = filter_wheel_information[0]

    # Continuously cycle through all the slots in the filter wheel
    for current_slot in itertools.cycle(range(1, filter_wheel.NumberOfSlots + 1)):
        print(f"Moving to slot {current_slot} ...")
        efw.move(filter_wheel.ID, current_slot)

        while efw.is_moving(filter_wheel.ID):
            print(f"Position: {efw.get_current_slot(filter_wheel.ID)}")
            time.sleep(0.5)

        print(f"Finished moving to slot {current_slot}")

        time.sleep(1)

finally:
    efw.close()
