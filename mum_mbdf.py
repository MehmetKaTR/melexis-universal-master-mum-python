"""
Python example application to use the Melexis MUM for MeLiBu communication using a MBDF file

Copyright Melexis N.V.

This product includes software developed at Melexis N.V. (https://www.melexis.com).

Melexis N.V. has provided this code according to LICENSE file attached to repository
"""
import time
import logging
import os
from pymumclient import MelexisUniversalMaster
from pymelibu import MelibuBusManager
from pymelibu import MelibuCluster
from pymumclient import MelibuLowLevelException
from pymelibu.protocol import MelibuNetworkManagement

from pymelibu import Melibu1Device
NUMBER_OF_NODES = 5
FIRST_NODE_ADDRESS = 55


MELIBU_VERSION_1 = 1

def main():
    """ Python example application to use the Melexis MUM for MeLiBu communication

    This example shows how a MBDF file can be used to define the frame + content.
    The used MBDF file is located within the subfolder "example_inputs" and must be used
    together with the .hex file of the same name. For example:
    81116xAE_PWM_4RGBLED.MBDF has to be used with a node which is programmed with:
    81116xAE_PWM_4RGBLED.hex
    """

    # The logging can be used to check which commands are send to the
    # Melexis Universal Master (MUM) in which order and with which content
    # This requires to update level=logging.ERROR to level=logging.DEBUG
    log_format = "%(asctime)-15s %(name)s %(levelname)-8s %(message)s"
    logging.basicConfig(filename="melibu_log.log", filemode="w", level=logging.ERROR, format=log_format)

    print("Agasan Bootloader - MehmetKaTR")
    print("---------------------------------------\n")

    # create objects and connect
    mlx_master = MelexisUniversalMaster()
    mlx_master.open_all("mum-sag") # 192.168.7.2

    # get the slave power control object
    power_control = mlx_master.get_device("power_out0")

    # configure the client interface to use the MeLiBu interface
    melibumaster = mlx_master.get_device("melibu0")

    # Configure the MUM to use MeLiBu for normal operation after selecting melibu0
    melibumaster.setup()
     # create a MeLiBu bus bus object
    melibubus = MelibuBusManager(melibumaster, MELIBU_VERSION_1)

    # create a standard MeLiBu device object
    melibudevice = Melibu1Device(melibubus)
    
 # create a MeLiBu network object
    MelibuNetworkManagement = melibudevice.get_device("bus/network_management")
    try:
        # The autoaddressing requires to set a number of nodes which are available in the system and
        # which address shall be the first address witin the system
        # Please ensure that the requirements for autoaddressing are fulfilled
        print("\nConfigure the Autoaddressing parameters:")
        MelibuNetworkManagement.start_address = FIRST_NODE_ADDRESS
        MelibuNetworkManagement.number_slaves = NUMBER_OF_NODES
        print("First Node-Address:", MelibuNetworkManagement.start_address)
        print("Number of nodes:", MelibuNetworkManagement.number_slaves)

        # In case the EPM command is not send via broadcast, the
        # autoaddressing shall be executed before the EPM command
        print("\nStart Autoaddressing sequence before EPM")
        MelibuNetworkManagement.autoaddressing(True, 50)
        MelibuNetworkManagement.autoaddressing(True, 50)
        


    except MelibuLowLevelException as error:
        print(error)
    # get the file-path for MBDF file to use
    # the MBDF must match the firmware settings to ensure a proper communication
    # For this example a MLX81116xAE + EVB81116-A2 is used with:
    # 81116xAE_PWM_4RGBLED.MBDF has to be used with a node which is programmed with 81116xAE_PWM_4RGBLED.hex
    dirname = os.path.dirname(__file__)
    mbdf_filename = os.path.join(dirname, "Programlar/FCL_Right.MBDF")
    # create a MeLiBu cluster object by providing the MBDF file
    # the MBDF file is used to create a model including frames, signals, schedules etc.
    melibucluster = MelibuCluster(mbdf_filename)

    # create a MeLiBu bus bus object
    melibubus = MelibuBusManager(melibumaster, melibucluster.melibu_version)

    melibucluster.bind_bus(melibubus)

    # get the melibu device object from the cluster providing a valid node name which is used in the MBDF file
    melibudevice = melibucluster.get_slave("MLX_Node1")
 
    print(melibudevice)

    print("Power up slave\n")
    power_control.power_up()
    time.sleep(0.020)
  
   

    

    print("The following signals are supported by the node:")
    for signal in melibudevice.node.supported_signals:
        print(signal, "with current value:", melibudevice.node.supported_signals[signal])

    print("\nThe following MeLiBu frames are supported by the node:")
    for frame in melibudevice.node.supported_frames:
        print(frame)

    print("\nExchanged signal value, used in message SetColor for example")
    melibudevice.set_signal_value("led_0_duty_cycle_write", 5000)
    # handle_frame is receiving/transmitting the message on the bus, including creating the payload etc based
    # on the signal values

    # The signals which are used by the message are updated afterwards
  
    print(melibudevice.handle_frame("set_pwm_duty_cycle"))
    
    time.sleep(0.020)


    print("\nRequest to fill TX-Buffer with LED Vf values, done with ReqVfData")
    print(melibudevice.handle_frame("req_diag1"))
  
    time.sleep(0.020)

    print("\nRequest S2M message with LedVf")
    #handle_frame is receiving/transmitting the message on the bus, including creating the payload etc based
    #on the signal values
    #The signals which are used by the message are updated afterwards
    print(melibudevice.handle_frame("get_diag1"))
    #get_signal_value provides the value of the signal represented in human readable format based on the settings
     #which are provided in the section "Signal_encoding_types" in the MBDF.
    print("Signal value SigVfLC0: " + str(melibudevice.get_signal_value("led_0_fv")))
     #get_bus_value provides the raw value of the signal which is send/received on the bus.
    print("Bus value SigVfLC0: " + str(melibudevice.get_bus_value("led_0_fv")))
    time.sleep(0.20)


    print("\nPower down slave")
    power_control.power_down()

    melibumaster.teardown()

    mlx_master.close_all()


if __name__ == "__main__":
    main()
