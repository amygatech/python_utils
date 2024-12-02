# -*- coding: utf-8 -*-
"""
Created on Sat Oct  5 17:36:00 2024

@author: atran
"""

import struct
import base64
import binascii

def float_to_hex(f):
    return hex(struct.unpack('<I', struct.pack('<f', f))[0])

def hex_to_float(hex_value):
    return struct.unpack('!f', bytes.fromhex(hex_value))[0]

def hex_to_ascii(hex_string):
    # Convert hex string to bytes
    byte_data = bytes.fromhex(hex_string)
    # Convert bytes to ASCII string
    ascii_string = byte_data.decode('ascii')
    return ascii_string



def base64_to_ascii(base64_string):
    # Decode the base64 string to bytes
    decoded_bytes = base64.b64decode(base64_string)
    # Convert bytes to ASCII string
    ascii_string = decoded_bytes.decode('ascii')
    return ascii_string



def base64_to_hex(base64_string):
    # Decode the base64 string to bytes
    decoded_bytes = base64.b64decode(base64_string)
    # Convert bytes to hex string
    hex_string = binascii.hexlify(decoded_bytes).decode('utf-8')
    return hex_string

def ascii_to_base64(ascii_string):
    # Convert ASCII string to bytes
    byte_data = ascii_string.encode('ascii')
    # Encode bytes to base64
    base64_encoded = base64.b64encode(byte_data)
    # Convert bytes to string
    return base64_encoded.decode('ascii')

def ascii_to_hex(text):
    # Convert each character to its hexadecimal equivalent and join them
    hex_output = ''.join(format(ord(c), '02x') for c in text)
    return hex_output


####################################
#extract hex value
# Example input
#input_string = "RECV 016c3d3600070000000148656c6c6f416d79"
#extract_hex_data(input_string)
#Extracted hex data: 48656c6c6f416d79
######################################
def extract_hex_data(input_string):
    # Define the prefix to look for
    prefix = "RECV "
    
    # Check if the input starts with "RECV "
    if input_string.startswith(prefix):
        # Extract the part after "RECV "
        hex_data = input_string[len(prefix):]

        # Skip the first 10 bytes (20 hex characters)
        if len(hex_data) > 20:
            extracted_hex = hex_data[20:]
            print(f"Extracted hex data: {extracted_hex}")
        else:
            print("Not enough data to skip 10 bytes.")
    else:
        print("Prefix 'RECV' not found in the input.")




# Example usage:
#hex_string = '48656c6c6f20776f726c6421'
#ascii_string = hex_to_ascii(hex_string)
#print(ascii_string)  # Output: Hello world!



# Example usage:
#base64_string = 'SGVsbG8gd29ybGQh'
#hex_string = base64_to_hex(base64_string)
#print(hex_string)  # Output: 48656c6c6f20776f726c6421


# Example usage:
#print(float_to_hex(3.14))  # Output: '0x4048f5c3'
