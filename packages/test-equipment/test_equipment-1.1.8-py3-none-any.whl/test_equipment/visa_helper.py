#!/usr/bin/env python3

import pyvisa

# Example code is at the bottom of the file.


class VisaDev(object):
    """@brief Responsible for providing an interface to test equipment that supports the VISA interface."""

    @staticmethod
    def Show(uio):
        """@brief Show the list of locally available VISA devices to the user.
           @param uio A UIO instance.
           @return The number of VISA devices found."""
        visaDeviceCount = 0
        vDev = VisaDev()
        uio.info("Searching for VISA devices...")
        devList = vDev.getList()
        table = [("Device Name", "VISA ID String")]
        for dev in devList:
            try:
                vDev = VisaDev(uio=uio)
                vDev.connect(dev)
                response = vDev.query("*IDN?")
                response = response.strip('\r\n')
                table.append((str(dev), str(response)))
                visaDeviceCount += 1
            except Exception:
                pass
        if len(table) > 1:
            uio.info("VISA devices")
            uio.showTable(table)

        return visaDeviceCount

    def __init__(self, uio=None):
        """@brief Create a VisaDev instance.
           @param uio A UIO instance."""
        self._uio = uio
        self._resMgr = None
        self._theInstrument = None

    def _debug(self, msg):
        """@brief Show a debug message.
           @msg The message to be displayed."""
        if self._uio:
            self._uio.debug(msg)

    def connect(self, devS):
        """@brief Connect to a VISA device.
           @param devS A VISA resource string.

                            E.G.
                            TCPIP::192.168.0.20::INSTR
                            TCPIP::192.168.2.30::hislip1
                            GPIB::10::INSTR
                            USB::0x0403::0xed72::019779656::INSTR
                            RSNRP::0x0095::106102::INSTR
                            ASRL/dev/ttyUSB0::INSTR"""
        self._resMgr = pyvisa.ResourceManager()
        self._theInstrument = self._resMgr.open_resource(devS)
        self._debug(f"Connected to {devS}")

    def disconnect(self):
        """@brief Disconnect from a VISA device."""
        if self._resMgr:
            self._resMgr.close()
            self._resMgr = None

    def getList(self):
        """@return A list of all local available VISA instruments."""
        if not self._resMgr:
            self._resMgr = pyvisa.ResourceManager()

        devList = self._resMgr.list_resources()
        return devList

    def query(self, qCmd):
        """@brief Run a query command.
           @param qCmd The query command (SCPI).
           @return The response to the above."""
        self._debug(f"Running Query CMD: {qCmd}")
        response = self._theInstrument.query(qCmd)
        self._debug(f"Response: {response}")
        return response

    def cmd(self, cmd):
        """@brief Run an SCPI command (write only).
           @param cmd The command (SCPI).
           @return None"""
        self._debug("Running CMD: {}".format(cmd))
        self._theInstrument.write(cmd)


# Example code

def test():
    from p3lib.uio import UIO
    uio = UIO(debug=False)
    uio.info("Show all local VISA devices.")
    VisaDev.Show(uio)


if __name__ == '__main__':
    test()
