import glob
import platform
# import time
import serial
import sys
# import pathlib
import logging
from logger import getLogger

# from functools import partial
from serial.tools import list_ports

# current_dir = pathlib.Path(__file__).resolve()
# parent_dir = current_dir.parent.parent
# sys.path.append(str(parent_dir))
# from lib import *

logger = getLogger(logging.INFO)

if platform.system() == "Windows":
    serial_port_name = "COM3"
elif sys.platform.startswith("darwin"):
    serial_port_name = "/dev/tty.usbserial-FT9O53VF"
    serial_port_name = "/dev/tty.usbserial-D30JB26J"
else:
    serial_port_name = "/dev/ttyUSB0"


def serial_ports():
    """Lists serial port names that are likely to be USB devices.

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of the serial ports available on the system
    """
    if sys.platform.startswith("win"):
        # Use list_ports.comports() to get detailed port information
        ports = list_ports.comports()
        # Filter out only ports with 'USB' in the description
        result = [port.device for port in ports if "USB" in port.description]
    elif sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
        ports = glob.glob("/dev/tty[A-Za-z]*")
        ports = [port for port in ports if "USB" in port]
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
    elif sys.platform.startswith("darwin"):
        ports = glob.glob("/dev/tty.*")
        ports = [port for port in ports if "usb" in port.lower()]
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
    else:
        raise EnvironmentError("Unsupported platform")

    if len(result) == 0:
        logger.warning("No serial ports found")
    elif serial_port_name not in result:
        logger.warning(
            f"serial_port_name: {serial_port_name} not found in serial_ports: {result}"
        )

    return result
