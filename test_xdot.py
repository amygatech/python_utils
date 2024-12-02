#!/usr/bin/env python3
# test xdot

import sys
import os
import time
#import datetime 
import serial
from serial import SerialException
#import random
import csv
import signal
import struct
import re
import logging
#import threading

from functools import partial
from queue import Queue, Empty
from SerialUart import InputThread
import argparse

class XdotTest:
    def __init__(self, COM="COM5", join_delay=7.0, join_tries=3):
        # initialize serial values
        # Open the serial port
        self.serial = serial.Serial()
        self.serial.port = COM
        self.serial.timeout = 1
        self.serial.baudrate = 115200
        self.serial.bytesize = serial.EIGHTBITS
        self.serial.parity = serial.PARITY_NONE
        self.serial.stopbits = serial.STOPBITS_ONE
        self.serial.xonxoff = False            
        # initialize network join parameters
        self.join_delay = join_delay
        self.join_tries = join_tries

    def open_serial(self):
        '''attempt to open serial connection'''
        try:
            self.serial.open()
            print("Connected to serial port %s" %(self.serial.port))
        except SerialException:
            raise ValueError('Failed to open %s Port' %(self.serial.port))

    def close_serial(self):
        print("\n Close serial Port \n")
        self.serial.close()
    
    def join_network(self,join_tries=None,join_delay=None):
        '''attempts to join LoRaWAN network if not already connected'''
        # initialize default values
        if join_tries is None:
            join_tries = self.join_tries
        if join_delay is None:
            join_delay = self.join_delay

        already_connected = self.get_join_status()
        # if already connected, skip connecting
        if already_connected is True:
            print("NOTICE: xdot already connected to network") 
        # if not already connected, try to connect
        else:
            self.attempt_join(join_tries,join_delay)
            if self.get_join_status() is False:
                raise ValueError("connection status invalid despite successful connection")
            
    def attempt_join(self, join_tries=3, join_delay=7.0):
        '''tells xdot to join LoRaWAN network'''
        for i in range (join_tries):
            self.command_join(join_delay)
            response = self.serial.read_all().decode('utf-8')
            print(response)
            if (response.find("Successfully joined network") > 0):
                print("Joined network on attempt #",str(i+1))
                return True
        raise ValueError("unable to connect to network")

    def get_join_status(self):
        '''checks if the xdot is still connected to the network'''
        self.command_njs()
        response = self.serial.readall().decode()
        if re.search("AT\+NJS\?[\r\n]+1[\r\n]+OK",response):
            return True
        else:
            return False
        
    ## commands
        
    def command_join(self,delay=7.0):
        '''send command to join network'''
        command = "AT+JOIN\r"
        self.serial.write(command.encode())
        time.sleep(delay)

    def command_send(self, data_str, delay=0.15):
        '''send message via LoRaWAN'''
        command = "AT+SEND="+data_str+"\r"
        self.serial.write(command.encode())
        time.sleep(delay)
    
    def command_sendb(self, data_str, delay=0.15):
        '''send bytes via LoRaWAN'''
        command = "AT+SENDB="+data_str+"\r"
        #print("Send: ", command)
        print(f"Write Command : {command}") 
        self.serial.write(command.encode())
        time.sleep(delay)
    
    def command_urc(self,delay=0.15):
        '''send command to receive unsolicited messages'''
        command = "AT+URC=1\r"
        self.serial.write(command.encode())
        time.sleep(delay)
        
    def command_config_class_c(self,delay=0.15):
        '''send config class C'''
        command = "AT+DC=C\r"
        self.serial.write(command.encode())
        time.sleep(delay)
        
    def command_recv(self,delay=0.15):
        '''send command to read received message'''
        command = "AT+RECV\r"
        self.serial.write(command.encode())
        time.sleep(delay)

    def command_njs(self,delay=0):
        '''send command to check network join status'''
        command = "AT+NJS?\r"
        self.serial.write(command.encode())
        time.sleep(delay)
    
    def command_rxo(self,delay=0.15,setting=3):
        '''send command to set receive output format'''
        command = "AT+RXO=" + str(setting) + "\r"
        self.serial.write(command.encode())
        time.sleep(delay)

    def command_adr(self,delay=0.15,setting=0):
        '''send command to adjust adaptive data rate setting, defaulting to off'''
        command = "AT+ADR=" + str(setting) + "\r"
        self.serial.write(command.encode())
        time.sleep(delay)

    def command_txdr(self,delay=0.15,setting="DR1"):
        '''send command to adjust data rate, defaulting to 53 bytes'''
        command = "AT+TXDR=" + str(setting) + "\r"
        self.serial.write(command.encode())
        time.sleep(delay)

####---ENd class XDotTest commands#######################
##########################################################

###########################################
# CSV classs
###########################################

class CSVReader:
    def __init__(self, relative_path):
        # Use the relative path provided
        self.file_path = os.path.join(os.getcwd(), relative_path)
        self.data = []

    def read_csv(self):
        # Ensure the file exists
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File '{self.file_path}' not found.")
        
        # Read CSV data
        with open(self.file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            # Skip the header
            header = next(csv_reader)
            print(f"Header: {header}")
            
            # Store data as a list of tuples (epoch_time, adc_value)
            self.data = [
                (row[0],  row[1])  # Convert hex epoch_time to int and adc_value to float
                for row in csv_reader
                ]
            return self.data
        
            # Process the rows
            #for row in csv_reader:
            #    epoch_time = row[0]  # First column
            #    adc_value = row[1]   # Second column
            #    # Print the processed data
            #    print(f"Epoch Time (Hex): {epoch_time},  ADC Value: {adc_value}")
   
            #self.data = [row for row in csv_reader]
            #---------------------------------------



    def display_data(self):
        # Print the data row by row
        if not self.data:
            print("No data loaded. Please read the CSV first.")
        else:
            for row in self.data:
                print(row)
    
    def remove_hex_prefix(self, hex_str):
        return hex_str[2:] if hex_str.startswith("0x") else hex_str
    
    def float_to_hex(self, float_val):
        # Convert float to its IEEE 754 hex representation
        #return hex(struct.unpack('<I', struct.pack('<f', float_val))[0])
        # Convert float to its IEEE 754 hex representation without the '0x' prefix
        return format(struct.unpack('<I', struct.pack('<f', float_val))[0], 'x')
 
    ##########################End Class CSVReader################
    #############################################################



def read_file_and_send_data(file_name , xdot: XdotTest):
    ''' Read csv data file and send over xdot'''
    
    if xdot.get_join_status() is False:
        raise ValueError("<ERROR> xdot connection failed. Need to connnect xdot!")

    
    csv_reader = CSVReader(file_name)
    try:
        # Attempt to read and display the file's contents
        data_in_csv_file = csv_reader.read_csv()
        #reader.display_data()
    except FileNotFoundError as e:
        print(e)
        
    # Loop through the data and process each entry
    for epoch_time, adc_value in data_in_csv_file:
        epoch_value = csv_reader.remove_hex_prefix(epoch_time)
        # Convert ADC value to hex (without the '0x' prefix)
        hex_adc_value = csv_reader.float_to_hex(float(adc_value))
        #print(f"Epoch Time: {epoch_value}, ADC Value: {adc_value}, ADC Value (Hex): {hex_adc_value}")
        #print(f"Epoch Time: {epoch_value}, ADC Value: {adc_value}") 
        hex_str_combine = epoch_value + hex_adc_value
        #print(hex_str_combine)
        xdot.command_sendb(hex_str_combine, 0.5)
        time.sleep(1.5) # sleep in second
        




def setup_classc(xdot):
    '''runs commands to connect to and setup class C serial communication with LoRaWAN gateway'''
    xdot.open_serial()
    xdot.command_urc()

    # connect and send
    xdot.join_network()
    xdot.command_send("msg1")
    xdot.command_send("msg2")


def get_time():
    return time.strftime("%Y-%m-%dT%H%M%S",time.localtime())




######################################################  
# define file and com port
######################################################   

#xdot = XdotTest(COM="COM5")
# Example Usage
#file_path = "data/2024-11-28T00_46_03_UTC.216.csv"  # Direct relative path to your CSV file

#################################################
# Handler Ctrl+C Interrupt
#################################################
# Handler Ctrl+C Interrupt
def interrupt_handler(xdot, signum, frame, ask=True):
    print(f'Handling signal {signum} ({signal.Signals(signum).name}).')
    if ask:
        signal.signal(signal.SIGINT, partial(interrupt_handler, xdot, ask=False))
        print('To confirm interrupt, press ctrl-c again.')
        return

    print('Cleaning/exiting...')
    xdot.close_serial()
    time.sleep(1)
    sys.exit(0)
    
    
#########################
# Main 
#########################    
def main():
    # Set up the command-line argument parser
   parser = argparse.ArgumentParser(description="XdotTest COM port selector.")
   parser.add_argument('--COM', type=str, default='COM5', help="Specify the COM port (e.g., COM5, COM7). Default is COM5.")
   args = parser.parse_args()

   # Initialize XdotTest with the specified COM port
   xdot = XdotTest(COM=args.COM)
   # Set the signal handler for graceful shutdown
   signal.signal(signal.SIGINT, partial(interrupt_handler, xdot))
   # Example usage of file_path
   file_path = "data/2024-11-28T00_46_03_UTC.216.csv"  # Direct relative path to your CSV file
   print(f"File path is set to: {file_path}")
    
   # Set up the logger
   current_time = get_time()
   log_file = "./logs/" + current_time + ".log"
   logging.basicConfig(filename=log_file,
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
   # Check if the log file is created
   if os.path.isfile(log_file):
       print(f'Log file created successfully: {os.path.abspath(log_file)}')
   else:
       print('Failed to create log file')


   logging.info(get_time() + ": Open Xdot Device")
   # Open xdot device
   xdot.open_serial()
   logging.info(get_time() + ": Join Network")
   xdot.join_network()
   #increase tx size
   xdot.command_adr()
   xdot.command_txdr()
    
   logging.info(get_time() + ": Read file and send data")
   read_file_and_send_data(file_path,xdot)
   logging.info(get_time() + ": Close xdot device")
   xdot.close_serial()
   
    
if __name__ == '__main__':
    #signal.signal(signal.SIGINT, interrupt_handler)

    main()
    
    
    