#!/usr/bin/env python3

# https://docs.digi.com/resources/documentation/digidocs/90002386/os/python-hid-module-c.htm?TocPath=Applications%7C_____5

import hid # from hidapi (not hid)
import math
import time
from datetime import datetime
import argparse

GMK87_VENDOR_ID = 0x320f
GMK87_PRODUCT_ID = 0x5055

def send_data(device, data):
    print("** Sending", len(data), "bytes **************")
    device.set_nonblocking(1)
    device.write(bytes(data))

def checksum(buf: bytes) -> int:
    chk = 0
    for v in buf:
        chk += v
    return chk

def to_hex_num(num: int) -> int:
    # print("to_hex_num. input : ", num)
    if num >= 100 or num < 0:
        raise ValueError("num is out of range (0-99)")
    low = num % 10
    high = num // 10
    # print("to_hex_num. output : ", (low + high * 16).to_bytes())
    return low + high * 16

def sendConfigFrame(device, command, dataCommand = []):
    data = bytearray(2)
    data[0x00] = 0x00 # command start
    data[0x01] = command
    data.extend(dataCommand)
    additionalData = bytearray(33 - len(data))
    data.extend(additionalData)

    # print("** Printable data (", len(data), ") **************")
    # print(data)
    # print("** Raw data (", len(data),")**************")
    # print(''.join('\\x{:02x}'.format(letter) for letter in data))

    send_data(device, data)
    
    # print("Timer for answer")
    time.sleep(0.05)
    # # read back the answer
    print("Get answer")
    while True:
        d = device.read(32)
        if d:
            print(d)
        else:
            print("Break")
            break

def getProtoclVersion(device):
    command = 0x01
    sendConfigFrame(device, command)

def getBrightness(device):
    command = 0x07
    dataCommand = [0x09]
    sendConfigFrame(device, command, dataCommand)

def getRGB(device):
    command = 0x08
    dataCommand = [0x0a]
    sendConfigFrame(device, command, dataCommand)
 
def setRGB(device, mode):
    command = 0x07
    dataCommand = [0x0a, mode]
    sendConfigFrame(device, command, dataCommand)
 
def saveLightning(device):
    command = 0x09
    sendConfigFrame(device, command)
 
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', dest='path', type=str, help='HID path to use. The user running the script must have the write access to it. Example : /dev/hidraw3')
    args = parser.parse_args()

    try:
        # print("Opening device in path ", GMK87_VENDOR_ID, GMK87_PRODUCT_ID)
        print("Opening device in path ", args.path)
        device = hid.device()
        if args.path :
            device.open_path(bytes(args.path, "utf-8" ))
        else :
            device.open(GMK87_VENDOR_ID, GMK87_PRODUCT_ID)
        print("Device opened")
        print("Manufacturer: ",device.get_manufacturer_string())
        print("Product: ",device.get_product_string())
        # getProtoclVersion(device)
        # getBrightness(device)
        # getRGB(device)
        # setRGB(device, 0x01) # WAVE FORM
        # getRGB(device)

        # Underglow brightness
        # sendConfigFrame(device, 0x07, [0x80, 0x0a])
        # Underglow effect
        # sendConfigFrame(device, 0x07, [0x81, 0x01])
        # Underglow effect speed
        # sendConfigFrame(device, 0x07, [0x82, 0x00])
        
        sendConfigFrame(device, 0x07, [0x81, 0x01])

        # time.sleep(0.5)

        # Save lighting configuration
        # sendConfigFrame(device, 0x09)

        # time.sleep(0.5)

        # Ask for underglow effect

        # sendConfigFrame(device, 0x08, [0x80])
        # sendConfigFrame(device, 0x08, [0x81])
        # sendConfigFrame(device, 0x08, [0x82])

        sendConfigFrame(device, 0x08, [0x81])


    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'device' in locals() and device :
            print("Device closed")
            device.close()

if __name__ == "__main__":
   main()
