#!/usr/bin/env python3

import argparse
import requests

from time import sleep, time

from p3lib.uio import UIO
from p3lib.helper import logTraceBack
from p3lib.pconfig import DotConfigManager

from test_equipment.dmm_8112_3 import DMM8112
from test_equipment.cm2100b import CM2100B


class Shelly1PMPlusConfig(DotConfigManager):
    """@brief Responsible for saving the Shelly1PMPlus configuration persistently."""
    CFG_FILE = "Shelly1PMPlus"
    VOLTS_CAL_OFFSET = "VOLTAGE_CAL_OFFSET"
    AMPS_CAL_OFFSET = "AMPS_CAL_OFFSET"
    DEFAULT_UNIT_NAME = "DEFAULT_UNIT_NAME"

    DEFAULT_UNIT_ATTR_DICT = {VOLTS_CAL_OFFSET: 0.0,
                              AMPS_CAL_OFFSET: 0.0}

    DEFAULT_CONFIG = {DEFAULT_UNIT_NAME: DEFAULT_UNIT_ATTR_DICT}

    def __init__(self, uio=None):
        """@brief Constructor.
           @param uio A UIO instance or None"""
        # We don't strip unknown keys from the config because the Shelly unit ID
        # will be unknown until read from the unit.
        super().__init__(Shelly1PMPlusConfig.DEFAULT_CONFIG,
                         uio=uio,
                         stripUnknownKeys=False,
                         filenameOverride=Shelly1PMPlusConfig.CFG_FILE)
        # Store to remove any unused keys
        self.store()


class Shelly1PMPlusInterface(object):
    """@brief Responsible for providing an interface to the Shelly 1PM Plus16A Smart Power Metering Switch."""

    DEV_INFO_NAME_KEY = 'name'
    DEV_INFO_ID_KEY = 'id'
    DEV_INFO_MAC_KEY = 'mac'
    DEV_INFO_MODEL_KEY = 'model'
    DEV_INFO_GEN_KEY = 'gen'
    DEV_INFO_FW_ID_KEY = 'fw_id'
    DEV_INFO_FW_VER_KEY = 'ver'
    DEV_INFO_APP_KEY = 'app'
    DEV_INFO_AUTH_ENABLED_KEY = 'auth_en'
    DEV_INFO_AUTH_DOMAIN_KEY = 'auth_domain'

    STATS_POWER_KEY = 'apower'
    STATS_VOLTAGE_KEY = 'voltage'
    STATS_CURRENT_KEY = 'current'
    STATS_OUTPUT_ON_KEY = 'output'

    def __init__(self, uio=None):
        """@brief Constructor.
           @param uio A UIO instance or None."""
        self._uio = uio
        self._address = None
        self._unit_id = 0
        self._stats_dict = None
        self._dev_info_dict = None
        self._cal_config = Shelly1PMPlusConfig(uio=uio)

    def _debug(self, msg):
        """@brief Display a debug message.
           @param msg The debug message to display."""
        if self._uio:
            self._uio.debug(msg)

    def _info(self, msg):
        """@brief Display an info message.
           @param msg The info message to display."""
        if self._uio:
            self._uio.info(msg)

    def set_address(self, address):
        """@brief Set the address of the shelly 1PM Plus unit.
           @param address The address to display."""
        self._address = address
        # Set to None to ensure we re read the device info
        self._dev_info_dict = None

    def get_response(self, url, params=None):
        """@brief Get a response over the shelly REST interface.
           @param url The URL to connect to the unit."""
        response = requests.get(url, params=params)
        return response.json()

    def _check_address(self):
        """@brief Check that the address has been set."""
        if self._address is None:
            raise Exception(
                "The address of the Shelly 1PM Plus module has not been set.")

    def _check_stats(self):
        """@brief Check that the stats have been read."""
        if self._stats_dict is None:
            raise Exception("Stats not set. Call update_stats() first.")

    def update_stats(self):
        """@brief Update/read the stats dict. This is stored locally.
           @return The stats dict read from the unit."""
        self._check_address()
        if self._dev_info_dict is None:
            self._update_dev_info()
        url = f"http://{self._address}/rpc/Switch.GetStatus?id={self._unit_id}"
        self._stats_dict = self.get_response(url)
        return self._stats_dict

    def _update_dev_info(self):
        """@brief Update/read the device info dict. This is stored locally.
           @return The device info dict read from the unit."""
        self._check_address()
        url = f"http://{self._address}/rpc/Shelly.GetDeviceInfo"
        self._dev_info_dict = self.get_response(url)

        id = self._dev_info_dict[Shelly1PMPlusInterface.DEV_INFO_ID_KEY]
        if id not in self._cal_config.getAttrList():
            print(f"{id} is not in {self._cal_config.getAttrList()}")
            self._cal_config.addAttr(
                id, Shelly1PMPlusConfig.DEFAULT_UNIT_ATTR_DICT)
            self._cal_config.store()

        return self._dev_info_dict

    def turn_on(self, on):
        """@brief Turn the output on/off
           @param on If True turn the output on."""
        self._check_address()
        if on:
            state = 'on'
        else:
            state = 'off'
        url = f"http://{self._address}/relay/0?turn={state}"
        return self.get_response(url)

    def get_unit_id(self):
        """@brief Get the ID of the Shelly 1PM Plus unit we are connected to.
           @return The unique ID of the Shell 1PM Plus unit to which we are connected."""
        unit_id = None
        if self._dev_info_dict:
            if Shelly1PMPlusInterface.DEV_INFO_ID_KEY in self._dev_info_dict:
                unit_id = self._dev_info_dict[Shelly1PMPlusInterface.DEV_INFO_ID_KEY]
            else:
                raise Exception(
                    f'{Shelly1PMPlusInterface.DEV_INFO_ID_KEY} not found in {self._dev_info_dict}')

        else:
            raise Exception(
                "BUG: self._dev_info_dict not set. Call update_stats() before this point.")
        return unit_id

    def _get_unit_cal_dict(self):
        """@return The cal dict for the unit to which we are connected."""
        cal_dict = None
        id = self.get_unit_id()
        if id in self._cal_config.getAttrList():
            cal_dict = self._cal_config.getAttr(id)
        else:
            raise Exception(
                f'{id} not found in {self._cal_config.getAttrList()}')
        return cal_dict

    def get_volts_cal_offset(self):
        """@return the voltage cal offset."""
        cal_dict = self._get_unit_cal_dict()
        return cal_dict[Shelly1PMPlusConfig.VOLTS_CAL_OFFSET]

    def set_volts_cal_offset(self, offset):
        """@brief Save the offset voltage for this unit to the local cal file
                  ~/.config/Shelly1PMPlus.cfg."""
        id = self.get_unit_id()
        cal_dict = self._get_unit_cal_dict()
        cal_dict[Shelly1PMPlusConfig.VOLTS_CAL_OFFSET] = offset
        self._cal_config.addAttr(id, cal_dict)
        self._cal_config.store()

    def get_uncalibrated_voltage(self, read_now=False):
        """@brief Get the voltage read from the Shelly 1PM Plus unit without the calibration
                  correction value applied.
                  update_stats() should be called prior to calling this method to read
                  the stats from the unit unless read_now = True.
           @param read_now If True the stats are read from the device. If not we use the
                           stats from the last update_stats() call."""
        if read_now:
            self.update_stats()
        return self._stats_dict[Shelly1PMPlusInterface.STATS_VOLTAGE_KEY]

    def get_calibrated_voltage(self, read_now=False):
        """@brief Get the voltage read from the Shelly 1PM Plus unit with the calibration
                  correction value applied.
                  update_stats() should be called prior to calling this method to read
                  the stats from the unit unless read_now = True.
           @param read_now If True the stats are read from the device. If not we use the
                           stats from the last update_stats() call."""
        voltage = self.get_uncalibrated_voltage(read_now=read_now)
        cal_offset = self.get_volts_cal_offset()
        # Only add the call offset if we have a value > 0.0
        if voltage > 0.0:
            cal_volts = voltage + cal_offset
        else:
            cal_volts = 0.0
        return cal_volts

    def get_amps_cal_offset(self):
        """@return the amps cal offset."""
        cal_dict = self._get_unit_cal_dict()
        return cal_dict[Shelly1PMPlusConfig.AMPS_CAL_OFFSET]

    def set_amps_cal_offset(self, offset):
        """@brief Save the offset current for this unit to the local cal file
                  ~/.config/Shelly1PMPlus.cfg."""
        id = self.get_unit_id()
        cal_dict = self._get_unit_cal_dict()
        cal_dict[Shelly1PMPlusConfig.AMPS_CAL_OFFSET] = offset
        self._cal_config.addAttr(id, cal_dict)
        self._cal_config.store()

    def get_uncalibrated_current(self, read_now=False):
        """@brief Get the current read (in amps) from the Shelly 1PM Plus unit without the calibration
                  correction value applied. update_stats() may be called prior to calling
                  this method to read the stats from the unit.
                  update_stats() should be called prior to calling this method to read
                  the stats from the unit unless read_now = True.
           @param read_now If True the stats are read from the device. If not we use the
                           stats from the last update_stats() call."""
        if read_now:
            self.update_stats()
        return self._stats_dict[Shelly1PMPlusInterface.STATS_CURRENT_KEY]

    def get_calibrated_current(self, read_now=False):
        """@brief Get the current read (in amps) from the Shelly 1PM Plus unit with the calibration
                  correction value applied. update_stats() may be called prior to calling
                  this method to read the stats from the unit.
                  update_stats() should be called prior to calling this method to read
                  the stats from the unit unless read_now = True.
           @param read_now If True the stats are read from the device. If not we use the
                           stats from the last update_stats() call."""
        amps = self.get_uncalibrated_current(read_now=read_now)
        cal_offset = self.get_amps_cal_offset()
        # Only add the call offset if we have a value > 0.0
        if amps > 0.0:
            cal_amps = amps + cal_offset
        else:
            cal_amps = 0.0
        return cal_amps

    def get_uncalibrated_watts(self, read_now=False):
        """@brief Get the power in watts read from the Shelly 1PM Plus. No calibrated
                  watts value is available.
                  update_stats() should be called prior to calling this method to read
                  the stats from the unit unless read_now = True.
           @param read_now If True the stats are read from the device. If not we use the
                           stats from the last update_stats() call."""
        if read_now:
            self.update_stats()
        return self._stats_dict[Shelly1PMPlusInterface.STATS_POWER_KEY]

    def get_config_file(self):
        """@return The ABS path of the config file."""
        return self._cal_config._getConfigFile()


class CalibrateShelly1PMPlus(object):

    def __init__(self, uio, options, s1PM):
        """@brief Constructor.
           @param uio A UIO instance or None.
           @parm options An instance returned from parser.parse_args().
           @param s1PM A Shelly1PMPlusInterface instance.
           """
        self._uio = uio
        self._options = options
        self._s1PM = s1PM

    def _debug(self, msg):
        """@brief Display a debug message.
           @param msg The debug message to display."""
        if self._uio:
            self._uio.debug(msg)

    def _info(self, msg):
        """@brief Display an info message.
           @param msg The info message to display."""
        if self._uio:
            self._uio.info(msg)

    def _init_volts_dmm(self, dmm8112):
        """@brief Init the voltage DMM.
           @param dmm8112 A DMM8112 instance."""
        dmm8112.connect(self._options.port)

        # Set the meter to periodically return the voltage reading
        dmm8112.send_cmd(DMM8112.GROUP_1,
                         DMM8112.GROUP_1_TRIGGER_FUNCTION,
                         DMM8112.GROUP_1_TRIGGER_SINGLE)

        # Set the meter to read mains voltage
        dmm8112.send_cmd(DMM8112.GROUP_0,
                         DMM8112.GROUP_0_VAC_FUNCTION,
                         DMM8112.GROUP_0_VAC_600V)
        # Set the meter to measure every 500ms
        dmm8112.send_cmd(DMM8112.GROUP_1,
                         DMM8112.GROUP_1_MEAS_TIME_FUNCTION,
                         DMM8112.GROUP_1_MEAS_TIME_1S)
        # Set the meter to periodically return the voltage reading
        dmm8112.send_cmd(DMM8112.GROUP_1,
                         DMM8112.GROUP_1_TRIGGER_FUNCTION,
                         DMM8112.GROUP_1_TRIGGER_AUTO)

    def reset_voltage_cal(self, user_check=False):
        """@brief Reset the stored voltage calibration value.
           @param If True check that the user is ok to reset the calibration value."""
        if user_check:
            self._check_for_cal_values(True, False)

        self._s1PM.update_stats()
        id = self._s1PM.get_unit_id()
        self._s1PM.set_volts_cal_offset(0.0)
        self._uio.info(f"{id}: Reset the voltage calibration offset to 0.0 volts.")

    def _calibrate_voltage(self,
                           seconds=60,
                           calibration_check=False):
        """@brief Perform voltage calibration of the Shelly 1PM Plus unit.
                  This is somewhat problematic because the AC mains voltage
                  is constantly changing by larger or smaller amounts possibly
                  due to changing loads (in house and surrounding houses etc).
                  Therefore we take multiple reading and average the result.
           @param seconds The number of seconds to average  values over.
           @param calibration_check If True do not perform calibration but check the
                  max error in the voltage read.
           @return The average error in the voltage reading if calibration_check = False.
                   The max error if calibration_check = True."""
        if self._options.port is None:
            raise Exception(
                "Please define the serial port connected to the R&S 8112-3 Precision Multimeter to be used to measure the AC voltage.")

        return_value = None
        # We ensure the load is off to get the most stable voltage we can.
        # As the load is a fna heater it's load tends to change as the
        # as it's been on for a while.
        self._s1PM.turn_on(False)
        self._s1PM.update_stats()
        id = self._s1PM.get_unit_id()
        dmm8112 = DMM8112(uio=self._uio)
        try:
            delta_list = []
            self._init_volts_dmm(dmm8112)
            sleep(1)
            start_time = time()
            while time() < start_time + seconds:
                # Read from the DMM first as this takes longer
                dmm_ac_volts = dmm8112.get_float()
                if dmm_ac_volts is not None:
                    # Ignore spurious values, not sure why these occur ???
                    if dmm_ac_volts > 215:
                        self._s1PM.update_stats()
                        if calibration_check:
                            ac_volts = self._s1PM.get_calibrated_voltage()
                        else:
                            ac_volts = self._s1PM.get_uncalibrated_voltage()

                        delta = dmm_ac_volts - ac_volts
                        delta_list.append(delta)
                        secs_left = start_time + seconds - time()
                        self._uio.info(
                            f"HM8112-3 AC volts = {dmm_ac_volts:.3f}, Shelly 1PM Plus AC Volts = {ac_volts:.3f}, delta={delta:.3f}, secs left = {secs_left:.0f}")
                    else:
                        self._uio.warn(
                            f"IGNORED VALUE: dmm_ac_volts = {dmm_ac_volts}")

            if calibration_check:
                max_error = max(delta_list, key=abs)
                self._uio.info(
                    f"{id}: Max voltage measurement error = {max_error:.4f} volts.")
                return_value = max_error

            else:
                average_delta = sum(delta_list) / \
                    len(delta_list) if delta_list else 0
                # We now have the offset to save to the calibration data for this unit.
                self._s1PM.set_volts_cal_offset(average_delta)
                self._uio.info(
                    f"{id}: Saved voltage calibration offset = {average_delta} amps.")
                return_value = average_delta

        finally:
            dmm8112.disconnect()
        return return_value

    def reset_current_cal(self, user_check=False):
        """@brief Reset the stored current calibration value."""
        if user_check:
            self._check_for_cal_values(False, True)

        self._s1PM.update_stats()
        id = self._s1PM.get_unit_id()
        self._s1PM.set_amps_cal_offset(0.0)
        self._uio.info(
            f"{id}: Reset the amps calibration offset to 0.0 volts.")

    def _get_ac_amps(self, cm2100B):
        """@brief Get the AC amps read by the CM2100B clamp meter."""
        amps = None
        reading = cm2100B.get_meter_reading()
        if reading.endswith(" AC A"):
            elems = reading.split()
            if len(elems) > 0:
                try:
                    amps = float(elems[0])
                except ValueError:
                    pass
        else:
            raise Exception("The CM2100B is not set to read AC Amps: '{reading}'")

        if amps is None:
            raise Exception("Failed to read amps from the CM2100B meter.")
        return amps

    def _waitfor_load_current(self, cm2100B):
        """@brief Turn on the load and wait for the load current to settle.
           @param cm2100B A CM2100B instance providing an interface to the CM2100B current clamp meter."""
        current_reading_list = []
        while True:
            amps = self._get_ac_amps(cm2100B)
            self._uio.info(f"Load current = {amps:.2f} Amps.")
            if amps < 5.0:
                self._uio.info("Waiting for load current to reach 5 amps.")
            current_reading_list.insert(0, amps)
            # Keep the last 5 readings in this list
            if len(current_reading_list) > 5:
                current_reading_list.pop()
            # Check if we have had a stable current for the last five readings.
            if len(current_reading_list) == 5:
                minI = min(current_reading_list)
                maxI = max(current_reading_list)
                # If the readings diverge by less than 0.5A
                if maxI - minI < 0.5:
                    self._uio.info(f"Load current is stable at {amps} amps.")
                    break

    def _calibrate_current(self,
                           cm2100b,
                           seconds=60,
                           calibration_check=False,
                           load_off_on_completion=True):
        """@brief Perform current calibration of the Shelly 1PM Plus unit.
                  This is somewhat problematic because the AC mains voltage
                  is constantly changing by larger or smaller amounts and the load
                  we need to apply to calibrate it. A 2kW fan heater is used to
                  provide the load required to calibrate the current.
           @param cmb2100b A CM2100B instance connected to a CM2100b meter over bluetooth.
           @param seconds The number of seconds to average values over.
           @param calibration_check If True do not perform calibration but check the
                  max error in the current read.
           @param load_off_on_completion If True turn the load off on completion.
           @return The average error in the current reading if calibration_check = False.
                   The max error if calibration_check = True."""
        try:
            # Read some stats from the Shelly 1PM Plus module.
            self._s1PM.update_stats()
            # Get the id of this unit.
            id = self._s1PM.get_unit_id()
            # We ensure the load is on as we need a load current in order to start the calibration process.
            self._s1PM.turn_on(True)
            # Wait for the load current to stablise.
            self._waitfor_load_current(cm2100b)

            delta_list = []

            start_time = time()
            while time() < start_time + seconds:
                dmm_ac_amps = self._get_ac_amps(cm2100b)
                if dmm_ac_amps is not None:
                    self._s1PM.update_stats()
                    if calibration_check:
                        ac_amps = self._s1PM.get_calibrated_current()
                    else:
                        ac_amps = self._s1PM.get_uncalibrated_current()

                    delta = dmm_ac_amps - ac_amps
                    delta_list.append(delta)
                    secs_left = start_time + seconds - time()
                    self._uio.info(
                        f"CM2100B AC Amps = {dmm_ac_amps:.3f}, Shelly 1PM Plus AC Amps = {ac_amps:.3f}, delta={delta:.4f}, secs left = {secs_left:.0f}")
                else:
                    self._uio.warn(
                        f"IGNORED VALUE: CM2100B AC Amps = {dmm_ac_amps}")

            if calibration_check:
                max_error = max(delta_list, key=abs)
                self._uio.info(
                    f"{id}: Max current measurement error = {max_error:.4f} amps.")
                return_value = max_error

            else:
                average_delta = sum(delta_list) / \
                    len(delta_list) if delta_list else 0
                # We now have the offset to save to the calibration data for this unit.
                self._s1PM.set_amps_cal_offset(average_delta)
                self._uio.info(
                    f"{id}: Saved current calibration offset = {average_delta} amps.")
                return_value = average_delta

        finally:
            if load_off_on_completion:
                # We ensure the load is off on completion.
                self._s1PM.turn_on(False)
        return return_value

    def _performVoltageCalibration(self):
        """@brief Perform the voltage calibration process."""
        # Reset stored voltage calibration to 0.0
        self.reset_voltage_cal()
        # Get the max voltage reading error without calibration (60 readings)
        uncalibrated_max_error = self._calibrate_voltage(calibration_check=True)
        # Calibrate the Shelly 1PM Plus voltage reading.
        self._calibrate_voltage(calibration_check=False)
        # Get the max voltage reading error with calibration (60 readings)
        calibrated_max_error = self._calibrate_voltage(calibration_check=True)

        percentage_improvement = (
            abs(uncalibrated_max_error) / abs(calibrated_max_error))*100.0
        self._cal_msg_lines.append(
            f"Un calibrated Voltage error = {uncalibrated_max_error} volts")
        self._cal_msg_lines.append(
            f"Calibrated Voltage error    = {calibrated_max_error} volts")
        self._cal_msg_lines.append(
            f"The calibration process improved the voltage reading accuracy by {percentage_improvement:.0f} %.")

    def _performCurrentCalibration(self):
        """@brief Perform the current calibration process."""
        try:
            cm2100b = CM2100B(uio=self._uio)
            cm2100b.connect(self._options.mac)
            # Reset stored voltage calibration to 0.0
            self.reset_current_cal()
            # Get the max current reading error with calibration (60 readings)
            uncalibrated_max_error = self._calibrate_current(cm2100b,
                                                             calibration_check=True,
                                                             load_off_on_completion=False)
            # Calibrate the Shelly 1PM Plus current reading.
            self._calibrate_current(cm2100b,
                                    calibration_check=False,
                                    load_off_on_completion=False)
            # Get the max current reading error with calibration (60 readings)
            calibrated_max_error = self._calibrate_current(cm2100b,
                                                           calibration_check=True)

            percentage_improvement = (abs(uncalibrated_max_error) / abs(calibrated_max_error))*100.0
            self._cal_msg_lines.append(f"Un calibrated current error = {uncalibrated_max_error} amps.")
            self._cal_msg_lines.append(f"Calibrated current error    = {calibrated_max_error} amps.")
            self._cal_msg_lines.append(f"The calibration process improved the current reading accuracy by {percentage_improvement:.0f} %.")

        finally:
            # We ensure the load is off on completion.
            self._s1PM.turn_on(False)
            cm2100b.disconnect()

    def _check_for_cal_values(self, cal_volts, amps_cal):
        """@brief Check for any existing calibration values and ask user for confirmation if values already exist.
           @param cal_volts If True check voltage cal value.
           @param amps_cal If True check current cal value."""
        ask_user = False
        self._s1PM.update_stats()
        if cal_volts:
            volts_cal_offset = self._s1PM.get_volts_cal_offset()
            self._uio.info(f"Existing voltage calibration offset = {volts_cal_offset:.3f} volts.")
            if volts_cal_offset != 0:
                ask_user = True

        elif amps_cal:
            amps_cal_offset = self._s1PM.get_amps_cal_offset()
            self._uio.info(f"Existing current calibration offset = {amps_cal_offset:.3f} amps.")
            if amps_cal_offset != 0:
                ask_user = True

        else:
            volts_cal_offset = self._s1PM.get_volts_cal_offset()
            self._uio.info(f"Existing voltage calibration offset = {volts_cal_offset:.3f} volts.")
            amps_cal_offset = self._s1PM.get_amps_cal_offset()
            self._uio.info(f"Existing current calibration offset = {amps_cal_offset:.3f} amps.")
            if volts_cal_offset != 0 or amps_cal_offset != 0:
                ask_user = True

        if ask_user:
            proceed = self._uio.getBoolInput("Are you sure you wish to overwrite the existing calibration offsets ? [y]/[n]")
            if not proceed:
                raise Exception("User aborted calibration process.")

    def _check_cmd_line_args(self):
        """@brief Check tha the command line args are valid."""
        # If only calibrating voltage
        if self._options.volts:
            check_port = True

        elif self._options.amps:
            check_mac = True

        else:
            check_port = True
            check_mac = True

        if check_port and self._options.port is None:
            raise Exception("Use -p/--port to define the serial port connected to the R&S 8112-3 Precision Multimeter.")

        if check_mac and self._options.mac is None:
            raise Exception("Use -m/--mac to define the bluetooth MAC address of the OWON CM2100B AC/DC Clamp Ammeter.")

    def performCalibration(self):
        """@brief Perform calibration on the Shelly 1PM Plus unit."""
        self._check_for_cal_values(self._options.volts, self._options.amps)
        self._check_cmd_line_args()

        self._cal_msg_lines = []
        if self._options.volts:
            self._performVoltageCalibration()

        elif self._options.amps:
            self._performCurrentCalibration()

        else:
            # We perform current cal first because the CM2100B meter has to be set
            # into bluetooth mode at the start of the cal process. IT drops out of
            # bluetooth mode after a period of time. The voltage cal time may mean
            # that by the time the current cal process starts the CM2100B drops out
            # of bluetooth mode. So we run the current cal first.
            self._performCurrentCalibration()
            self._performVoltageCalibration()

        for line in self._cal_msg_lines:
            self._uio.info(line)
        cfg_file = self._s1PM.get_config_file()
        self._uio.info(f"Shelly 1PM Plus config file: {cfg_file}")


def main():
    """@brief Program entry point"""
    uio = UIO()

    try:
        parser = argparse.ArgumentParser(description="Shelly 1PM Plus device interface.",
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument(
            "-d", "--debug",   action='store_true', help="Enable debugging.")
        parser.add_argument(
            "-a", "--address", help="The address of the Shelly 1PM Plus unit on the LAN.", default=None, required=True)
        parser.add_argument(
            "--on",            action='store_true', help="Turn Shelly 1PM Plus on.")
        parser.add_argument(
            "--off",           action='store_true', help="Turn Shelly 1PM Plus off.")
        parser.add_argument("-s", "--stats",   action='store_true',
                            help="Read the state from the Shelly 1PM Plus unit.")

        parser.add_argument("-c", "--calibrate",  action='store_true',
                            help="Perform the Shelly 1PM Plus module calibration. This will update a local config file with the voltage and current offsets for the connected Shelly 1PM Plus module.")
        parser.add_argument(
            "--volts",            action='store_true', help="Only calibrate voltage.")
        parser.add_argument(
            "--amps",             action='store_true', help="Only calibrate amps.")
        parser.add_argument(
            "-p", "--port",       help="The serial port to which a R&S 8112-3 Precision Multimeter. This is used to calibrate the AC voltage.", default=None)
        parser.add_argument(
            "-m", "--mac",        help="The bluetooth MAC address of the OWON CM2100B meter used to read the AC current value. This is used to calibrate the AC current.", default=None)
        parser.add_argument("--reset_cal_v",     action='store_true',
                            help="Reset voltage calibration offset to 0.0 volts.")
        parser.add_argument("--reset_cal_c",     action='store_true',
                            help="Reset current calibration offset to 0.0 amps.")

        options = parser.parse_args()

        uio.enableDebug(options.debug)

        ss = Shelly1PMPlusInterface(uio=uio)
        ss.set_address(options.address)

        if options.on:
            ss.turn_on(True)
            uio.info(f"{options.address}: Turned ON")

        elif options.off:
            ss.turn_on(False)
            uio.info(f"{options.address}: Turned OFF")

        elif options.stats:
            stats_dict = ss.update_stats()
            cal_volts = ss.get_calibrated_voltage()
            cal_amps = ss.get_calibrated_current()

            uio.info(f"WATTS:   {stats_dict[Shelly1PMPlusInterface.STATS_POWER_KEY]} (un-calibrated)")
            uio.info(f"VOLTS:   {cal_volts:.1f} (calibrated), {stats_dict[Shelly1PMPlusInterface.STATS_VOLTAGE_KEY]} un-calibrated")
            uio.info(f"AMPS:    {cal_amps:.2f} (calibrated),  {stats_dict[Shelly1PMPlusInterface.STATS_CURRENT_KEY]}  un-calibrated")

        elif options.calibrate:
            calS1PMP = CalibrateShelly1PMPlus(uio, options, ss)
            calS1PMP.performCalibration()

        elif options.reset_cal_v:
            calS1PMP = CalibrateShelly1PMPlus(uio, options, ss)
            calS1PMP.reset_voltage_cal(user_check=True)

        elif options.reset_cal_c:
            calS1PMP = CalibrateShelly1PMPlus(uio, options, ss)
            calS1PMP.reset_current_cal(user_check=True)

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
