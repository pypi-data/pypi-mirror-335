import serial
import logging

from time import sleep

from test_equipment.serial_helper import SerialPortFinder
from test_equipment.visa_helper import VisaDev

from pymodbus.client.serial import ModbusSerialClient
from pymodbus.framer import FramerType


class PSUBase(object):
    """@brief Define a generalised interface to power supply."""

    def __init__(self, type, name, uio):
        """@brief Construct a power supply interface.
           @param type The type of power supply (an int value).
           @param name The name of the power supply type (a str value).
           @param uio A UIO instance or None. If a UIO instance is passed then debug messages
                  may be displayed when the _debug(msg) method is called."""
        self._uio = uio
        if type is None:
            raise NotImplementedError('The power supply type must be defined.')

        if name is None:
            raise NotImplementedError('The power supply name must be defined.')
        self._type = type
        self._name = name

    def _debug(self, msg):
        """@brief Display a debug message."""
        if self._uio:
            self._uio.debug(msg)

    def connect(self, dev):
        """@brief Connect to the PSU.
           @param dev A device connect string. E.G serial port."""
        raise NotImplementedError(
            "connect() method not implemented by {}".format(self.__class__.__name__))

    def disconnect(self):
        """@brief Disconnect from the power supply."""
        raise NotImplementedError(
            "disconnect() method not implemented by {}".format(self.__class__.__name__))

    def selectOutput(self, output):
        """@brief Select PSU output.
           @param output The output to select. An integer value."""
        raise NotImplementedError(
            "selectOutput() method not implemented by {}".format(self.__class__.__name__))

    def setVolts(self, voltage):
        """@brief Set the currently selected output voltage.
           @param voltage The voltage in volts."""
        raise NotImplementedError(
            "setVolts() method not implemented by {}".format(self.__class__.__name__))

    def setAmps(self, current):
        """@brief Set the selected output current limit.
           @param current The current limit in amps."""
        raise NotImplementedError(
            "setAmps() method not implemented by {}".format(self.__class__.__name__))

    def enableOutput(self, on):
        """@brief Enable a previously selected output.
           @param on If True turn output on when apply switchOn is called."""
        raise NotImplementedError(
            "enableOutput() method not implemented by {}".format(self.__class__.__name__))

    def switchOn(self, on):
        """@brief Turn on/off all previously enabled outputs.
           @param on If True turn output/s on."""
        raise NotImplementedError(
            "switchOn() method not implemented by {}".format(self.__class__.__name__))

    def getVolts(self):
        """@brief Get the selected output voltage.
           @return The selected output voltage in volts."""
        raise NotImplementedError(
            "getVolts() method not implemented by {}".format(self.__class__.__name__))

    def getLimitAmps(self):
        """@brief Get the selected output current limit.
           @return The selected output current limit in amps."""
        raise NotImplementedError(
            "getLimitAmps() method not implemented by {}".format(self.__class__.__name__))

    def getLoadAmps(self):
        """@brief Get the selected output load current.
           @return The selected output load current in amps."""
        raise NotImplementedError(
            "getLoadAmps() method not implemented by {}".format(self.__class__.__name__))


class DummyPSU(object):
    """@brief Dummy power supply chamber for dev puposes."""

    PSU_TYPE = 0
    PSU_NAME = "Dummy PSU"

    def __init__(self, uio=None):
        """@brief Construct a power supply interface.
           @param uio A UIO instance or None. If a UIO instance is passed then debug messages
                  may be displayed when the _debug(msg) method is called."""
        super().__init__(DummyPSU.PSU_TYPE, DummyPSU.PSU_NAME, uio=uio)

    def connect(self, dev):
        """@brief Connect to the PSU.
           @param dev A device connect string. E.G serial port."""
        self._debug("DummyPSU.connect()")

    def disconnect(self):
        """@brief Disconnect from the power supply."""
        self._debug("DummyPSU.disconnect()")

    def selectOutput(self, output):
        """@brief Select PSU output.
           @param output The output to select. An integer value."""
        self._debug("DummyPSU.selectOutput()")

    def setVolts(self, voltage):
        """@brief Set the currently selected output voltage.
           @param voltage The voltage in volts."""
        self._debug("DummyPSU.setVolts()")

    def setAmps(self, current):
        """@brief Set the selected output current limit.
           @param current The current limit in amps."""
        self._debug("DummyPSU.setAmps()")

    def enableOutput(self, on):
        """@brief Enable a previously selected output.
           @param on If True turn output on when apply switchOn is called."""
        self._debug("DummyPSU.enableOutput()")

    def switchOn(self, on):
        """@brief Turn on/off all previously enabled outputs.
           @param on If True turn output/s on."""
        self._debug("DummyPSU.switchOn()")

    def getVolts(self):
        """@brief Get the selected output voltage.
           @return The selected output voltage in volts."""
        self._debug("DummyPSU.getVolts()")
        return 3.3

    def getLimitAmps(self):
        """@brief Get the selected output current limit.
           @return The selected output current limit in amps."""
        self._debug("DummyPSU.getLimitAmps()")
        return 1.0

    def getLoadAmps(self):
        """@brief Get the selected output load current.
           @return The selected output load current in amps."""
        self._debug("DummyPSU.getLoadAmps()")
        return 1.0


class HMP2030PSU(PSUBase):
    """@brief Responsible for providing an interface to R&S/Hameg HMP2030 PSU's.

              - This requires the use of the pyvisa python module.
              - This python module was tested with the USB interface selected on
                the instrument (Menu button / Interface / Select Interface)."""
    PSU_TYPE = 1
    PSU_NAME = "HMP2030 PSU"

    MIN_VOLTS = 0.0
    MAX_VOLTS = 32.0
    MIN_AMPS = 0.0
    MAX_AMPS = 5.0  # The maximum channel output current for HMP2030 PSU's.
    # HMP2030 PSU supports 5A on all channels.
    # This reduces to 2.5 amps at max voltage.
    # HMP2020 PSU supports 10A on channel 1 and 2.5A on channel 2.

    def __init__(self, uio=None):
        """@brief Construct a power supply interface.
           @param uio A UIO instance or None. If a UIO instance is passed then debug messages
                  may be displayed when the _debug(msg) method is called."""
        super().__init__(HMP2030PSU.PSU_TYPE, HMP2030PSU.PSU_NAME, uio=uio)
        self._visaDevice = None

    def connect(self, dev):
        """@brief Connect to the PSU.
           @param dev A device connect string. E.G serial port."""
        self._visaDevice = VisaDev(uio=self._uio)
        self._visaDevice.connect(dev)
        self._visaDevice.query("*IDN?")

    def disconnect(self):
        """@brief Disconnect from the instrument."""
        if self._visaDevice:
            self._visaDevice.disconnect()
            self._visaDevice = None

    def selectOutput(self, output):
        """@brief Select PSU output.
           @param output The output to select. An integer value."""
        output = int(output)
        if output not in [1, 2, 3]:
            raise Exception(
                f"{output} is not a valid output. This PSU has outputs 1,2 or 3.")
        self._visaDevice.cmd(f"INST OUT{output}")

    def setVolts(self, voltage):
        """@brief Set the currently selected output voltage.
           @param voltage The voltage in volts."""
        voltage = float(voltage)

        if voltage < HMP2030PSU.MIN_VOLTS:
            raise Exception(
                f"{voltage} is an invalid voltage (MIN={HMP2030PSU.MIN_VOLTS}).")

        if voltage > HMP2030PSU.MAX_VOLTS:
            raise Exception(
                f"{voltage} is an invalid voltage (MAX={HMP2030PSU.MAX_VOLTS}).")

        self._visaDevice.cmd(f"VOLT {voltage}")

    def setAmps(self, current):
        """@brief Set the selected output current limit.
           @param current The current limit in amps."""
        amps = float(current)

        if amps < HMP2030PSU.MIN_AMPS:
            raise Exception(
                f"{amps} is an invalid current (MIN={HMP2030PSU.MIN_AMPS}).")

        if amps > HMP2030PSU.MAX_AMPS:
            raise Exception(
                f"{amps} is an invalid current (MAX={HMP2030PSU.MAX_AMPS}).")

        self._visaDevice.cmd(f"CURR {amps}")

    def enableOutput(self, on):
        """@brief Enable a previously selected output.
           @param on If True turn output on when apply switchOn is called."""
        if on:
            self._visaDevice.cmd("OUTP:SEL 1")
        else:
            self._visaDevice.cmd("OUTP:SEL 0")

    def switchOn(self, on):
        """@brief Turn on/off all previously enabled outputs.
           @param on If True turn output/s on."""
        if on:
            self._visaDevice.cmd("OUTP:GEN 1")
        else:
            self._visaDevice.cmd("OUTP:GEN 0")

    def getVolts(self):
        """@brief Get the selected output voltage.
           @return The selected output voltage in volts."""
        return float(self._visaDevice.query("VOLTS?"))

    def getLimitAmps(self):
        """@brief Get the selected output current limit.
           @return The selected output current limit in amps."""
        return float(self._visaDevice.query("CURR?"))

    def getLoadAmps(self):
        """@brief Get the selected output load current.
           @return The selected output load current in amps."""
        return float(self._visaDevice.query("MEAS:CURR?"))


class TENMA722550PSU(PSUBase):
    """@brief Responsible for providing an interface to TENMA 72-2550 PSU's."""

    MIN_VOLTS = 0.0
    MAX_VOLTS = 60.0
    MIN_AMPS = 0.0
    MAX_AMPS = 3.0
    PSU_TYPE = 2
    PSU_NAME = "TENMA 72-2550 PSU"
    BPS = 9600
    TIMEOUT_SECONDS = 2

    def __init__(self, uio=None):
        """@brief Construct a power supply interface.
           @param uio A UIO instance or None. If a UIO instance is passed then debug messages
                  may be displayed when the _debug(msg) method is called."""
        super().__init__(TENMA722550PSU.PSU_TYPE, TENMA722550PSU.PSU_NAME, uio=uio)
        self._serial = None

    def connect(self, dev):
        """@brief Connect to the PSU.
           @param dev The serial port to use. This maybe the device name, the serial
                      port serial number or the USB location string.
                      See SerialPortFinder.GetDevice() for more info."""

        if self._serial:
            self.disconnect()

        serialDev = SerialPortFinder.GetDevice(dev)
        self._serial = serial.Serial()
        self._serial.port = serialDev
        self._serial.baudrate = TENMA722550PSU.BPS
        self._serial.bytesize = serial.EIGHTBITS
        self._serial.stopbits = serial.STOPBITS_ONE
        self._serial.parity = serial.PARITY_NONE
        self._serial.xonxoff = False
        self._serial.rtscts = False
        self._serial.dsrdtr = False
        self._serial.timeout = TENMA722550PSU.TIMEOUT_SECONDS
        self._serial.open()
        # Initially read the PSU voltage to check communication with the PSU.
        voltage = self.getVolts()
        self._debug("PSU Voltage = {:.3f} volts".format(voltage))

    def disconnect(self):
        """@brief Disconnect from the instrument."""
        if self._serial:
            self._serial.close()
            self._serial = None

    def selectOutput(self, output):
        """@brief Select the output on the PSU.
           @param output The output to select."""
        if output != 1:
            raise Exception(
                f"Cannot set output {output} on {TENMA722550PSU.PSU_NAME} as it only has one output.")

    def _sendCmd(self, cmdString):
        """@brief Send a command string to the instrument."""
        self._debug("CMD: {}".format(cmdString))
        self._serial.write(cmdString.encode())
        sleep(.5)

    def _getRXString(self):
        """@brief Get the response to a command.
           @return The string received."""
        cList = []
        # 5 characters should be present in the response.
        for _ in range(0, 5):
            char = self._serial.read(1)
            cList.append(char.decode("utf-8", errors='ignore'))
        rxString = "".join(cList)
        self._debug("RESPONSE: {}".format(rxString))
        return rxString

    def _writeCommand(self, wCommand, rCommand, wValue, retry=5):
        """@brief Write an attribute and read it back to check it has been set.
           @param wCommand The command to send.
           @param rCommand The command to read the PSU attribute.
           @param wValue The value to send.
           @param retry The number of retries before an error occurs."""
        tries = 0
        while True:
            wCmd = f"{wCommand}{wValue:2.2f}"
            self._sendCmd(wCmd)
            self._sendCmd(rCommand)
            rxStr = self._getRXString()
            if len(rxStr) > 0:
                try:
                    rValue = float(rxStr)
                    if wValue == rValue:
                        break
                except ValueError:
                    pass
            if tries >= retry:
                raise Exception(
                    f"{retry} failed attempt to read back the value set on the PSU.")

            sleep(0.4)
            tries += 1

    def _getCmd(self, rCommand, retry=5):
        """@brief Get a value (float) from the PSU.
           @param rCommand The command to read the PSU attribute.
           @param retry The number of retries before an error occurs."""
        tries = 0
        valueRead = None
        while True:
            self._sendCmd(rCommand)
            rxStr = self._getRXString()
            if len(rxStr) > 0:
                try:
                    valueRead = float(rxStr)
                    break
                except ValueError:
                    pass
            if tries >= retry:
                raise Exception(
                    "{} failed attempt to read back the value set on the PSU".format(retry))

            sleep(0.4)
            tries += 1

        return valueRead

    def setVolts(self, volts):
        """@brief Set the currently selected output voltage.
           @param voltage The voltage in volts."""
        self._writeCommand("VSET1:", "VSET1?", volts)

    def setAmps(self, amps):
        """@brief Set the selected output current limit.
           @param current The current limit in amps."""
        self._writeCommand("ISET1:", "ISET1?", amps)

    def enableOutput(self, on):
        """@brief Enable a previously selected output.
                  This method is redundant on this PSU as it only has one output."""
        pass

    def switchOn(self, on):
        """@brief Turn on/off all previously enabled outputs.
           @param on If True turn output/s on."""
        cmd = "OUT0"
        if on:
            cmd = "OUT1"
        self._sendCmd(cmd)
        self.getVolts()

    def getVolts(self):
        """@brief Get the selected output voltage.
           @return The selected output voltage in volts."""
        return self._getCmd("VOUT1?")

    def getLimitAmps(self):
        """@brief Get the selected output current limit.
           @return The selected output current limit in amps."""
        return self._getCmd("ISET1?")

    def getLoadAmps(self):
        """@brief Get the selected output load current.
           @return The selected output load current in amps."""
        return self._getCmd("IOUT1?")


class ETMXXXXPError(Exception):
    """@brief An exception produced by ETMXXXXP class instances."""
    pass


class ETMXXXXP(PSUBase):
    """Repsonsible for providing an interface to the ETommens eTM-xxxxP Series PSU.
       Several Mfg's use this supply, Hanmatek HM305P, Rockseed RS305P,
       Hanmatek HM310P, RockSeed RS310P, Rockseed RS605P.

       Ref https://sigrok.org/wiki/ETommens_eTM-xxxxP_Series#Protocol

       This class supports

       Setting

       - Output on/off state
       - Output Voltage
       - Current limit
       - Over voltage protection
       - Over current protection
       - Over power protection
       - Setting the buzzer on/off state

       Getting

       - The output on/off state
       - The target output voltage
       - The actual output voltage (drops to 0 if output is off)
       - The output current
       - The output power
       - The current limit value
       - The over voltage protection value
       - The over current protection value
       - The over power protection value

       """
    PSU_TYPE = 3
    PSU_NAME = "ETMXXXXP"

    MIN_VOLTAGE = 0
    MAX_VOLTAGE = 32.0
    # This is the max value that can be set on the PSU
    MAX_OVER_VOLTAGE = 33.0
    # 10A max, some models have a 5A max current.
    MAX_CURRENT = 10.0
    # This is the max value that can be set on the PSU
    MAX_OVER_CURRENT = 10.5
    # This is the max value that can be set on the PSU
    MAX_OVER_POWER = 310.0
    # RW REG
    OUTPUT_STATE_REG_ADDR = 0x0001
    # R REGS
    PROTECTION_STATE_REG_ADDR = 0x0002
    MODEL_ID_REG_ADDR = 0x0004
    OUTPUT_VOLTAGE_REG_ADDR = 0x0010
    OUTPUT_CURRENT_REG_ADDR = 0x0011
    OUTPUT_PWR_HI_REG_ADDR = 0x0012         # Top 16 bits of output power reg
    OUTPUT_PWR_LO_REG_ADDR = 0x0013         # Bottom 16 bits of output power reg
    # R/WR REGS
    VOLTAGE_TARGET_REG_ADDR = 0x0030
    CURRENT_LIMIT_REG_ADDR = 0x0031
    OVER_VOLTAGE_PROT_REG_ADDR = 0x0020
    OVER_CURRENT_PROT_REG_ADDR = 0x0021
    OVER_PWR_PROT_HI_REG_ADDR = 0x0022      # Top 16 bits of over power protection
    # Bottom 16 bits of over power protection
    OVER_PWR_PROT_LOW_REG_ADDR = 0x0023
    # 1 = enable (beep on key press), 0 = disable
    BUZZER_REG_ADDR = 0x8804

    def __init__(self, uio=None):
        """@brief Construct a power supply interface.
           @param uio A UIO instance or None. If a UIO instance is passed then debug messages
                  may be displayed when the _debug(msg) method is called."""
        super().__init__(ETMXXXXP.PSU_TYPE, ETMXXXXP.PSU_NAME, uio=uio)
        self._slave = 1  # The unit number on the modbus interface. As it's a serial interface
        # only one unit is physically connected.
        self._client = None  # Modbus client connection

        if uio and uio.isDebugEnabled():
            logging.basicConfig()
            log = logging.getLogger()
            log.setLevel(logging.DEBUG)

    def connect(self, dev, timeout=2):
        """@brief connect to the PSU over the serial port.
           @param timeout The command response timeout in seconds (default=2).
           @return True if connected."""
        serialDev = SerialPortFinder.GetDevice(dev)
        self._client = ModbusSerialClient(framer=FramerType.RTU,
                                          port=serialDev,
                                          baudrate=9600,
                                          stopbits=1,
                                          bytesize=8,
                                          parity='N',
                                          timeout=timeout)
        return self._client.connect()

    def selectOutput(self, output):
        """@brief Select the output on the PSU.
           @param output The output to select."""
        if output != 1:
            raise Exception(
                f"Cannot set output {output} on {ETMXXXXP.PSU_NAME} as it only has one output.")

    def enableOutput(self, on):
        """@brief Enable a previously selected output.
                  This method is redundant on this PSU as it only has one output."""
        pass

    def setVolts(self, volts):
        """@brief Set the currently selected output voltage.
           @param voltage The voltage in volts."""
        self.setVoltage(volts)

    def setVoltage(self, voltage):
        """@brief Set the output voltage.
           @param voltage The voltage in volts (a float value)."""
        if voltage < ETMXXXXP.MIN_VOLTAGE or voltage > ETMXXXXP.MAX_VOLTAGE:
            raise ETMXXXXPError("{} is an invalid voltage (valid range {}V - {}V)".format(
                voltage, ETMXXXXP.MIN_VOLTAGE, ETMXXXXP.MAX_VOLTAGE))
        self._client.write_register(
            ETMXXXXP.VOLTAGE_TARGET_REG_ADDR, int(voltage*100.0), slave=self._slave)

    def setAmps(self, amps):
        """@brief Set the selected output current limit.
           @param current The current limit in amps."""
        self.setCurrentLimit(amps)

    def setCurrentLimit(self, amps):
        """@brief Set the current limit value.
           @param amps The current in amps (a float value)."""
        if amps < 0.0 or amps > ETMXXXXP.MAX_CURRENT:
            raise ETMXXXXPError(
                "{} is an invalid current value (valid range 0A - {}A)".format(amps, ETMXXXXP.MAX_CURRENT))
        self._client.write_register(
            ETMXXXXP.CURRENT_LIMIT_REG_ADDR, int(amps*1000.0), slave=self._slave)

    def switchOn(self, on):
        """@brief Turn on/off all previously enabled outputs.
           @param on If True turn output/s on."""
        self.setOutput(on)

    def setOutput(self, on):
        """@brief Set The PSU output on/off.
           @param on If True the PSU output is on."""
        self._client.write_register(
            ETMXXXXP.OUTPUT_STATE_REG_ADDR, on, slave=self._slave)

    def getVolts(self):
        """@brief Get the selected output voltage.
           @return The selected output voltage in volts."""
        volts, _, _ = self.getOutputStats()
        return volts

    def getLoadAmps(self):
        """@brief Get the selected output load current.
           @return The selected output load current in amps."""
        _, amps, _ = self.getOutputStats()
        return amps

    def getOutputStats(self):
        """@brief Read the output voltage, current and power of the PSU.
           @return A tuple containing
                   0: voltage
                   1: amps
                   2: watts"""
        rr = self._client.read_holding_registers(
            ETMXXXXP.OUTPUT_VOLTAGE_REG_ADDR, count=4, slave=self._slave)
        voltage = float(rr.registers[0])
        if voltage > 0:
            voltage = voltage / 100.0
        amps = float(rr.registers[1])
        if amps > 0:
            amps = amps / 1000.0
        wattsH = rr.registers[2]
        wattsL = rr.registers[3]
        watts = wattsH << 16 | wattsL
        if watts > 0:
            watts = watts / 1000.0
        return (voltage, amps, watts)

    def disconnect(self):
        """@brief Disconnect from the PSU if connected."""
        if self._client:
            self._client.close()
            self._client = None

    # READ REGS
    def getOutput(self):
        """@brief Get the state of the PSU output.
           @return 1 if the output is on, else 0."""
        rr = self._client.read_holding_registers(
            ETMXXXXP.OUTPUT_STATE_REG_ADDR, count=1, slave=self._slave)
        return rr.registers[0]

    def getProtectionState(self):
        """@brief Get the state of the protections switch.
           @return 1 if protection mode is enabled, else 0."""
        rr = self._client.read_holding_registers(
            ETMXXXXP.PROTECTION_STATE_REG_ADDR, count=1, slave=self._slave)
        return rr.registers[0]

    def getModel(self):
        """@brief Get the model ID
           @return The model ID value"""
        rr = self._client.read_holding_registers(
            ETMXXXXP.MODEL_ID_REG_ADDR, count=1, slave=self._slave)
        return rr.registers[0]

    def getTargetVolts(self):
        """@brief Read the target output voltage
           @return The output voltage set in volts."""
        rr = self._client.read_holding_registers(
            ETMXXXXP.VOLTAGE_TARGET_REG_ADDR, count=1, slave=self._slave)
        voltage = float(rr.registers[0])
        if voltage > 0:
            voltage = voltage / 100.0
        return voltage

    def getCurrentLimit(self):
        """@brief Read the current limit in amps
           @return The current limit."""
        rr = self._client.read_holding_registers(
            ETMXXXXP.CURRENT_LIMIT_REG_ADDR, count=1, slave=self._slave)
        amps = float(rr.registers[0])
        if amps > 0:
            amps = amps / 1000.0
        return amps

    def getProtectionValues(self):
        """@brief Read the over voltage, current and power protection values
           @return A tuple containing
                   0: over voltage protection value
                   1: over current protection value
                   2: over power protection value"""
        rr = self._client.read_holding_registers(
            ETMXXXXP.OVER_VOLTAGE_PROT_REG_ADDR, count=4, slave=self._slave)
        voltage = float(rr.registers[0])
        if voltage > 0:
            voltage = voltage / 100.0
        amps = float(rr.registers[1])
        if amps > 0:
            amps = amps / 1000.0
        wattsH = rr.registers[2]
        wattsL = rr.registers[3]
        watts = float(wattsH << 16 | wattsL)
        if watts > 0:
            watts = watts / 1000.0
        return (voltage, amps, watts)

    def getBuzzer(self):
        """@brief Get the state of the buzzer
           @return 1 if enabled, 0 if disabled."""
        rr = self._client.read_holding_registers(
            ETMXXXXP.BUZZER_REG_ADDR, count=1, slave=self._slave)
        return rr.registers[0]

    def setOverCurrentP(self, amps):
        """@brief Set the over current protection value.
           @param amps The current in amps (a float value)."""
        print(f"PJA: amps={amps}")
        if amps < 0.0 or amps > ETMXXXXP.MAX_OVER_CURRENT:
            raise ETMXXXXPError(
                "{} is an invalid voltage (valid range 0V - {}V)".format(amps, ETMXXXXP.MAX_OVER_CURRENT))
        self._client.write_register(
            ETMXXXXP.OVER_CURRENT_PROT_REG_ADDR, int(amps*1000.0), slave=self._slave)

    def setOverVoltageP(self, voltage):
        """@brief Set the over voltage protection value.
           @param voltage The voltage in volts (a float value)."""
        if voltage < ETMXXXXP.MIN_VOLTAGE or voltage > ETMXXXXP.MAX_OVER_VOLTAGE:
            raise ETMXXXXPError("{} is an invalid voltage (valid range {}V - {}V)".format(
                voltage, ETMXXXXP.MIN_VOLTAGE, ETMXXXXP.MAX_VMAX_OVER_VOLTAGEOLTAGE))
        self._client.write_register(
            ETMXXXXP.OVER_VOLTAGE_PROT_REG_ADDR, int(voltage*100.0), slave=self._slave)

    def setOverPowerP(self, watts):
        """@brief Set the over power protection value.
           @param watts The power in watts (a float value)."""
        if watts < 0.0 or watts > ETMXXXXP.MAX_OVER_POWER:
            raise ETMXXXXPError(
                "{} is an invalid power (valid range 0W - {}W)".format(watts, ETMXXXXP.MAX_OVER_POWER))
        wattValue = int((watts*1000))
        wattsL = wattValue & 0x0000ffff
        wattsH = (wattValue & 0xffff0000) >> 16
        self._client.write_register(
            ETMXXXXP.OVER_PWR_PROT_HI_REG_ADDR, wattsH, slave=self._slave)
        self._client.write_register(
            ETMXXXXP.OVER_PWR_PROT_LOW_REG_ADDR, wattsL, slave=self._slave)

    def setBuzzer(self, on):
        """@brief Set the buzzer on/off.
           @param on If True the buzzer is set on, 0 = off."""
        self._client.write_register(
            ETMXXXXP.BUZZER_REG_ADDR, on, slave=self._slave)


class PSUFactory(object):
    """@brief This class is responsible for providing a PSU instance of the required type."""

    SUPPORTED_PSU_LIST = [
        DummyPSU,
        HMP2030PSU,
        TENMA722550PSU,
        ETMXXXXP
    ]

    MAX_PSU_TYPE = len(SUPPORTED_PSU_LIST)-1

    @staticmethod
    def GetInstance(psuType, uio=None):
        """@brief Get an instance of the required PSU class.
           @param psuType The PSU type as an integer."""
        if psuType == DummyPSU.PSU_TYPE:
            psu = DummyPSU(uio=uio)

        elif psuType == HMP2030PSU.PSU_TYPE:
            psu = HMP2030PSU(uio=uio)

        elif psuType == TENMA722550PSU.PSU_TYPE:
            psu = TENMA722550PSU(uio=uio)

        elif psuType == ETMXXXXP.PSU_TYPE:
            psu = ETMXXXXP(uio=uio)

        else:
            raise Exception("{} is an unknown PSU type.")

        return psu
