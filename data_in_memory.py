# -*- coding: utf-8 -*-
"""
Test code to see how float in memoy
This is a temporary script file.
"""
import struct

def float_to_bytes(f):
    return struct.pack('f', f)

while True:
    user_input = input("Enter a float value: ")
    
    try:
        # Convert the input to a float
        my_float = float(user_input)
        
        # Convert the float to bytes
        bytes_representation = float_to_bytes(my_float)
        
        # Print the byte representation
        print("Byte representation:", bytes_representation)
        break  # Exit the loop if the input is valid
    except ValueError:
        print("Invalid input. Please enter a valid float value.")

