# seriell einlesen ohne thread
# UNGETESTET: das wegwerfen von empfangenen zeilen, die mit ":" beginnen!

import datetime  # time and
import __main__ as main  # main necessary for error logging in file
import logging
import serial
from time import *

logger = logging.Logger()
logger.setLevel('debug')
# Configuration
BAUDRATE = 9600
MAX_WAIT_FOR_RX_TIMEOUT = 2000
# this is the character(s) at the end of a complete input line, sent by AVR via CAN
EOL_CHAR_RX = chr(10)
# this is the character(s) at the end of an command sent by raspberry pi
EOL_CHAR_TX = chr(13) + chr(10)
MAX_BUFFER_LENGTH = 80

# initialise serial connection
ser = serial.Serial("/dev/ttyAMA0", BAUDRATE, xonxoff=False)


def calculate_checksum(payload):
    # calculate simple checksum (sum over all bytes in payload)
    checksum = sum([ord(c) for c in payload])
    return checksum


def send_command(sendstring):
    """Send command in sendstring on serial output

    Wait maximal max_wait_for_rx_timeout milliseconds for answer, typ. 2 seconds
    return string with answer from remote device
    in case of timeout error will be logged if error log active
    """
    timeouterror = True
    input_line = ""
    returnstring = ""
    ser.flushInput()
    checksum = calculate_checksum(sendstring)
    sendstring = sendstring + "#" + str(checksum) + EOL_CHAR_TX
    ser.write(sendstring)

    # wait max max_wait_for_rx_timeout for new line(s) from serial input. if received line begins with ":", then discard it.
    maxwait = MAX_WAIT_FOR_RX_TIMEOUT
    while (maxwait > 0):
        # received character waiting in uart buffer
        if ser.inWaiting() > 0:
            # reset flag
            saveline = False
            # read one byte from serial input line
            s = ser.read()
            if s == EOL_CHAR_RX:
                saveline = True
            # received character is no control code
            elif ord(s) > 31:
                # append received character to buffer
                input_line = input_line + s
                if len(input_line) >= MAX_BUFFER_LENGTH:
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
            checksum_calc = calculate_checksum(payload)
            # if checksum_calc == int(checksum_received):
            if True:
                returnstring = payload
            else:
                logger.error("wrong checksum from CAN client. received string was: {0}".format(returnstring))
                returnstring = ""

    return returnstring


while True:
    sendstring = ":altair setport 5 1"
    print "TX: -> " + sendstring
    returnstring = send_command(sendstring)
    print "TX: <- " + returnstring

    sendstring = ":altair setport 5 0"
    print "TX: -> " + sendstring
    returnstring = send_command(sendstring)
    print "TX: <- " + returnstring

    sendstring = ":altair getana 0"
    print "TX: -> " + sendstring
    returnstring = send_command(sendstring)
    print "TX: <- " + returnstring

ser.close()
