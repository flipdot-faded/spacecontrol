# -*- coding: utf-8 -*-

import serial
from time import sleep
import logging
logging.basicConfig()

from errors import CANException

logger = logging.getLogger(__name__)


class CanClient(object):
    def __init__(self, name, bus):
        self.name = name
        self.bus = bus

    def set_port(self, port, state):
        return self.bus.send_command(self.name, 'setport', port, state)

    def set_rgb(self, r, g, b):
        return self.bus.send_command(self.name, "setrgb", r, g, b)

    def set_servo(self, servo_no, servo_angle):
        return self.bus.send_command(self.name, "setservo", servo_no, servo_angle)

    def get_analog(self, port):
        return self.bus.send_command(self.name, 'getana', port)

    def get_port(self, port):
        return self.bus.send_command(self.name, "getport", port)

    def get_temp(self):
        return self.bus.send_command(self.name, "gettemp")

    def get_act_temp(self):
        return "{:10.2f}".format((int(self.bus.send_command(self.name, "getActTemp"))/100.0))

    def get_target_temp(self):
        ret = self.bus.send_command(self.name, "getTargetTemp")
	try:
            ret = "{}".format(int(ret)/100)
        except:
            return ret
        return ret
        #return "%d" % (int(self.bus.send_command(self.name, "getTargetTemp"))/100)

    def get_heater_valve(self):
        return "%d" % (int(self.bus.send_command(self.name, "getActValve")))

    def set_target_temp(self, temp):
        return self.bus.send_command(self.name, "setTargetTemp", temp)

    def send_cmd(self, cmd, *params):
        return self.bus.send_command(self.name, cmd, params)



class CanBus(object):
    def __init__(self,
                 baudrate=9600,
                 rx_timeout=2000,
                 eol_char_rx=chr(10),
                 eol_char_tx=chr(13) + chr(10),
                 buffer_length=80,
                 device="/dev/ttyAMA0"):
        self.baudrate = baudrate
        self.rx_timeout = rx_timeout
        self.eol_char_rx = eol_char_rx
        self.eol_char_tx = eol_char_tx
        self.buffer_length = buffer_length
        self.device = device

        self.serial = serial.Serial(self.device, self.baudrate, xonxoff=False, timeout=1)

    def get_can_client(self, client_name):
        return CanClient(client_name, self)

    def send_command(self, client, command, *args):
        args = (str(x) for x in args)
        command = ":{0} {1} {2}".format(client, command, ' '.join(args))
        return self._send_command(command)

    # legacy code
    def _calculate_checksum(self, payload):
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
        checksum = self._calculate_checksum(sendstring)
        sendstring = sendstring + "#" + str(checksum) + self.eol_char_tx
        self.serial.flushInput()
        self.serial.write(sendstring)
        print sendstring
        # wait max max_wait_for_rx_timeout for new line(s) from serial input. if received line begins with ":", then discard it.
        maxwait = self.rx_timeout


        while (maxwait > 0):
            # received character waiting in uart buffer
            waiting = self.serial.inWaiting()
            if  waiting > 0:
                #print "waiting: "+str(waiting)
                # reset flag
                saveline = False
                # read one byte from serial input line
                s = self.serial.read()
                #print "s was: "+s
                if len(s) == 0:
                    continue
                if s == self.eol_char_rx or s == '\n' or s == '\r':
                    #print "----w"
                    if len(input_line) > 0:
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
            raise CANException("CAN client response timeout")
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
                    raise CANException("CAN client send invalid checksum")
            else:
                logger.error("no checksum found")
                raise CANException("no checksum found")
        print returnstring
        return returnstring

