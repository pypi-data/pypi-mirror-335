# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for ATMegaZero ESP32-S2
 - port: espressif
 - board_id: atmegazero_esp32s2
 - NVM size: 8192
 - Included modules: _asyncio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
IO0: microcontroller.Pin  # GPIO0
IO1: microcontroller.Pin  # GPIO1
IO2: microcontroller.Pin  # GPIO2
IO3: microcontroller.Pin  # GPIO3
IO4: microcontroller.Pin  # GPIO4
IO5: microcontroller.Pin  # GPIO5
IO6: microcontroller.Pin  # GPIO6
IO7: microcontroller.Pin  # GPIO7
IO8: microcontroller.Pin  # GPIO8
IO9: microcontroller.Pin  # GPIO9
IO10: microcontroller.Pin  # GPIO10
IO11: microcontroller.Pin  # GPIO11
IO12: microcontroller.Pin  # GPIO12
IO13: microcontroller.Pin  # GPIO13
IO14: microcontroller.Pin  # GPIO14
IO17: microcontroller.Pin  # GPIO17
IO18: microcontroller.Pin  # GPIO18
IO21: microcontroller.Pin  # GPIO21
IO33: microcontroller.Pin  # GPIO33
IO34: microcontroller.Pin  # GPIO34
IO35: microcontroller.Pin  # GPIO35
IO36: microcontroller.Pin  # GPIO36
IO37: microcontroller.Pin  # GPIO37
IO38: microcontroller.Pin  # GPIO38
IO40: microcontroller.Pin  # GPIO40
IO43: microcontroller.Pin  # GPIO43
IO44: microcontroller.Pin  # GPIO44
PD5: microcontroller.Pin  # GPIO0
D5: microcontroller.Pin  # GPIO1
D6: microcontroller.Pin  # GPIO2
A5: microcontroller.Pin  # GPIO3
D7: microcontroller.Pin  # GPIO4
HWD: microcontroller.Pin  # GPIO5
A4: microcontroller.Pin  # GPIO6
D9: microcontroller.Pin  # GPIO7
D2: microcontroller.Pin  # GPIO8
D3: microcontroller.Pin  # GPIO9
D12: microcontroller.Pin  # GPIO10
D13: microcontroller.Pin  # GPIO11
A3: microcontroller.Pin  # GPIO12
A2: microcontroller.Pin  # GPIO13
AREF: microcontroller.Pin  # GPIO14
A0: microcontroller.Pin  # GPIO17
A1: microcontroller.Pin  # GPIO18
D10: microcontroller.Pin  # GPIO21
D4: microcontroller.Pin  # GPIO33
D8: microcontroller.Pin  # GPIO34
D14: microcontroller.Pin  # GPIO35
D15: microcontroller.Pin  # GPIO36
D16: microcontroller.Pin  # GPIO37
D11: microcontroller.Pin  # GPIO38
D1: microcontroller.Pin  # GPIO43
D2: microcontroller.Pin  # GPIO44
SD_CS: microcontroller.Pin  # GPIO0
SDA: microcontroller.Pin  # GPIO8
SCL: microcontroller.Pin  # GPIO9
DAC1: microcontroller.Pin  # GPIO17
DAC2: microcontroller.Pin  # GPIO18
MISO: microcontroller.Pin  # GPIO37
SCK: microcontroller.Pin  # GPIO36
MOSI: microcontroller.Pin  # GPIO35
NEOPIXEL: microcontroller.Pin  # GPIO40
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
