#!/usr/bin/env python3

import argparse
from time import sleep

import serial

from test_equipment.serial_helper import SerialPortFinder

from p3lib.uio import UIO
from p3lib.helper import logTraceBack


class DMM8112(object):
    """@brief Responsible for an interface to R&S (Hameg) 8112-3 6.5 digit precision multimeter."""

    BPS = 9600
    TIMEOUT_SECONDS = 10

    GROUP_0 = '0'
    GROUP_1 = '1'
    GROUP_2 = '2'
    VALID_GROUPS = (GROUP_0,
                    GROUP_1,
                    GROUP_2)

    # 3rd character to select function, 1st char = 0', group/second char = '0'
    GROUP_0_VDC_FUNCTION = '0'
    GROUP_0_VAC_FUNCTION = '1'
    GROUP_0_IDC_FUNCTION = '2'
    GROUP_0_IAC_FUNCTION = '3'
    GROUP_0_OHM_2WIRE_FUNCTION = '4'
    GROUP_0_OHM_4WIRE_FUNCTION = '5'
    GROUP_0_FREQ_PERIOD_VAC_FUNCTION = '8'
    GROUP_0_DIODE_TEST_FUNCTION = 'B'
    GROUP_0_CONTINUITY_FUNCTION = 'C'
    GROUP_0_SENSOR_RTD_2WIRE_FUNCTION = 'D'
    GROUP_0_SENSOR_RTD_4WIRE_FUNCTION = 'E'
    GROUP_0_SENSOR_TH_FUNCTION = 'F'

    GROUP_0_VALID_FUNCTIONS = (GROUP_0_VDC_FUNCTION,
                               GROUP_0_VAC_FUNCTION,
                               GROUP_0_IDC_FUNCTION,
                               GROUP_0_IAC_FUNCTION,
                               GROUP_0_OHM_2WIRE_FUNCTION,
                               GROUP_0_OHM_4WIRE_FUNCTION,
                               GROUP_0_FREQ_PERIOD_VAC_FUNCTION,
                               GROUP_0_DIODE_TEST_FUNCTION,
                               GROUP_0_CONTINUITY_FUNCTION,
                               GROUP_0_SENSOR_RTD_2WIRE_FUNCTION,
                               GROUP_0_SENSOR_RTD_4WIRE_FUNCTION,
                               GROUP_0_SENSOR_TH_FUNCTION)

    # VDC 4'th character / parameter
    GROUP_0_VDC_100MV = '0'
    GROUP_0_VDC_1V = '1'
    GROUP_0_VDC_10V = '2'
    GROUP_0_VDC_100V = '3'
    GROUP_0_VDC_600V = '4'

    # VAC 4'th character / parameter
    GROUP_0_VAC_1V = '6'
    GROUP_0_VAC_10V = '7'
    GROUP_0_VAC_100V = '8'
    GROUP_0_VAC_600V = '9'

    # IDC 4'th character / parameter
    GROUP_0_IDC_0_1MA = '0'
    GROUP_0_IDC_1MA = '1'
    GROUP_0_IDC_10MA = '2'
    GROUP_0_IDC_100MA = '3'
    GROUP_0_IDC_1A = '4'

    # IAC 4'th character / parameter
    GROUP_0_IAC_0_1MA = GROUP_0_IDC_0_1MA
    GROUP_0_IAC_1MA = GROUP_0_IDC_1MA
    GROUP_0_IAC_10MA = GROUP_0_IDC_10MA
    GROUP_0_IAC_100MA = GROUP_0_IDC_100MA
    GROUP_0_IAC_1A = GROUP_0_IDC_1A

    # OHM_2WIRE 4'th character / parameter
    GROUP_0_OHM_2WIRE_100_OHM = '0'
    GROUP_0_OHM_2WIRE_1K_OHM = '1'
    GROUP_0_OHM_2WIRE_10K_OHM = '2'
    GROUP_0_OHM_2WIRE_100K_OHM = '3'
    GROUP_0_OHM_2WIRE_1M_OHM = '4'
    GROUP_0_OHM_2WIRE_10M_OHM = '5'

    # OHM_4WIRE 4'th character / parameter
    GROUP_0_OHM_4WIRE_100_OHM = GROUP_0_OHM_2WIRE_100_OHM
    GROUP_0_OHM_4WIRE_1K_OHM = GROUP_0_OHM_2WIRE_1K_OHM
    GROUP_0_OHM_4WIRE_10K_OHM = GROUP_0_OHM_2WIRE_10K_OHM
    GROUP_0_OHM_4WIRE_100K_OHM = GROUP_0_OHM_2WIRE_100K_OHM
    GROUP_0_OHM_4WIRE_1M_OHM = GROUP_0_OHM_2WIRE_1M_OHM
    GROUP_0_OHM_4WIRE_10M_OHM = GROUP_0_OHM_2WIRE_10M_OHM

    # OHM_FREQ_PERIOD_VAC 4'th character / parameter
    GROUP_0_FREQ_PERIOD_VAC_FREQ = '1'
    GROUP_0_FREQ_PERIOD_VAC_PERIOD = '2'

    # CONTINUITY 4'th character / parameter
    GROUP_0_CONTINUITY_10_OHM = '6'

    # SENSOR_RTD_2WIRE 4'th character / parameter
    GROUP_0_SENSOR_RTD_2WIRE_PT100 = '3'
    GROUP_0_SENSOR_RTD_2WIRE_PT1000 = '5'

    # SENSOR_RTD_4WIRE 4'th character / parameter
    GROUP_0_SENSOR_RTD_2WIRE_PT100 = GROUP_0_SENSOR_RTD_2WIRE_PT100
    GROUP_0_SENSOR_RTD_2WIRE_PT1000 = GROUP_0_SENSOR_RTD_2WIRE_PT1000

    # SENSOR_TH 4'th character / parameter
    GROUP_0_SENSOR_TH_J = '1'
    GROUP_0_SENSOR_TH_K = '2'

    # 3rd character to select function, 1st char = 0', group/second char = '1'
    GROUP_1_AUTO_RANGE_FUNCTION = '0'
    GROUP_1_MEAS_TIME_FUNCTION = '1'
    GROUP_1_FILTER_FUNCTION = '2'
    GROUP_1_MATH_FUNCTION = '3'
    GROUP_1_TRIGGER_FUNCTION = '6'
    GROUP_1_ZERO_FUNCTION = '7'
    GROUP_1_TEMP_FUNCTION = '8'
    GROUP_1_STORAGE_FUNCTION = '9'
    GROUP_1_BUFFER_FUNCTION = 'A'
    GROUP_1_RECORD_NR_FUNCTION = 'B'
    GROUP_1_SENSOR_COMP_FUNCTION = 'C'
    GROUP_1_TEST_FUNCTION = 'F'

    GROUP_1_VALID_FUNCTIONS = (GROUP_1_AUTO_RANGE_FUNCTION,
                               GROUP_1_MEAS_TIME_FUNCTION,
                               GROUP_1_FILTER_FUNCTION,
                               GROUP_1_MATH_FUNCTION,
                               GROUP_1_TRIGGER_FUNCTION,
                               GROUP_1_ZERO_FUNCTION,
                               GROUP_1_TEMP_FUNCTION,
                               GROUP_1_STORAGE_FUNCTION,
                               GROUP_1_BUFFER_FUNCTION,
                               GROUP_1_RECORD_NR_FUNCTION,
                               GROUP_1_SENSOR_COMP_FUNCTION,
                               GROUP_1_TEST_FUNCTION)

    # AUTO_RANGE 4'th character / parameter
    GROUP_1_AUTO_RANGE_OFF = '0'
    GROUP_1_AUTO_RANGE_ON = '1'
    GROUP_1_AUTO_RANGE_UP = '8'
    GROUP_1_AUTO_RANGE_DOWN = '9'

    # MEAS_TIME 4'th character / parameter
    GROUP_1_MEAS_TIME_10MS = '1'
    GROUP_1_MEAS_TIME_50MS = '2'
    GROUP_1_MEAS_TIME_100MS = '3'
    GROUP_1_MEAS_TIME_500MS = '4'
    GROUP_1_MEAS_TIME_1S = '5'
    GROUP_1_MEAS_TIME_10S = '6'
    GROUP_1_MEAS_TIME_60S = '7'
    GROUP_1_MEAS_TIME_UP = GROUP_1_AUTO_RANGE_UP
    GROUP_1_MEAS_TIME_DOWN = GROUP_1_AUTO_RANGE_DOWN

    # FILTER 4'th character / parameter
    GROUP_1_FILTER_CONT = '0'
    GROUP_1_FILTER_2 = '1'
    GROUP_1_FILTER_4 = '2'
    GROUP_1_FILTER_8 = '3'
    GROUP_1_FILTER_16 = '4'

    # MATH 4'th character / parameter
    GROUP_1_MATH_OFF = '0'
    GROUP_1_MATH_OFFSET = '1'
    GROUP_1_MATH_HIGH_LIMIT = '2'
    GROUP_1_MATH_LOW_LIMIT = '3'
    GROUP_1_MATH_MAX = '7'
    GROUP_1_MATH_MIN = '8'

    # TRIGGER 4'th character / parameter
    GROUP_1_TRIGGER_AUTO = '0'
    GROUP_1_TRIGGER_SINGLE = '1'

    # ZERO 4'th character / parameter
    GROUP_1_ZERO_ZERO = '1'

    # TEMP 4'th character / parameter
    GROUP_1_TEMP_C = '4'
    GROUP_1_TEMP_F = '5'

    # STORAGE 4'th character / parameter
    GROUP_1_STORAGE_STOP = '0'
    GROUP_1_STORAGE_START = '1'
    GROUP_1_STORAGE_DUMP = '2'
    GROUP_1_STORAGE_SINGLE_DUMP = '3'
    GROUP_1_STORAGE_CLEAR = '4'
    GROUP_1_STORAGE_REC_END = '5'
    GROUP_1_STORAGE_REC_EMPTY = '6'
    GROUP_1_STORAGE_STOR_FULL = '7'

    # BUFFER 4'th character / parameter
    GROUP_1_BUFFER_OFF = '0'
    GROUP_1_BUFFER_ON = '1'
    GROUP_1_BUFFER_DUMP = '2'
    GROUP_1_BUFFER_CLEAR = '3'
    GROUP_1_BUFFER_AUTO_CLEAR = '4'
    GROUP_1_BUFFER_EMPTY = '5'

    # RECORD_NR 4'th character / parameter
    GROUP_1_RECORD_NR_1 = '1'
    GROUP_1_RECORD_NR_2 = '2'
    GROUP_1_RECORD_NR_3 = '3'
    GROUP_1_RECORD_NR_4 = '4'
    GROUP_1_RECORD_NR_5 = '5'
    GROUP_1_RECORD_NR_6 = '6'
    GROUP_1_RECORD_NR_8 = '8'
    GROUP_1_RECORD_NR_F = 'F'

    # SENSOR_COMP 4'th character / parameter
    GROUP_1_SENSOR_COMP_EXT_ICE = '0'
    GROUP_1_SENSOR_COMP_23C = '1'
    GROUP_1_SENSOR_COMP_FRONT = '2'

    # TEST 4'th character / parameter
    GROUP_1_TEST_RAM = '1'
    GROUP_1_TEST_RAM_GOOD = '4'
    GROUP_1_TEST_RAM_FAIL = '5'

    # 3rd character to select function, 1st char = 0', group/second char = '2'
    GROUP_2_COM_RS232_FUNCTION = '2'
    GROUP_2_MESSAGE_FUNCTION = 'C'
    GROUP_2_ERROR_FUNCTION = 'D'
    GROUP_2_INFO_DATA_READ_FUNCTION = 'F'

    VALID_GROUP_2_FUNCTIONS = (GROUP_2_COM_RS232_FUNCTION,
                               GROUP_2_MESSAGE_FUNCTION,
                               GROUP_2_ERROR_FUNCTION,
                               GROUP_2_INFO_DATA_READ_FUNCTION)

    # COM_RS232 4'th character / parameter
    GROUP_2_COM_RS232_OFF = '0'
    GROUP_2_COM_RS232_9600 = '3'
    GROUP_2_COM_RS232_19200 = '4'

    # MESSAGE 4'th character / parameter
    GROUP_2_MESSAGE_STATE_DUMP = '2'
    GROUP_2_MESSAGE_STATE_OFF = '3'
    GROUP_2_MESSAGE_STATE_AUTO_STATE = '4'
    GROUP_2_MESSAGE_STATE_CONT_STATE = '5'

    # ERROR 4'th character / parameter
    GROUP_2_ERROR_LENGTH = '0'
    GROUP_2_ERROR_GROUP_1 = '1'
    GROUP_2_ERROR_GROUP_2 = '2'
    GROUP_2_ERROR_GROUP_E = '9'

    # INFO_DATA_READ 4'th character / parameter
    GROUP_2_INFO_DATA_READ_REVISION = '0'
    GROUP_2_INFO_DATA_LAST_CAL = '1'
    GROUP_2_INFO_DATA_SER_NUM = '2'
    GROUP_2_INFO_DATA_LEAD_RES = '3'

    def __init__(self, uio=None):
        """@brief Constructor.
           @param uio A UIO instance or None. If a UIO instance is passed then debug messages
                  may be displayed when the _debug(msg) method is called."""
        self._uio = uio
        self._serial = None

    def _debug(self, msg):
        """@brief Display a debug message."""
        if self._uio:
            self._uio.debug(msg)

    def _info(self, msg):
        """@brief Display an info message."""
        if self._uio:
            self._uio.info(msg)

    def connect(self, dev):
        """@brief Connect to the PSU.
           @param dev The serial port to use. This maybe the device name, the serial
                      port serial number or the USB location string.
                      See SerialPortFinder.GetDevice() for more info."""
        if not self._serial:
            serialDev = SerialPortFinder.GetDevice(dev)
            if serialDev is None:
                raise Exception("No serial port found.")

            self._serial = serial.Serial()
            self._serial.port = serialDev
            self._serial.baudrate = DMM8112.BPS
            self._serial.bytesize = serial.EIGHTBITS
            self._serial.stopbits = serial.STOPBITS_ONE
            self._serial.parity = serial.PARITY_NONE
            self._serial.xonxoff = False
            self._serial.rtscts = False
            self._serial.dsrdtr = False
            self._serial.timeout = DMM8112.TIMEOUT_SECONDS
            self._serial.open()
            self._serial.setDTR(True)  # DTR on
            self._serial.setRTS(False)  # RTS on
            if not self._serial.is_open:
                raise Exception(
                    "Failed to open {serialDev}. check it's not in use.")
            self._debug(f"Connected to {serialDev}")

    def disconnect(self):
        """@brief Disconnect from the instrument."""
        if self._serial:
            self._serial.close()
            self._serial = None

    def send_cmd(self, group, function, parameter):
        """@brief Set the state of the meter.
           @param group The command group ('0','1' or '2').
           @param function The function select character.
           @param parameter The parameter for the selected function."""
        # Check the arguments are valid
        if group not in DMM8112.VALID_GROUPS:
            raise Exception(
                f"{group} is an invalid group ({",".join(DMM8112.VALID_GROUPS)} are valid.)")

        if group == DMM8112.VALID_GROUPS[0]:
            if function not in DMM8112.GROUP_0_VALID_FUNCTIONS:
                raise Exception(
                    f"{function} is an invalid function for group 0 commands ({",".join(DMM8112.VALID_GROUP_0_FUNCTIONS)} are valid.)")

        if group == DMM8112.VALID_GROUPS[1]:
            if function not in DMM8112.GROUP_1_VALID_FUNCTIONS:
                raise Exception(
                    f"{function} is an invalid function for group 1 commands ({",".join(DMM8112.VALID_GROUP_1_FUNCTIONS)} are valid.)")

        if group == DMM8112.VALID_GROUPS[2]:
            if function not in DMM8112.GROUP_2_VALID_FUNCTIONS:
                raise Exception(
                    f"{function} is an invalid function for group 2 commands ({",".join(DMM8112.VALID_GROUP_2_FUNCTIONS)} are valid.)")

        cmd_string = '0' + group + function + parameter + "\r"
        self._debug(f"CMD: {cmd_string}")
        # The command does not always appear to be acted upon by the meter ???
        # Workaround this by sending the command 10 times.
        # for _ in range(0,10):
        self._serial.write(cmd_string.encode())
        self._serial.flush()
        # The meter appears to need some time to process the cmd before sending
        # another or it ignores cmds.
        sleep(0.1)

    def _get_full_function_name(self, function_name):
        ff_name = None
        attr_list = self._get_attr_list()
        for attr in attr_list:
            group = attr[:7]
            _attr = attr[8:]
            __attr = _attr.replace("_FUNCTION", "")
            if __attr == function_name:
                ff_name = group + "_" + __attr + "_FUNCTION"
                break
        return ff_name

    def _get_full_parameter_name(self, parameter_name):
        param_name = None
        attr_list = self._get_attr_list()
        for attr in attr_list:
            if attr.endswith(parameter_name):
                param_name = attr
                break
        return param_name

    def _get_group_name(self, full_func_or_param_name):
        return full_func_or_param_name[:7]

    def send(self, function_name, parameter_name):
        """@brief Send a command to the meter.
           @param function_name The name of the function to be set.
           @param parameter_name The name of the parameter to be set."""
        if function_name is None:
            raise Exception("Function name not set.")

        if parameter_name is None:
            raise Exception("Parameter name not set.")

        full_function_name = self._get_full_function_name(function_name)
        full_parameter_name = self._get_full_parameter_name(parameter_name)
        group_name = self._get_group_name(full_parameter_name)

        if hasattr(DMM8112, group_name):
            char2 = getattr(DMM8112, group_name)
        else:
            raise Exception(f"{group_name} group name not found.")

        if hasattr(DMM8112, full_function_name):
            char3 = getattr(DMM8112, full_function_name)
        else:
            raise Exception(f"{full_function_name} not found.")

        if hasattr(DMM8112, full_parameter_name):
            char4 = getattr(DMM8112, full_parameter_name)
        else:
            raise Exception(f"{full_parameter_name} parameter name not found.")

        self.send_cmd(char2, char3, char4)

    def get_str(self):
        """@brief Get a response on the serial port."""
        self._serial.reset_input_buffer()
        return self._serial.readline().decode()

    def get_float(self):
        """@return a float value on the serial port."""
        value = None
        rx_str = self.get_str()
        rx_str = rx_str.rstrip("\n\r")
        try:
            value = float(rx_str)
        except ValueError:
            pass
        return value

    def _get_attr_list(self):
        arg_list = [attr for attr in dir(DMM8112) if attr.isupper()]
        return arg_list

    def list_args(self):
        """@param list the arguments that the user can pass."""
        constant_names = self._get_attr_list()
        result_dict = {}
        for group in ('GROUP_0', 'GROUP_1', 'GROUP_2'):
            group_list = [s for s in constant_names if s.startswith(group)]
            group_0_function_list = [
                s for s in group_list if s.endswith('_FUNCTION')]
            for name in group_0_function_list:
                _name = name.replace("_FUNCTION", "")
                __name = _name.replace(group, "")
                _name = name.replace("_FUNCTION", "")
                param_list = [s for s in group_list if s.startswith(
                    _name) and not s.endswith('_FUNCTION')]
                d_list = []
                for param in param_list:
                    _param = param.replace(group, "")
                    param_name = _param[1:]
                    d_list.append(param_name)
                result_dict[__name[1:]] = d_list

        # Display in sorted order
        function_list = list(result_dict.keys())
        function_list.sort()
        for function in function_list:
            self._info(function)
            param_list = result_dict[function]
            param_list.sort()
            for param in param_list:
                self._info(4*" " + param)


def main():
    """@brief Program entry point"""
    uio = UIO()

    try:
        parser = argparse.ArgumentParser(description="A command line interface to a R&S (Hameg) 8112-3 6.5 digit precision multimeter.",
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-d",
                            "--debug",
                            help="Enable debugging.",
                            action='store_true')

        parser.add_argument("-l",
                            "--list_args",
                            help="List the valid commands.",
                            action='store_true')

        parser.add_argument("--port",
                            help="The serial port to use. If left blank the first serial port found will be used.")

        parser.add_argument("-s",
                            "--send",
                            help="Send a command to the meter.",
                            action='store_true')

        parser.add_argument("-f",
                            "--function",
                            help="The required function.")

        parser.add_argument("-p",
                            "--parameter",
                            help="The parameter passed to the function.")

        parser.add_argument("-g",
                            "--get",
                            help="Read any data being sent on the serial port.",
                            action='store_true')

        options = parser.parse_args()

        uio.enableDebug(options.debug)
        dmm = DMM8112(uio)

        if options.list_args:
            dmm.list_args()

        if options.send:
            dmm.connect(options.port)
            dmm.send(options.function, options.parameter)
            dmm.disconnect()

        if options.get:
            try:
                dmm.connect(options.port)
                while True:
                    value = dmm.get_float()
                    uio.info(f"{value}")
            finally:
                dmm.disconnect()

    # If the program throws a system exit exception
    except SystemExit:
        pass
    # Don't print error information if CTRL C pressed
    except KeyboardInterrupt:
        pass
    except Exception as ex:
        logTraceBack(uio)

        if options.debug:
            raise
        else:
            uio.error(str(ex))


if __name__ == '__main__':
    main()
