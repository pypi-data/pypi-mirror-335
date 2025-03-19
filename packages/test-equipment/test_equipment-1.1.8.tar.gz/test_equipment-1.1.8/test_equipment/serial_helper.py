#!/usr/bin/env python3

# Example code is at the bottom of the file.

from serial.tools.list_ports import comports


class SerialPortFinder(object):
    """@brief Responsible for providing methods useful when checking what serial ports are available on a machine."""

    @staticmethod
    def GetList():
        """@brief Find the serial numbers of each port.
           @return A list containing the serial ports."""
        pl = []
        cpl = comports()
        for p in cpl:
            if p.vid is not None:
                pl.append(p)
        return pl

    @staticmethod
    def ShowPorts(uio):
        """@brief Display details of the available serial ports."""
        pl = SerialPortFinder.GetList()

        if len(pl) > 0:
            uio.info("Available Serial Ports")
            table = [("Device Name", "Port Serial Number",
                      "USB Port Location String")]
            for p in pl:
                table.append(
                    (str(p.device), str(p.serial_number), str(p.location)))
            uio.showTable(table)

        else:
            uio.info("No serial ports found on this machine.")

    @staticmethod
    def GetDevice(idStr):
        """@brief Get the serial device string matching of the idStr on the serial port number or USB location string.
           @param idStr A string used to identify the a serial port. This may be one of the following
                        - The device string. On Linux systems this could be be /dev/ttyUSB0.
                        - The serial port serial number. The USB serial device may have a serial number. If
                          a match is found on the serial number then this port will be selected.
                        - The USB location string. The location string is a hierachical string that defines
                          the port. E.G 1-2.3.3
                        - None If this is the case then the first serial port found is returned.
           @return The device name of the serial port or None if no matching serial port is found."""
        serDev = None
        pl = SerialPortFinder.GetList()
        if idStr is None:
            # Get the first available port
            if len(pl) > 0:
                serDev = pl[0].device

        else:
            # If an idStr was passed
            for p in pl:
                if p.device == idStr:
                    # If the device string was passed in it is simply returned.
                    serDev = idStr
                    break

                # If a match was found on the serial number of the port
                elif p.serial_number == idStr:
                    # Return the device name of the matching port
                    serDev = p.device
                    break

                # If a match was found on the USB location string
                elif p.location == idStr:
                    # Return the device name of the matching port
                    serDev = p.device
                    break

        return serDev


def test():
    from p3lib.uio import UIO
    uio = UIO()
    uio.info("Show all available serial ports.")
    SerialPortFinder.ShowPorts(uio)
    uio.info("")
    uio.info("Checking for serial port match")
    idStrList = ('1-2.3.3', '019779656', '/dev/ttyUSB0', None)
    for idStr in idStrList:
        dev = SerialPortFinder.GetDevice(idStr)
        uio.info(f"{idStr} matches {dev}")


if __name__ == '__main__':
    test()
