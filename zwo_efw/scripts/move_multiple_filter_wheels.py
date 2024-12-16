# Core dependencies
import time

# Project dependencies
from zwo_efw import EFW


efw = EFW()

try:
    efw.initialize()
    efw.filter_wheel_information

    for filter_wheel in efw.filter_wheel_information:
        id = filter_wheel.ID

        position = efw.get_position(id)

        print(f"Moving filter wheel ID {id} four slot positions")

        efw.set_position(id, (position + 4) % 5 )

        while efw.is_moving(id):
            time.sleep(1)

        print(f"Done moving filter wheel ID {id}")

finally:
    efw.close()
