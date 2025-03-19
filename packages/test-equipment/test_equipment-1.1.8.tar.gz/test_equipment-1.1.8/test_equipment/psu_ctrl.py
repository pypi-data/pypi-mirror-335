#!/usr/bin/env python3

import argparse

from p3lib.uio import UIO
from p3lib.helper import logTraceBack
from p3lib.pconfig import ConfigManager

from test_equipment.psu import PSUFactory, ETMXXXXP
from test_equipment.serial_helper import SerialPortFinder
from test_equipment.visa_helper import VisaDev


class PersistentPSUCtrlConfig(object):
    """@brief Responsible for saving the PSU configuratiion persistently."""
    CFG_FILE = "psu_ctrl.cfg"
    PSU_TYPE = "PSU_TYPE"
    PSU_CONNECTION_STRING = "PSU_CONNECTION_STRING"

    DEFAULT_CONFIG = {PSU_TYPE: ETMXXXXP.PSU_TYPE,
                      PSU_CONNECTION_STRING: ""}

    def __init__(self, uio):
        """@brief Constructor
           @param uio A UIO instance handling user input and output (E.G stdin/stdout or a GUI)
           @param options An instance of the OptionParser command line options."""
        self._uio = uio
        self._configManager = ConfigManager(
            self._uio, PersistentPSUCtrlConfig.CFG_FILE, PersistentPSUCtrlConfig.DEFAULT_CONFIG)
        self._configManager.load(True)
        self._configManager.store()

    def _enterPSUType(self):
        """@brief Allow the user to configure the connected PSU type."""
        lines = []
        lines.append("Supported Power Supplies")
        lines.append("Type   Description")
        for psu in PSUFactory.SUPPORTED_PSU_LIST:
            self._uio.info("{: <7}{}".format(psu.PSU_TYPE, psu.PSU_NAME))
        self._configManager.inputDecInt(
            PersistentPSUCtrlConfig.PSU_TYPE, "PSU TYPE", minValue=1, maxValue=PSUFactory.MAX_PSU_TYPE)

    def _enterPSUDeviceString(self):
        """@brief Allow the user to configure the PSU device String."""
        # Show VISA devices available
        if VisaDev.Show(self._uio) == 0:
            # If no VISA devices are available then show serial devices available.
            SerialPortFinder.ShowPorts(self._uio)
        self._configManager.inputStr(
            PersistentPSUCtrlConfig.PSU_CONNECTION_STRING, "PSU connection string", False)

    def _editConfig(self, key):
        """@brief Edit a single config parameter/attribute.
           @param key The dictionary key to edit."""

        if key == PersistentPSUCtrlConfig.PSU_TYPE:
            self._enterPSUType()

        elif key == PersistentPSUCtrlConfig.PSU_CONNECTION_STRING:
            self._enterPSUDeviceString()

    def getAttr(self, key, allowModify=True):
        """@brief Get an attribute value.
           @param key The key for the value we're after.
           @param allowModify If True and the configuration has been modified
                  since the last read by the caller then the config will be reloaded."""
        return self._configManager.getAttr(key, allowModify=allowModify)

    def config(self):
        """@brief Allow the user to change the config."""
        self._configManager.configure(self._editConfig)


class PSU(object):
    """@brief Allow the user to set and get PSU status."""

    def __init__(self, uio, options):
        """@brief Constructor
           @param uio A UIO instance handling user input and output (E.G stdin/stdout or a GUI)
           @param options An instance of the OptionParser command line options."""
        self._uio = uio
        self._options = options
        self._pPSUConfig = PersistentPSUCtrlConfig(self._uio)
        self._psuType = self._pPSUConfig.getAttr(
            PersistentPSUCtrlConfig.PSU_TYPE)
        self._psuConnectionString = self._pPSUConfig.getAttr(
            PersistentPSUCtrlConfig.PSU_CONNECTION_STRING)
        self._psu = PSUFactory.GetInstance(self._psuType, uio=self._uio)

    def _getCfgAttr(self, attrName):
        """@brief Get a config attribute
           @param attrName The name of the attribute
           @return the Attr value."""
        return self._pPSUConfig.getAttr(attrName)

    def setOutput(self, on):
        """@brief Set output on/off.
           @param on If True then set output on. If False set output off."""

        serialDevice = self._getSerialDevice()

        self._psu.connect(serialDevice)

        self._psu.selectOutput(self._options.output)
        self._psu.enableOutput(on)

        if on:
            self._psu.setVolts(self._options.volts)
            self._uio.info(
                "Set PSU voltage to {:.2f} volts.".format(self._options.volts))
            self._psu.setAmps(self._options.amps)
            self._uio.info(
                "Set PSU current limit to {:.2f} amps.".format(self._options.amps))

        self._psu.switchOn(on)
        if on:
            self._uio.info("Set PSU On")
        else:
            self._uio.info("Set PSU Off")

        self._psu.disconnect()

    def _getSerialDevice(self):
        """@brief Get the device string to be used to connect to the device.
           @return The Linux serial device string or the VISA device string."""
        if self._psuConnectionString.endswith(":INSTR"):
            # In this case this device string is the VISA device string
            serialDevice = self._psuConnectionString
        else:
            # In this case we get the Linux serial interface /dev
            serialDevice = SerialPortFinder.GetDevice(
                self._psuConnectionString)

        return serialDevice

    def readPower(self):
        """@brief Read the current/power that is being drawn from the PSU."""

        # serialDevice = self._getDeviceString()
        serialDevice = self._getSerialDevice()

        self._psu.connect(serialDevice)

        volts = self._psu.getVolts()
        amps = self._psu.getLoadAmps()
        self._psu.disconnect()
        self._uio.info("Voltage: {:.3f} volts".format(volts))
        self._uio.info("Amps:    {:.3f} volts".format(amps))
        self._uio.info("Power:   {:.3f} Watts".format(volts*amps))

    def config(self):
        """@brief Allow the user to configure the test station attributes.
           @return None"""
        self._pPSUConfig.config()


def main():
    """@brief Program entry point"""
    uio = UIO()

    try:
        parser = argparse.ArgumentParser(
            description="Control different PSU types.", formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument(
            "-d", "--debug",  help="Enable debugging.", action='store_true')
        parser.add_argument(
            "-c", "--config", help="Configure the PSU parameters.", action='store_true')
        parser.add_argument(
            "-v", "--volts",  help="Set PSU voltage (default=3.3).",        type=float, default=3.3)
        parser.add_argument(
            "-a", "--amps",   help="Set PSU current limit (default=1.0).",  type=float, default=1.0)
        parser.add_argument(
            "-o", "--output", help="The PSU output to use (default=1).",    type=int, default=1)
        parser.add_argument(
            "--on",           help="Turn the output on.",                   action='store_true')
        parser.add_argument(
            "--off",          help="Turn the output off.",                  action='store_true')
        parser.add_argument(
            "-r", "--read",   help="Read the output current/power.",        action='store_true')

        lines = []
        lines.append("Supported Power Supplies")
        lines.append("Type   Description")
        for psu in PSUFactory.SUPPORTED_PSU_LIST:
            lines.append("{: <7}{}".format(psu.PSU_TYPE, psu.PSU_NAME))
        parser.epilog = ("\n".join(lines))

        options = parser.parse_args()

        uio.enableDebug(options.debug)
        psu = PSU(uio, options)

        if options.config:
            psu.config()

        else:
            if options.on:
                psu.setOutput(True)

            elif options.off:
                psu.setOutput(False)

            if options.read:
                psu.readPower()

    # If the program throws a system exit exception
    except SystemExit:
        pass
    # Don't print error information if CTRL C pressed
    except KeyboardInterrupt:
        pass
    except Exception as ex:
        logTraceBack(uio)
        raise

        if options.debug:
            raise
        else:
            uio.error(str(ex))


if __name__ == '__main__':
    main()
