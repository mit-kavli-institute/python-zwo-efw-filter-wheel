# Core dependencies
import time

# Project dependencies
from zwo_efw import EFW

efw = EFW()

try:
    # Initialize communication to any EFW filter wheels that are connected
    efw.initialize()

    # Get the information for all the filter wheels that were identified
    filter_wheel_information = efw.filter_wheel_information

    # For each filter wheel present, print out its information bundle
    for filter_wheel in filter_wheel_information:
        print("The following filter wheels are present:")
        print(f"    {filter_wheel}")
    print()  # print a newline

    # Get the first available filter wheel
    filter_wheel = filter_wheel_information[0]

    # Cycle through all the slots in the filter wheel once
    for current_slot in range(1, filter_wheel.NumberOfSlots + 1):
        print(f"Moving to slot {current_slot} ...")
        efw.move(filter_wheel.ID, current_slot)

        # Wait until the filter wheel has finished moving to the commanded slot
        while efw.is_moving(filter_wheel.ID):
            # Note that `None` means that the position is unknown, which is usually
            # because the filter wheel is moving between slots
            print(f"Position: {efw.get_current_slot(filter_wheel.ID)}")
            time.sleep(0.5)

        # The move is done, so print out the current slot position
        print(f"Finished moving to slot {current_slot}\n")

        # Wait 1 second before the next move
        print("Waiting 1 second before the next move ...\n")
        time.sleep(1)

except KeyboardInterrupt:
    print("\nKeyboard interrupt detected. Stopping the script.\n")

except Exception as exception:
    print(f"An exception occurred: {exception}\n")

finally:
    print(
        "Done moving through all the slots, an exception occurred, "
        "or a keyboard interrupt was detected."
    )
    efw.close()
