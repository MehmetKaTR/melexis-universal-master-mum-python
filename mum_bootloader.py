import time
import logging
import os
import sys
import os, sys
print("PYTHON:", sys.executable)
print("CWD:", os.getcwd())


from pymumclient import MelexisUniversalMaster
from pymumclient import MelibuLowLevelException
from pymelibu import MelibuBusManager
from pymelibu import Melibu1Device

MELIBU_VERSION_1 = 1
FIRST_NODE_ADDRESS = 55
NUMBER_OF_NODES = 5
TARGET_NODE = 55

MAX_RETRY = 5


def run_bootloader():
    print("\nPower up slave")
    power_control.power_up()
    time.sleep(0.05)

    print("\nErase FLASH")
    melibudevice.erase_memory(
        mem_type="FLASH",
        target=TARGET_NODE,
        startaddress=FIRST_NODE_ADDRESS,
        slave_count=NUMBER_OF_NODES,
        epm_delay_ms=100
    )

    print("\nErase EEPROM")
    melibudevice.erase_memory(
        mem_type="EEPROM",
        target=TARGET_NODE,
        startaddress=FIRST_NODE_ADDRESS,
        slave_count=NUMBER_OF_NODES,
        epm_delay_ms=100
    )

    print("\nProgram FLASH")
    melibudevice.program_memory(
        mem_type="FLASH",
        hexfile=filename,
        target=TARGET_NODE,
        startaddress=FIRST_NODE_ADDRESS,
        slave_count=NUMBER_OF_NODES,
        epm_delay_ms=100
    )


def main():
    print("3E Automotive BootLoader")
    print("---------------------------------------\n")

    mlx_master = MelexisUniversalMaster()
    mlx_master.open_all("mum-sag") # 192.168.7.2

    global power_control, melibudevice, filename

    power_control = mlx_master.get_device("power_out0")
    melibumaster = mlx_master.get_device("melibu0")
    melibumaster.setup()

    melibubus = MelibuBusManager(melibumaster, MELIBU_VERSION_1)
    melibudevice = Melibu1Device(melibubus)

    melibubus.get_device("physical_layer").baudrate = 1_000_000

    filename = os.path.join(
        os.path.dirname(__file__),
        "Programlar/81116xAC_GRAVITY.hex"
    )

    retry = 0

    while True:
        try:
            run_bootloader()
            print("\nBootloader finished")
            sys.exit(0)

        except MelibuLowLevelException as err:
            retry += 1

            print("\nBootloader error:")
            print(err)

            print("Power down slave")
            power_control.power_down()

            if retry >= MAX_RETRY:
                print(f"\nFAILED after {MAX_RETRY} retries")
                melibumaster.teardown()
                mlx_master.close_all()
                sys.exit(1)   #HATA

            time.sleep(0.5)
            print(f"Retrying... ({retry}/{MAX_RETRY})\n")

    # (buraya normalde düşmez)


if __name__ == "__main__":
    main()
