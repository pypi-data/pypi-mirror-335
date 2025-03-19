#!/usr/bin/env python3

import argparse
import asyncio
import queue
import threading
from time import time, sleep

from bleak import BleakClient, BleakScanner

from p3lib.uio import UIO
from p3lib.helper import logTraceBack


class CM2100B(object):
    """@brief Responsible for an interface to the OWON CM2100B current clamp meter."""

    # Define the terminal service and characteristic UUIDs (based on your output)
    TERMINAL_SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
    TERMINAL_CHARACTERISTIC_UUID = "0000fff4-0000-1000-8000-00805f9b34fb"  # Choose a relevant characteristic

    INF_OPEN = -32767

    MODE_DC_VOLTS = 0b00000000
    MODE_AC_VOLTS = 0b00000001
    MODE_AC_AMPS = 0b00000011
    MODE_DC_AMPS = 0b00000010
    MODE_NCV = 0b00001101
    MODE_OHMS = 0b00000100
    MODE_CAPACITANCE = 0b00000101
    MODE_DIODE = 0b00001010
    MODE_CONTINUITY = 0b00001011
    MODE_FREQUENCY = 0b00000110
    MODE_PERCENT = 0b00000111
    MODE_TEMP_C = 0b00001000
    MODE_TEMP_F = 0b00001001
    MODE_HFE = 0b00001100

    SHUTDOWN_CMD = "SHUTDOWN_CMD"

    BLUETOOTH_DEV_NAME = "BDM"

    FUNCTION_STRING = "FUNCTION_STRING"
    READING_VALUE = "READING_VALUE"
    DISCONNECTED_MSG = "Disconnected: "

    def __init__(self, uio=None):
        """@brief Constructor.
           @param uio A UIO instance or None. If a UIO instance is passed then debug messages
                  may be displayed when the _debug(msg) method is called."""
        self._uio = uio
        self._to_cm2100b_queue = queue.Queue()
        self._from_cm2100b_queue = queue.Queue()

    def _info(self, msg):
        if self._uio:
            self._uio.info(msg)

    def _debug(self, msg):
        if self._uio:
            self._uio.debug(msg)

    async def _connect_to_terminal_service(self):
        """@brief Connect to the device and interact with the terminal service."""
        self._from_cm2100b_queue.put(f"Connecting to: {self._dev_address}")
        start_time = time()
        async with BleakClient(self._dev_address) as client:
            elapsed_secs = time() - start_time
            self._from_cm2100b_queue.put(f"Connected: Took {elapsed_secs:.1f} seconds.")

            # Subscribe to the terminal characteristic for notifications (if applicable)
            await client.start_notify(CM2100B.TERMINAL_CHARACTERISTIC_UUID, self._notification_handler)

            # Wait here for a shutdown command
            while True:
                try:
                    cmd = self._to_cm2100b_queue.get_nowait()
                    if cmd == CM2100B.SHUTDOWN_CMD:
                        break
                except queue.Empty:
                    pass

                await asyncio.sleep(.2)

        await client.disconnect()
        self._from_cm2100b_queue.put(CM2100B.DISCONNECTED_MSG)

    def _notification_handler(self, sender: int, data: bytearray):
        """@brief Notification handler function to handle incoming data from the terminal.
           @param sender The handle to the sender.
           @param data The data received on the blue tooth connection."""
        if len(data) == 6:
            # convert bytes to 'reading' array
            reading = []
            reading.append(data[1] << 8 | data[0])
            reading.append(data[3] << 8 | data[2])
            reading.append(data[5] << 8 | data[4])

            # Extract data items from first field
            function = (reading[0] >> 6) & 0x0f
            scale = (reading[0] >> 3) & 0x07
            decimal = reading[0] & 0x07

            # Extract and convert measurement value (sign)
            if (reading[2] < 0x7fff):
                measurement = reading[2]
            else:
                measurement = -1 * (reading[2] & 0x7fff)

            value = measurement / float(10**decimal)
            func_str = self._get_func_str(function, scale, measurement)
            reading_dict = {}
            reading_dict[CM2100B.FUNCTION_STRING] = func_str
            reading_dict[CM2100B.READING_VALUE] = value
            self._from_cm2100b_queue.put(reading_dict)

    def _get_func_str(self, function, scale, measurement):
        """@brief Get the function string.
           @param function The function id.
           @param scale Scaling factor.
           @param measurement The measurement value."""

        if function == CM2100B.MODE_DC_VOLTS:
            if scale == 3:
                funct_s = "DC mV"
            elif scale == 4:
                funct_s = "DC V"
            else:
                funct_s = "??DC V"

        elif function == CM2100B.MODE_AC_VOLTS:
            if scale == 4:
                funct_s = "AC V"
            elif scale == 3:
                funct_s = "AC mV"
            else:
                funct_s = "??AC V"

        elif function == CM2100B.MODE_AC_AMPS:
            if scale == 2:
                funct_s = "AC µA"
            elif scale == 3:
                funct_s = "AC mA"
            elif scale == 4:
                funct_s = "AC A"
            else:
                funct_s = "??AC A"

        elif function == CM2100B.MODE_DC_AMPS:
            if scale == 2:
                funct_s = "DC µA"
            elif scale == 3:
                funct_s = "DC mA"
            elif scale == 4:
                funct_s = "DC A"
            else:
                funct_s = "??DC A"

        elif function == CM2100B.MODE_NCV:
            funct_s = "NCV"

        elif function == CM2100B.MODE_OHMS:
            if measurement == CM2100B.INF_OPEN:
                funct_s = "Ohms Open"
            else:
                if scale == 4:
                    funct_s = "Ohms"
                elif scale == 5:
                    funct_s = "K Ohms"
                elif scale == 6:
                    funct_s = "M Ohms"
                else:
                    funct_s = "??Ohms"

        elif function == CM2100B.MODE_CAPACITANCE:
            if scale == 1:
                funct_s = "nF"
            elif scale == 2:
                funct_s = "uF"
            else:
                funct_s = "??Farads"

        elif function == CM2100B.MODE_DIODE:
            if measurement == CM2100B.INF_OPEN:
                funct_s = "Diode Open"
            else:
                funct_s = "Diode"

        elif function == CM2100B.MODE_CONTINUITY:
            if measurement == CM2100B.INF_OPEN:
                funct_s = "Continuity Open"
            else:
                funct_s = "Continuity Closed"

        elif function == CM2100B.MODE_FREQUENCY:
            funct_s = "Hz"  # frequency mode

        elif function == CM2100B.MODE_PERCENT:
            funct_s = "%"  # percent mode

        elif function == CM2100B.MODE_TEMP_C:
            funct_s = "Deg C"

        elif function == CM2100B.MODE_TEMP_F:
            funct_s = "Deg F"

        elif function == CM2100B.MODE_HFE:
            funct_s = "HFE"

        else:
            funct_s = "???"

        return funct_s

    async def _discover_ble_devices(self):
        """@brief Function to discover BLE devices."""
        devices = await BleakScanner.discover()
        for device in devices:
            dev_dict = {}
            dev_dict[device.name] = device.address
            self._from_cm2100b_queue.put(dev_dict)

    async def _create_bluetooth_scan_task(self):
        task = asyncio.create_task(self._discover_ble_devices())
        await task

    async def _start_reading(self):
        """@brief Called to start the process of reading data from the CM2100B."""
        task = asyncio.create_task(self._connect_to_terminal_service())
        await task

    # The following methods are outside the asyncio task

    def start_reading(self):
        """@brief Called to start the process of reading values from the CM2100B meter."""
        loop = asyncio.new_event_loop()  # Create a new event loop for this thread
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._start_reading())

    def connect(self, mac_address):
        """@brief Read the current value measured by the CM2100B meter."""
        self._dev_address = mac_address
        self._info("Connecting to CM2100B AC/DC Clamp Meter.")
        # Start thread in background to read data from the DMM
        thread = threading.Thread(target=self.start_reading, daemon=True)
        thread.start()
        while True:
            try:
                rx_obj = self._from_cm2100b_queue.get_nowait()
                self._info(rx_obj)
                if isinstance(rx_obj, str):
                    if rx_obj.startswith('Connected:'):
                        self._info("Connected to CM2100B AC/DC Clamp Meter.")
                        break

            except queue.Empty:
                sleep(0.1)

    def start_dev_search(self):
        """@brief Called to start the process of discovering bluetooth devices"""
        asyncio.run(self._create_bluetooth_scan_task())

    def scan(self):
        """@brief Scan for bluetooth devices."""
        self._info("Scanning for CM2100B bluetooth devices...")
        self.start_dev_search()
        while True:
            try:
                rx_obj = self._from_cm2100b_queue.get_nowait()
                self._debug(f"RX: {rx_obj}")
                if isinstance(rx_obj, dict) and CM2100B.BLUETOOTH_DEV_NAME in rx_obj:
                    rx_dict = rx_obj
                    mac_address = rx_dict[CM2100B.BLUETOOTH_DEV_NAME]
                    self._info(f"CM2100B MAC address: {mac_address}")
                    break

            except queue.Empty:
                sleep(0.1)

    def get_meter_reading(self, waitfor_next=True):
        """@brief Get the amps measured by the meter.
                  connect() must be called successfully before calling this method.
           @return The meter reading. The number is returned first followed
                   by the string indicating the meter switch setting."""
        return_value = None
        if waitfor_next:
            while not self._from_cm2100b_queue.empty():
                self._from_cm2100b_queue.get()
        while self._from_cm2100b_queue.empty():
            sleep(0.1)
        response_dict = self._from_cm2100b_queue.get()
        if CM2100B.FUNCTION_STRING in response_dict and \
           CM2100B.READING_VALUE in response_dict:
            func_str = response_dict[CM2100B.FUNCTION_STRING]
            return_value = response_dict[CM2100B.READING_VALUE]

        else:
            raise Exception('CM2100B read error.')

        return f"{return_value} {func_str}"

    def show(self, mac_address):
        """@brief Show any value read from the CM2100B.
           @param mac_address The CM2100B mac address."""
        try:
            self.connect(mac_address)
            while True:
                reading = self.get_meter_reading()
                self._info(f"{reading}")

        finally:
            self.disconnect()

    def disconnect(self):
        """@brief Disconnect from a CM2100B that we previously connected to."""
        self._to_cm2100b_queue.put(CM2100B.SHUTDOWN_CMD)
        # Wait to receive confirmation that the bluetooth
        # connection has shut down.
        start_time = time()
        while True:
            if not self._from_cm2100b_queue.empty():
                msg = self._from_cm2100b_queue.get()
                if isinstance(msg, str):
                    if msg.startswith(CM2100B.DISCONNECTED_MSG):
                        break
            if time() > start_time+15:
                raise Exception("Failed to disconnect from CM2100B AC/DC Clamp Ammeter.")
            sleep(0.25)

        self._info("Disconnected from CM2100B AC/DC Clamp Meter.")


def main():
    """@brief Program entry point"""
    uio = UIO()

    try:
        parser = argparse.ArgumentParser(description="An interface to the CM2100B current clamp DMM.",
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-d", "--debug",   action='store_true', help="Enable debugging.")
        parser.add_argument("-m", "--mac",     help="The bluetooth MAC address of the CM2100B meter.", default=None)
        parser.add_argument("-r", "--read",    action='store_true', help="Read values from the CM2100B over bluetooth.")
        parser.add_argument("-l", "--list",    action='store_true', help="List bluetooth devices.")

        options = parser.parse_args()

        uio.enableDebug(options.debug)

        if options.list:
            cm2100b = CM2100B(uio=uio)
            cm2100b.scan()

        elif options.read:
            cm2100b = CM2100B(uio=uio)
            cm2100b.show(options.mac)

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
