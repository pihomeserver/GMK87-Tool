import time
import json
from types import SimpleNamespace

debugMode = False

CMD_EMPTY_COMMAND                   = 0x00
CMD_GET_PROTOCOL_VERSION            = 0x01
CMD_GET_KEYBOARD_VALUE              = 0x02
CMD_SET_KEYBOARD_VALUE              = 0x03
CMD_VIA_DYNAMIC_KEYMAP_GET_KEYCODE  = 0x04
CMD_VIA_DYNAMIC_KEYMAP_SET_KEYCODE  = 0x05
CMD_VIA_DYNAMIC_KEYMAP_RESET        = 0x06
CMD_LIGHTING_SET_VALUE              = 0x07
CMD_LIGHTING_GET_VALUE              = 0x08
CMD_GET_KEYBOARD_LAYERS             = 0x11

SUBCMD_SET_UNDERGLOW_BRIGHTNESS     = 0x80
SUBCMD_SET_UNDERGLOW_MODE           = 0x81
SUBCMD_SET_UNDERGLOW_SPEED          = 0x82
SUBCMD_SET_RGBLIGHT_COLOR           = 0x83

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

def printRawData(data):
    print(''.join('\\x{:02x}'.format(letter) for letter in data))

def sendCheckCommand(device, cmd, subcmd, subDataSet = []) -> bytearray:
    data = bytearray(3)
    data[0x00] = 0x00
    data[0x01] = cmd
    data[0x02] = subcmd
    data.extend(subDataSet)
    additionalData = bytearray(33 - len(data))
    data.extend(additionalData)

    if debugMode: 
        print("\nSending data")
        printRawData(data)

    send_data(device, data)
    time.sleep(0.05)
    while True:
        response = device.read(32)
        if response:
            if debugMode: 
                print("\nReceiving data")
                printRawData(response)
            return response
        else:
            break
    return []

def loadConfigurationFromFile(filename) :
    global debugMode
    with open(filename) as f:
        config = json.load(f)
        debugMode = config.get('debug', False)
        if debugMode: print("\nConfiguration loaded")

        return(config)    