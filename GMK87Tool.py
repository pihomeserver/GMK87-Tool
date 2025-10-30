#!/usr/bin/env python3

import hid # from hidapi (not hid)
import math
import time
from datetime import datetime
import utils
import argparse, os

class Keyboard():
    def __init__(self):
        self.kbVIAProtocol = 0
        self.kbLayers = -1
        self.name: ""
        self.manufacturer = ""
        self.vendorId = ""
        self.productId = ""
        self.path = ""

currentKeyboard = Keyboard()

def updateConfigFrame(device, config):
    if utils.debugMode: print("Building configuration frame")
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
    data[0x09] = config.get('config').get('underglow_effect', 0x01)

    # 0x0a = LED backlight brightness
    # 0x00 = off
    # 0x09 = maximum
    data[0x0a] = config.get('config').get('underglow_brightness', 0x02)

    # 0x0b = LED backlight speed
    # 0x00 = fast
    # 0x09 = slow
    data[0x0b] = config.get('config').get('underglow_speed', 0x02)

    # 0x0c = LED underglow orientation
    # 0x00 = Left to right
    # 0x01 = Right to left
    data[0x0c] = config.get('config').get('underglow_orientation', 0x01)

    # 0x0c = LED backlight mode
    # 0x00 = Hue mode only
    # 0x01 = Multiple color mode
    data[0x0d] = config.get('config').get('underglow_rainbow', 0x01)

    # 0x0e, 0x0f, 0x10 = LED backlight hue
    # 0x0e = Red (0x00 -> 0xff)
    # 0x0f = Green (0x00 -> 0xff)
    # 0x10 = Blue (0x00 -> 0xff)
    data[0x0e] = config.get('config').get('underglow_hue').get('red', 0xff)
    data[0x0f] = config.get('config').get('underglow_hue').get('green', 0xff)
    data[0x10] = config.get('config').get('underglow_hue').get('blue', 0xff)

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
    data[0x1d] = config.get('config').get('winlock', 0x00)

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
    data[0x24] = config.get('config').get('led_mode', 0x00)

    # 0x25 = Big led saturation
    # 0x00 = off
    # 0x09 = maximum
    data[0x25] = config.get('config').get('led_saturation', 0x00)

    # 0x26 = ??
    data[0x26] = 0x00

    # 0x27 = Big led color type
    # 0x00 = Hue mode only
    # 0x01 = Rainbow color mode
    data[0x27] = config.get('config').get('led_rainbow', 0x01)

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
    data[0x28] = config.get('config').get('led_color', 0x00)

    # 0x29 = Show image 0(time)/1/2
    # 0x00 = Show time
    # 0x01 = Show image 1
    # 0x02 = Show image 2
    data[0x29] = config.get('config').get('show_image', 0x00)
    
    # 0x2a = Frame count in image 1
    # 0x00 = Disable image (could not be displayed)
    # 0x?? = Number of frames of the images. Can be used to reactivate the image
    data[0x2a] = config.get('config').get('image1').get('frames', 0x00)

    # 0x2b ... 0x31 = define time amd date
    data[0x2b] = utils.to_hex_num(now.second)
    data[0x2c] = utils.to_hex_num(now.minute)
    data[0x2d] = utils.to_hex_num(now.hour)
    data[0x2e] = utils.to_hex_num(now.weekday())
    data[0x2f] = utils.to_hex_num(now.day)
    data[0x30] = utils.to_hex_num(now.month)
    data[0x31] = utils.to_hex_num(int(math.fmod(now.year, 100)))

    # frameDuration = 1000 # in ms
    # frameDurationLsb = frameDuration & 0xff
    # frameDurationMsb = (frameDuration >> 8) & 0xff 
    #data[0x33] = frameDurationLsb
    #data[0x34] = frameDurationMsb

    # 0x36 = Frame count in image 2
    data[0x36] = config.get('config').get('image2').get('frames', 0x00)

    # Checksum of the frame
    chk = utils.checksum(data[3:])
    data[0x01] = chk & 0xff # checksum LSB
    data[0x02] = (chk >> 8) & 0xff # checksum MSB

    # Print exact data block send to the keyboard
    if utils.debugMode: utils.printRawData(data)

    if utils.debugMode: print("Sending new configuration frame")
    utils.send_data(device, data)
    if utils.debugMode: print("New configuration frame sent")

def getKeyboardConfiguration(device, config):
    currentKeyboard.name = device.get_product_string()
    currentKeyboard.manufacturer = device.get_manufacturer_string()
    currentKeyboard.vendorId = config.get('keyboard').get('vendor_id')
    currentKeyboard.productId = config.get('keyboard').get('product_id')
    currentKeyboard.usageId = config.get('keyboard').get('usage_check')

    getViaProtocolVersion(device)
    if currentKeyboard.kbVIAProtocol > 0:
        getLayerCount(device)
    if utils.debugMode: 
        print("\nKeyboard configuration:\n")
        print(" * Name: ", currentKeyboard.name)
        print(" * Manufacturer: ", currentKeyboard.manufacturer)
        print(" * Vendor ID: ", currentKeyboard.vendorId)
        print(" * Product ID: ", currentKeyboard.productId)
        print(" * Usage ID: ", currentKeyboard.usageId)
        print(" * Path: ", currentKeyboard.path)
        print(" * VIA Protocol: ", currentKeyboard.kbVIAProtocol)
        print(" * Layers: ", currentKeyboard.kbLayers)

def getBacklightValue(device):
    value = utils.sendCheckCommand(device, utils.CMD_LIGHTING_GET_VALUE, 0, [])

def getLayerCount(device):
    layers = utils.sendCheckCommand(device, utils.CMD_GET_KEYBOARD_LAYERS, 0, [])
    if (len(layers) > 0):
        currentKeyboard.kbLayers = layers[1]

def getViaProtocolVersion(device):
    protocolData = utils.sendCheckCommand(device, utils.CMD_GET_PROTOCOL_VERSION, utils.CMD_EMPTY_COMMAND, [])
    if (len(protocolData) > 0):
        currentKeyboard.kbVIAProtocol = protocolData[2]

def validate_file(filename):
    if not os.path.exists(filename):
        raise argparse.ArgumentTypeError("{0} does not exist".format(filename))
    return filename        

def main():
    parser = argparse.ArgumentParser(   
                    prog='GMK87Tool',
                    description='Update the settings of a Zuoya GMK87 keyboard',
                    epilog='Please visit https://github.com/pihomeserver/GMK87-Tool for help and suggestions')
    
    parser.add_argument('-c', '--config', type=validate_file, help='Path to the JSON configuration file', required=True)

    args = parser.parse_args()

    try:
        config = utils.loadConfigurationFromFile(args.config)
        devices = hid.enumerate(int(config.get('keyboard').get('vendor_id')), int(config.get('keyboard').get('product_id')))
        deviceWithUsage = next((x for x in devices if x['usage'] == int(config.get('keyboard').get('usage_check'))), None)
        device = hid.device()
        device.open_path(deviceWithUsage['path'])
        
        currentKeyboard.path = deviceWithUsage['path']

        getKeyboardConfiguration(device, config)

        # r = utils.sendCheckCommand(device, \
        #     0x08, \
        #     utils.SUBCMD_SET_UNDERGLOW_BRIGHTNESS, \
        #     [])
        # print(r)

        # r = utils.sendCheckCommand(device, \
        #     utils.CMD_LIGHTING_SET_VALUE, \
        #     utils.SUBCMD_SET_UNDERGLOW_BRIGHTNESS, \
        #     [0x0f])
        # print(r)

        # For the full configuration frame, we have to use the device from another path
        deviceWithUsage = next((x for x in devices if x['usage'] == int(config.get('keyboard').get('usage_config'))), None)
        device = hid.device()
        device.open_path(deviceWithUsage['path'])
        updateConfigFrame(device, config)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'device' in locals() and device :
            if utils.debugMode: print("\nDevice closed")
            device.close()

if __name__ == "__main__":
   main()
