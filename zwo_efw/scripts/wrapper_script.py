# Core dependencies
import time

# Project dependencies
from zwo_efw.wrapper import EFWWrapper


efw = EFWWrapper()

print(f"Number of connected filter wheels: {efw.get_number_of_connected_filter_wheels()}")

print(f"Filter wheel ID for index 0: {efw.get_filter_wheel_id(0)}")

print("Opening filter wheel ID 0 ...")
efw.open_filter_wheel(0)

print(f"Filter wheel information: {efw.get_filter_wheel_information(0)}")

print(f"Position of filter wheel ID 0: {efw.get_position(0)}")

print("Setting position of filter wheel ID 0 to 1 ...")
efw.set_position(0, 0)

# Wait just enough time for the move to complete
time.sleep(5)

print("Closing filter wheel ID 0 ...")
efw.close_filter_wheel(0)
