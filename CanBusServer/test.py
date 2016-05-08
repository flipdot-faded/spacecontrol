#!/bin/python 
import serial
from time import sleep 
s = serial.Serial("/dev/ttyAMA0", 9600, timeout=1)

while True:
	s.write(":theemin getActTemp #1874\n")
	print s.readline()
	print s.readline()
	print s.readline()
