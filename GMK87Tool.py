#!/usr/bin/env python3

# https://docs.digi.com/resources/documentation/digidocs/90002386/os/python-hid-module-c.htm?TocPath=Applications%7C_____5

import hid # from hidapi (not hid)
import math
import time
from datetime import datetime
import argparse

GMK87_VENDOR_ID = 0x320f
GMK87_PRODUCT_ID = 0x5055
GMK87_USAGE = 146

def send_data(device, data):
    device.set_nonblocking(1)
    device.write(bytes(data))

def checksum(buf: bytes) -> int:
    chk = 0
    for v in buf:
        chk += v
    return chk

def to_hex_num(num: int) -> int:
    if num >= 100 or num < 0:
        raise ValueError("num is out of range (0-99)")
    low = num % 10
    high = num // 10
    return low + high * 16

def updateConfigFrame(device):
    print("Building configuration frame")
    now = datetime.now()

    data = bytearray(64)
    data[0x00] = 0x04 # report ID
    data[0x03] = 0x06 # Config command

    # 0x04 = Configuration
    # 0x29 = Turn off lights only ?
    # 0x30 = Full configration frame
    data[0x04] = 0x30

    # 0x09 = LED underglow effect
    # 0x00 = off
    # 0x01 = horizontal dimming wave
    # 0x02 = horizontal pulse wave
    # 0x03 = waterfall
    # 0x04 = full on, cycling colors
    # 0x05 = breathing
    # 0x06 = full on, one color
    # 0x07 = glow pressed key
    # 0x08 = glow spreading from pressed key
    # 0x09 = glow row of pressed key
    # 0x0a = random pattern, one color
    # 0x0b = full on, rainbow color cycle
    # 0x0c = full on, rainbow waterfall
    # 0x0d = continuous wave originating from center, one color
    # 0x0e = circling j/k keys, then spreading outward, one color
    # 0x0f = raining, one color
    # 0x10 = wave left/right back and forth, one color
    # 0x11 = full on, slow color saturation cycle
    # 0x12 = full on, slow outward rainbow origination from center
    # 0x13+ not tested
    data[0x09] = 0x01

    # 0x0a = LED backlight brightness
    # 0x00 = off
    # 0x09 = maximum
    data[0x0a] = 0x02

    # 0x0b = LED backlight speed
    # 0x00 = fast
    # 0x09 = slow
    data[0x0b] = 0x03

    # 0x0c = LED underglow orientation
    # 0x00 = Left to right
    # 0x01 = Right to left
    data[0x0c] = 0x00

    # 0x0c = LED backlight mode
    # 0x00 = Hue mode only
    # 0x01 = Multiple color mode
    data[0x0d] = 0x01

    # 0x0e, 0x0f, 0x10 = LED backlight hue
    # 0x0e = Red (0x00 -> 0xff)
    # 0x0f = Green (0x00 -> 0xff)
    # 0x10 = Blue (0x00 -> 0xff)
    data[0x0e] = 0xff
    data[0x0f] = 0x00
    data[0x10] = 0x00

    data[0x11] = 0x00 # ??
    data[0x12] = 0x00 # ??
    data[0x13] = 0x00 # ??
    data[0x14] = 0x00 # ??
    data[0x15] = 0x00 # ??
    data[0x16] = 0x00 # ??
    data[0x17] = 0x00 # ??
    data[0x18] = 0x00 # ??
    data[0x19] = 0x00 # ??
    data[0x1a] = 0x00 # ??
    data[0x1b] = 0x00 # ??
    data[0x1c] = 0x00 # ??

    # 0x1d = Lock windows key
    # 0x00 = off
    # 0x01 = on
    data[0x1d] = 0x00

    data[0x1e] = 0x00 # ??
    data[0x1f] = 0x00 # ??
    data[0x20] = 0x00 # ??
    data[0x21] = 0x00 # ??
    data[0x22] = 0x00 # ??
    data[0x23] = 0x00 # ??

    # 0x24 = Big led mode
    # 0x00 = One color blinking. Color defined in 0x28
    # 0x01 = One pulse off and color rainbow
    # 0x02 = One color blinking. . Color defined in 0x28
    # 0x03 = Fixed color. Color defined in 0x28
    # 0x04 = Fixed color. Color defined in 0x28
    data[0x24] = 0x00

    # 0x25 = Big led saturation
    # 0x00 = off
    # 0x09 = maximum
    data[0x25] = 0x00

    # 0x26 = ??
    data[0x26] = 0x00

    # 0x27 = Big led color type
    # 0x00 = Hue mode only
    # 0x01 = Rainbow color mode
    data[0x27] = 0x00

    # 0x28 = Big led color
    # 0x00 = Red
    # 0x01 = orange
    # 0x02 = yellow
    # 0x03 = green
    # 0x04 = teal
    # 0x05 = blue
    # 0x06 = purple
    # 0x07 = white
    # 0x08 = off
    # 0x09+ are repeating colors in some order?
    data[0x28] = 0x01

    # 0x29 = Show image 0(time)/1/2
    # 0x00 = Show time
    # 0x01 = Show image 1
    # 0x02 = Show image 2
    data[0x29] = 0x00
    
    # 0x2a = Frame count in image 1
    data[0x2a] = 0x30

    # 0x2b ... 0x31 = define time amd date
    data[0x2b] = to_hex_num(now.second)
    data[0x2c] = to_hex_num(now.minute)
    data[0x2d] = to_hex_num(now.hour)
    data[0x2e] = to_hex_num(now.weekday())
    data[0x2f] = to_hex_num(now.day)
    data[0x30] = to_hex_num(now.month)
    data[0x31] = to_hex_num(int(math.fmod(now.year, 100)))

    # frameDuration = 1000 # in ms
    # frameDurationLsb = frameDuration & 0xff
    # frameDurationMsb = (frameDuration >> 8) & 0xff 
    #data[0x33] = frameDurationLsb
    #data[0x34] = frameDurationMsb

    # 0x36 = Frame count in image 2
    data[0x36] = 0x00

    # Checksum of the frame
    chk = checksum(data[3:])
    data[0x01] = chk & 0xff # checksum LSB
    data[0x02] = (chk >> 8) & 0xff # checksum MSB

    # Print exact data block send to the keyboard
    #print(''.join('\\x{:02x}'.format(letter) for letter in data))

    print("Sending new configuration frame")
    send_data(device, data)
    print("New configuration frame sent")
 
def main():
    try:
        devices = hid.enumerate(GMK87_VENDOR_ID, GMK87_PRODUCT_ID)
        deviceWithUsage = next((x for x in devices if x['usage'] == GMK87_USAGE), None)
        device = hid.device()
        device.open_path(deviceWithUsage['path'])

        print("Device opened in path ", deviceWithUsage['path'])
        print("Manufacturer: ",device.get_manufacturer_string())
        print("Product: ",device.get_product_string())
        updateConfigFrame(device)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'device' in locals() and device :
            print("Device closed")
            device.close()

if __name__ == "__main__":
   main()
