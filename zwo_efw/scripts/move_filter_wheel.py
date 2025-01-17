# Core dependencies
import argparse
import time

# Project dependencies
from zwo_efw import EFW


def move() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--id")
    parser.add_argument("--slot")
    arguments = parser.parse_args()
    id = int(arguments.id)
    slot = int(arguments.slot)

    efw = EFW()

    try:
        efw.initialize()

        efw.set_position(id, slot)

        while efw.is_moving(id):
            print(f"Filter wheel is moving ...")
            time.sleep(1)

        print(f"Done. Filter wheel {id} is now at slot {efw.get_position(id)}")

    finally:
        efw.close()


if __name__ == "__main__":
    run()
