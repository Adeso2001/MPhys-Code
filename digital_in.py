"""
File:                       digital_in.py

Library Call Demonstrated:  mcculw.ul.d_in() and mcculw.ul.d_bit_in()

Purpose:                    Reads a digital input port.

Demonstration:              Configures the first compatible port  for input
                            (if necessary) and then reads and displays the value
                            on the port and the first bit.

Other Library Calls:        mcculw.ul.d_config_port()
                            mcculw.ul.release_daq_device()

Special Requirements:       Device must have a digital input port
                            or have digital ports programmable as input.
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import DigitalIODirection
from mcculw.device_info import DaqDeviceInfo

try:
    from console_examples_util import config_first_detected_device
except ImportError:
    from .console_examples_util import config_first_detected_device

def read_digital_port(board_num, port):
    try:
        daq_dev_info = DaqDeviceInfo(board_num)
        if not daq_dev_info.supports_digital_io:
            raise Exception('Error: The DAQ device does not support digital I/O')

        dio_info = daq_dev_info.get_dio_info()
        port_info = next((p for p in dio_info.port_info if p.type == port), None)
        
        if not port_info or not port_info.supports_input:
            raise Exception(f'Error: The specified port {port} does not support digital input')

        if port_info.is_port_configurable:
            ul.d_config_port(board_num, port, DigitalIODirection.IN)

        port_value = ul.d_in(board_num, port)
        print(f'Read {port.name} value: {port_value}')
        return port_value
    except Exception as e:
        print(f'Error in read_digital_port: {e}')
        return None

def read_digital_bit(board_num, port, bit_num):
    try:
        daq_dev_info = DaqDeviceInfo(board_num)
        if not daq_dev_info.supports_digital_io:
            raise Exception('Error: The DAQ device does not support digital I/O')

        dio_info = daq_dev_info.get_dio_info()
        port_info = next((p for p in dio_info.port_info if p.type == port), None)
        
        if not port_info or not port_info.supports_input:
            raise Exception(f'Error: The specified port {port} does not support digital input')

        if port_info.is_port_configurable:
            ul.d_config_port(board_num, port, DigitalIODirection.IN)

        bit_value = ul.d_bit_in(board_num, port, bit_num)
        print(f'Read {port.name} bit {bit_num} value: {bit_value}')
        return bit_value
    except Exception as e:
        print(f'Error in read_digital_bit: {e}')
        return None

def run_example():
    # By default, the example detects and displays all available devices and
    # selects the first device listed. Use the dev_id_list variable to filter
    # detected devices by device ID (see UL documentation for device IDs).
    # If use_device_detection is set to False, the board_num variable needs to
    # match the desired board number configured with Instacal.
    use_device_detection = True
    dev_id_list = []
    board_num = 0

    try:
        if use_device_detection:
            config_first_detected_device(board_num, dev_id_list)

        daq_dev_info = DaqDeviceInfo(board_num)
        if not daq_dev_info.supports_digital_io:
            raise Exception('Error: The DAQ device does not support digital I/O')

        print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',
              daq_dev_info.unique_id, ')\n', sep='')

        dio_info = daq_dev_info.get_dio_info()

        # Find the first port that supports input, defaulting to None
        # if one is not found.
        port = next((port for port in dio_info.port_info if port.supports_input),
                    None)
        if not port:
            raise Exception('Error: The DAQ device does not support digital input')

        # Read the digital port
        port_value = read_digital_port(board_num, port.type)

        # Read the first digital bit
        bit_num = 0
        bit_value = read_digital_bit(board_num, port.type, bit_num)

    except Exception as e:
        print('\n', e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
