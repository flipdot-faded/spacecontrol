#
# seriell einlesen ohne thread
# UNGETESTET: das wegwerfen von empfangenen zeilen, die mit ":" beginnen!

import datetime  # time and
import __main__ as main  # main necessary for error logging in file
import serial
from time import *
# import wlcd															# little module for tft control characters

# Configuration
error_log = True
baudrate = 9600
max_wait_for_rx_timeout = 2000
# this is the character(s) at the end of a complete input line, sent by AVR via CAN
eol_char_rx = chr(10)
# this is the character(s) at the end of an command sent by raspberry pi
eol_char_tx = chr(13) + chr(10)
max_buffer_length = 80

# initialise serial connection
ser = serial.Serial("/dev/ttyAMA0", baudrate, xonxoff=False)


# dump errorstring in error file, named "error_log_my-filename.py_.txt"
def log_error(errorstring):
    my_filename = (main.__file__)
    # add "error_log"
    errorfile_name = "error_log_" + my_filename + "_.txt"
    errorfile = open(errorfile_name, "a")
    current_time = datetime.datetime.now()
    # build date and time string as CSV for excel import later on
    rightnow = current_time.strftime('%Y-%m-%d; %H:%M:%S;')
    # if complete send commands are pasted into error string, cr/lf char is removed
    errorstring = errorstring.replace(eol_char_tx, "")
    # if complete received lines are pasted into error string, cr/lf char is removed
    errorstring = errorstring.replace(eol_char_rx, "")
    errorfile.write(rightnow + ' "' + errorstring + '"' + '\n')
    errorfile.close()


def calculate_checksum(payload):
    # calculate simple checksum (sum over all bytes in payload)
    checksum = sum([ord(c) for c in payload])
    return checksum


def sercom(sendstring):
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
    sendstring = sendstring + "#" + str(checksum) + eol_char_tx
    ser.write(sendstring)

    # wait max max_wait_for_rx_timeout for new line(s) from serial input. if received line begins with ":", then discard it.
    maxwait = max_wait_for_rx_timeout
    while (maxwait > 0):
        # received character waiting in uart buffer
        if ser.inWaiting() > 0:
            # reset flag
            saveline = False
            # read one byte from serial input line
            s = ser.read()
            if s == eol_char_rx:
                saveline = True
            # received character is no control code
            elif ord(s) > 31:
                # append received character to buffer
                input_line = input_line + s
                if len(input_line) >= max_buffer_length:
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
        if error_log == True:
            log_error("no answer from CAN client. transmit string was: " + sendstring)
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
                if error_log == True:
                    log_error("wrong checksum from CAN client. received string was: " + returnstring)
                    returnstring = ""

    return returnstring


while True:
    sendstring = ":altair setport 5 1"
    print "TX: -> " + sendstring
    returnstring = sercom(sendstring)
    print "TX: <- " + returnstring

    sendstring = ":altair setport 5 0"
    print "TX: -> " + sendstring
    returnstring = sercom(sendstring)
    print "TX: <- " + returnstring

    sendstring = ":altair getana 0"
    print "TX: -> " + sendstring
    returnstring = sercom(sendstring)
    print "TX: <- " + returnstring

ser.close()
