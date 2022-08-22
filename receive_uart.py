#!/usr/bin/python
# -*- coding:utf-8 -*-
import serial
import struct
import time

uart = serial.Serial("/dev/ttyS0",115200)

try:
    while True:
        byte_read = uart.read(1)
        if byte_read is None:
            continue
        if byte_read == b"<":
            message = []
            data_array = None
            data_array = []
            message_started = True
            continue
        if message_started:
            if byte_read == b">":
                message_parts = "".join(message)
                message_started = False
                myList = list(message_parts.split("\n"))
                for x in myList:
                    data_array.append(list(x.split(",")))
                print('received %s rows of data' %  len(data_array))
            else:
                # Accumulate message byte.
                message.append(chr(byte_read[0]))
#        if byte_read is not None:
#            print(byte_read)
except KeyboardInterrupt:
    if uart != None:
        uart.close()
