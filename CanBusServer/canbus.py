# -*- coding: utf-8 -*-

import serial
from time import sleep
import logging

logger = logging.getLogger(__name__)


class CanClient(object):
    def __init__(self, name, bus):
        self.name = name
        self.bus = bus

    def set_port(self, port, state):
        self.bus.send_command(self.name, )


class CanBus(object):
    def __init__(self,
                 baudrate=9600,
                 rx_timeout=2000,
                 eol_char_rx=chr(10),
                 eol_char_tx=chr(13) + chr(10),
                 buffer_length=80):
        self.baudrate = baudrate
        self.rx_timeout = rx_timeout
        self.eol_char_rx = eol_char_rx
        self.eol_char_tx = eol_char_tx
        self.buffer_length = buffer_length

        self.serial = serial.Serial("/dev/ttyAMA0", self.baudrate, xonxoff=False)

    def get_can_client(self, client_name):
        return CanClient(client_name, self)

    def send_command(self, client, command, *args):
        command = ":{0} {1} {2}".format(client, command, ' '.join(args))
        return self._send_command(command)

    # legacy code
    def _calculate_checksum(payload):
        # calculate simple checksum (sum over all bytes in payload)
        checksum = sum([ord(c) for c in payload])
        return checksum

    def _send_command(self, sendstring):
        """Send command in sendstring on serial output

        Wait maximal max_wait_for_rx_timeout milliseconds for answer, typ. 2 seconds
        return string with answer from remote device
        in case of timeout error will be logged if error log active
        """
        timeouterror = True
        input_line = ""
        returnstring = ""
        self.serial.flushInput()
        checksum = self._calculate_checksum(sendstring)
        sendstring = sendstring + "#" + str(checksum) + self.eol_char_tx
        self.serial.write(sendstring)

        # wait max max_wait_for_rx_timeout for new line(s) from serial input. if received line begins with ":", then discard it.
        maxwait = self.rx_timeout
        while (maxwait > 0):
            # received character waiting in uart buffer
            if self.serial.inWaiting() > 0:
                # reset flag
                saveline = False
                # read one byte from serial input line
                s = self.serial.read()
                if s == self.eol_char_rx:
                    saveline = True
                # received character is no control code
                elif ord(s) > 31:
                    # append received character to buffer
                    input_line = input_line + s
                    if len(input_line) >= self.buffer_length:
                        saveline = True
                if saveline == True:
                    pos = input_line.find(":")
                    if pos == 0:
                        # if the character ":" is at beginning of received line,
                        # discard received line, because its an echo of raspis own CAN bus command.
                        input_line = ""
                    else:
                        returnstring = input_line
                        input_line = ""
                        returnstring = returnstring.strip()
                        maxwait = 0
                        timeouterror = False
            else:
                # no char waiting, sleep for 1 ms
                sleep(0.001)
                maxwait = maxwait - 1

        if (timeouterror == True):
            logger.error("no answer from CAN client. transmit string was: {0}".format(sendstring))
            returnstring = "TIMEOUT"
        else:
            # look for separator "#" between payload and checksum (not present if string empty)
            pos = returnstring.find("#")
            if pos != -1:
                payload, checksum_received = returnstring.split("#")
                checksum_calc = self._calculate_checksum(payload)
                # if checksum_calc == int(checksum_received):
                if True:
                    returnstring = payload
                else:
                    logger.error("wrong checksum from CAN client. received string was: {0}".format(returnstring))
                    returnstring = ""

        return returnstring