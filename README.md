Python script to update settings, time and clock of a Zuoya GMK87 keyboard
*Inspired from https://github.com/ikkentim/gmk87-usb-reverse*

# Features
The script can update the following parameters
* Underglow effect
* LED backlight brightness
* LED backlight speed
* LED effect orientation
* LED backlight mode
* LED backlight hue
* Lock windows key
* Big led mode
* Big led saturation
* Big led color type
* Big led color
* Selection of the screen image to display (**no upload is possible for now**)
* Time
* Date

## Warning
It has been tested only under Arch. For Windows, please look at https://github.com/ikkentim/gmk87-usb-reverse

## To do
* Find saturation parameter
* Find how to retrieve settings from the keyboard to update only specific settings instead of all
* Upload images feature

# Install

On Arch
```
pacman -S python-hidapi
```
Then clone the repo and run the `GMK87Tool.py` script with the configuration file as parameter
**Not tested with python hid**


# Execution

```
sudo python GMK87Tool.py -c config.json
```

## Why sudo is needed
The script has to write to the device block. By default (at least in Arch), devices are owned by root

## I don't want to use sudo
You can identify the device block with the HIDList script
```
python HIDList.py
```
The correct device block has the following parameters :
```
product_id : 20565
usage : 146
vendor_id : 12815
```
Get the path of the block, for example :
```
path : b'/dev/hidraw3'
```
Then 
```
sudo chown $USER:$USER <provide the path like /dev/hidraw3 without the b and quotes>
```
