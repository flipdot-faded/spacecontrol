#
# seriell einlesen ohne thread
# UNGETESTET: das wegwerfen von empfangenen zeilen, die mit ":" beginnen!

# color_code = {"black":30, "red":31, "green":32, "yellow":33, "blue":34, "magenta":35, "cyan":36, "white":37}
# write ("\033["+str(color_code[fg])+";"+str(color_code[bg]+10)+"m") # color code for background is foreground code + 10

import datetime  # time and
import __main__ as main  # main necessary for error logging in file
import serial
from time import *
# import wlcd															# little module for tft control characters

error_log = True  # Write errors in logfile "error_log_my-filename.py_.txt" if True
baudrate = 9600  # communication baudrate to CAN client
max_wait_for_rx_timeout = 2000  # wait max. n milliseconds for return string of can client
eol_char_rx = chr(10)  # this is the character(s) at the end of a complete input line, sent by AVR via CAN
# only ONE character!
eol_char_tx = chr(13) + chr(10)  # this is the character(s) at the end of an command sent by raspberry pi
max_buffer_length = 80  # max number of characters received for processing buffer ..
# without receiving eol_char_rx


# sleep (30)														# if called by cronjob

# initialise serial connection 
ser = serial.Serial("/dev/ttyAMA0", baudrate, xonxoff=False)


# dump errorstring in error file, named "error_log_my-filename.py_.txt"
def log_error(errorstring):
    my_filename = (main.__file__)  # get file name of this script actual processed
    errorfile_name = "error_log_" + my_filename + "_.txt"  # add "error_log"
    errorfile = open(errorfile_name, "a")  # open for writing in append mode
    i = datetime.datetime.now()  # get actual time
    rightnow = i.strftime('%Y-%m-%d; %H:%M:%S;')  # build date and time string as CSV for excel import later on
    errorstring = errorstring.replace(eol_char_tx,
                                      "")  # if complete send commands are pasted into error string, cr/lf char is removed
    errorstring = errorstring.replace(eol_char_rx,
                                      "")  # if complete received lines are pasted into error string, cr/lf char is removed
    errorfile.write(rightnow + ' "' + errorstring + '"' + '\n')  # append this to file
    errorfile.close()  # close file to clean up nicely


def calculate_checksum(payload):
    checksum = sum([ord(c) for c in payload])  # calculate simple checksum (sum over all bytes in payload)
    # maybe more fancy later on
    return checksum


def sercom(sendstring):
    "send command in sendstring on serial output"
    "wait maximal max_wait_for_rx_timeout milliseconds for answer, typ. 2 seconds"
    "return string with answer from remote device"
    "in case of timeout error will be logged if error log active"
    timeouterror = True
    input_line = ""
    returnstring = ""
    ser.flushInput()
    checksum = calculate_checksum(sendstring)  # calculate checksum
    sendstring = sendstring + "#" + str(checksum) + eol_char_tx  # and append checksum after character "#" to payload
    ser.write(sendstring)  # write data telegram to CAN client out there

    # wait max max_wait_for_rx_timeout for new line(s) from serial input. if received line begins with ":", then discard it.
    maxwait = max_wait_for_rx_timeout
    while (maxwait > 0):
        if ser.inWaiting() > 0:  # received character waiting in uart buffer
            saveline = False  # reset flag
            s = ser.read()  # read one byte from serial input line
            if s == eol_char_rx:  # end of line character received?
                saveline = True  # received line so far will be processed later
            elif ord(s) > 31:  # if received character is no control code, then ..
                input_line = input_line + s  # append received character to buffer
                if len(input_line) >= max_buffer_length:  # maximum buffer length reached?
                    saveline = True
            if saveline == True:
                pos = input_line.find(
                    ":")  # find first occurrence of character ":". if it is at beginning of received line, ..
                if pos == 0:
                    input_line = ""  # then discard received line, because its an echo of raspis own CAN bus command.
                else:  # this line must be from CAN client out there
                    returnstring = input_line  # save received line in output buffer: new_input_line
                    input_line = ""  # clear temp input buffer
                    returnstring = returnstring.strip()  # remove spaces at end and beginning
                    maxwait = 0
                    timeouterror = False
        else:  # no char waiting, sleep for 1 ms
            sleep(0.001)
            maxwait = maxwait - 1

    if (timeouterror == True):
        if error_log == True:
            log_error("no answer from CAN client. transmit string was: " + sendstring)
            returnstring = "TIMEOUT"
    else:
        pos = returnstring.find("#")  # look for separator "#" between payload and checksum (not present if string ..
        if pos != -1:  # empty
            payload, checksum_received = returnstring.split(
                "#")  # part before "#" is payload, part after "#" is checksum
            checksum_calc = calculate_checksum(payload)  # calculate checksum
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

    # sendstring = ":altair setport 4 0"
    #	print "TX: -> " + sendstring
    #	returnstring = sercom(sendstring)
    #	print "TX: <- " + returnstring

    #	sendstring = ":altair setport 4 1"
    #	print "TX: -> " + sendstring
    #	returnstring = sercom(sendstring)
    #	print "TX: <- " + returnstring

    #	sendstring = ":altair setport 3 0"
    #	print "TX: -> " + sendstring
    #	returnstring = sercom(sendstring)
    #	print "TX: <- " + returnstring

    #	sendstring = ":altair setport 3 1"
    #	print "TX: -> " + sendstring
    #	returnstring = sercom(sendstring)
    #	print "TX: <- " + returnstring

    # sendstring = ":altair petana 0"
    # print "TX: -> " + sendstring
    # returnstring = sercom(sendstring)
    # print "TX: <- " + returnstring



    sendstring = ":altair getana 0"
    print "TX: -> " + sendstring
    returnstring = sercom(sendstring)
    print "TX: <- " + returnstring

ser.close()

