#!/usr/bin/env python
# Name:     SerialUart.py
# Purpose:  . 
# Dependency :
# pip install pyserial

import sys
import os
import time
import threading
import serial
from subprocess import Popen
from queue import Queue, Empty
import random

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class SerialThread (threading.Thread):
    def __init__(self, i_comPort, i_rxMsgQueue):
        threading.Thread.__init__(self)
        self.running = False
        self.comPort = i_comPort
        self.comBaud = 115200
        self.stopRequest = False
        self.ser = None
        self.rxMsgQueue = i_rxMsgQueue

    def run(self):
        self.running = True
        self.stopRequest = False
        


        while ( self.stopRequest == False) :
            line = ''
            if (self.ser == None):
                try:
                    #open UART communication link
                    self.ser = serial.Serial(self.comPort, self.comBaud, timeout=2.0,
                                        parity=serial.PARITY_NONE, rtscts=0)
                    self.ser.reset_input_buffer()
                except serial.SerialException as e:
                    print("Open serial Exception:", str(e))
                    self.stop()
                    continue
            try:
                rawLine = self.ser.readline()
                line = rawLine.decode('utf-8')
            except serial.SerialException as e:
                print("Read serial Exception:", str(e))
                #Close serial
                self.ser.close()
                self.ser = None
                time.sleep(0.5)
                continue
            except Exception as e:
                print("Exception decoding UART data:", str(e))
                print(rawLine, end='', flush=True)

            if ( line != "") :
                self.rxMsgQueue.put(line)

        #close UART link
        self.ser.close()
        self.ser = None
        self.running = False

    def stop(self):
        self.stopRequest = True

    def write(self, i_msg):
        if (self.ser != None):
            self.ser.write(i_msg)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class InputThread (threading.Thread):
    def __init__(self, i_inputMsgQueue):
        threading.Thread.__init__(self)
        self.running = False
        self.stopRequest = False
        self.inputMsgQueue = i_inputMsgQueue

    def run(self):
        self.running = True
        self.stopRequest = False

        while ( self.stopRequest == False) :
            try:
                inputKey = self.getChar()
                self.inputMsgQueue.put(inputKey.decode('utf-8'))
            except Exception as e:
                print("Exception:", str(e))

        self.running = False

    def stop(self):
        self.stopRequest = True

    def getChar(self):
        try:
            # for Windows-based systems
            import msvcrt # If successful, we are on Windows
            return msvcrt.getch()

        except ImportError:
            # for POSIX-based systems (with termios & tty support)
            import tty, sys, termios  # raises ImportError if unsupported

            fd = sys.stdin.fileno()
            oldSettings = termios.tcgetattr(fd)

            try:
                tty.setcbreak(fd)
                answer = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)

            return answer

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def crc16(data : bytearray , length):
    crc = 0xFFFF
    for i in range(0, length):
        crc ^= data[i] << 8
        for j in range(0,8):
            if (crc & 0x8000) > 0:
                crc =(crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    return crc & 0xFFFF


if __name__ == "__main__":
    """ Main entry point """

    rxMsgQueue = Queue()
    inputQueue = Queue()
    serialThread = SerialThread("COM5", rxMsgQueue)
    serialThread.start()

    inputThread = InputThread(inputQueue)
    inputThread.start()

    print("Press key S to send buffer")

    while (True):
        try:
            msg = rxMsgQueue.get(False)
            rxMsgQueue.task_done()
            print("<<< "+str(msg))
        except Empty:
            pass

        try:
            input = inputQueue.get(False)
            inputQueue.task_done()
            if (input == 's' or input == 'S'):
                print("Send buffer")
                random_array = [random.randint(21, 126) for _ in range(2048)]
                #compute simple CRC
                crc = crc16(random_array, len(random_array))
                print(hex(crc))
                serialThread.write(random_array)

        except Empty:
            pass


