#!/usr/bin/env python
#
#   Documentation: z21-lan-protokoll-en.pdf
#   https://www.z21.eu/en/downloads/manuals
#
#   Inspired by on: https://gitlab.com/z21-fpm/z21_python
#
#   2023-10-27 Tested on DR5000 via LAN
#
#   [z21.py] <----- (LAN) -----> [DR5000]  <----- (2-wire rails) -----> [LokSound5]
#
import logging
import struct
import sys
import time
from socket import socket, timeout, AF_INET, SOCK_STREAM, SOCK_DGRAM

# byteorder is positional to be compatible with micropython
# https://docs.micropython.org/en/latest/library/builtins.html#int.from_bytes
BYTEORDER = "little"
BIGORDER = 'big'

PORT = 21105 # Default port number for Z21
ON = 'on'
OFF = 'off'
TOGGLE = 'toggle'

def printCmd(sender, cmd):
    s = sender
    for b in cmd:
        s += '%02X ' % b
    print(s)

def ADDRESS(locoAddress):
    """Convert a locoAddress integer into a 2-byte array"""
    return locoAddress.to_bytes(2, BIGORDER)

def XOR(b):
    """Answer the XOR-parity byte from the byte-array that is necessary for most Z21 commands."""
    xor = None
    for byte in bytes(b):
        if xor is None:
            xor = byte
        else:
            xor = xor ^ byte
    return xor.to_bytes(1, BYTEORDER)

def CMD(*args):
    """Construct the byte-array from a list of arguments. If the argument is None, then substitute the XOR checksum, 
    based on the array if previous bytes. This way the Z21 class can define the layout of commands by templates.
        LAN_X_SET_TRACK_POWER_ON =      CMD(0x07, 0, 0x40, 0, 0x21, 0x81, None) # XOR: 0xa0, Z21: 2.6
    """
    b = b'' # Start with empty byte string
    xor = None # If still None at the end, then the XOR will be calculated on the cumulated @b bytes.
    for index, i in enumerate(args): # For all arguments in this call
        if i is None: # Place holder to fill XOR, of all bytes after the 4 byte header
            xor = XOR(b[4:])
        else:
            byte = i.to_bytes(1, BYTEORDER)
            b += byte
    if xor is not None:
        b += xor
    return b

class Z21:
    # None is replaced by calculated XOR 
    # Some commands need additional byte parameters, as indicated in the comment.
    # "Z21:" is referencing to the chapters in the z21-lan-protokoll-en.pdf manual.

    # Z21: 2 System, Status, Versions

    LAN_GET_SERIAL_NUMBER =         CMD(0x04, 0, 0x10, 0) # No checksum, Z21: 2.1
    LAN_LOGOFF =                    CMD(0x04, 0, 0x30, 0) # No checksum, Z21: 2.2
    LAN_GET_VERSION =               CMD(0x07, 0, 0x40, 0, 0x21, 0x21, None) # XOR: 0x00, Z21: 2.3

    LAN_X_GET_STATUS =              CMD(0x07, 0, 0x40, 0, 0x21, 0x24, None) # XOR: 0x05, Z21: 2.4
    LAN_X_SET_TRACK_POWER_OFF =     CMD(0x07, 0, 0x40, 0, 0x21, 0x80, None) # XOR: 0xa1, Z21: 2.5
    LAN_X_SET_TRACK_POWER_ON =      CMD(0x07, 0, 0x40, 0, 0x21, 0x81, None) # XOR: 0xa0, Z21: 2.6

    LAN_X_BC_TRACK_POWER_OFF =      CMD(0x07, 0, 0x40, 0, 0x61, 0x00, None) # XOR: 0x61, Z21: 2.7
    LAN_X_BC_TRACK_POWER_ON =       CMD(0x07, 0, 0x40, 0, 0x61, 0x01, None) # XOR: 0x60, Z21: 2.8
    LAN_X_BC_PROGRAMMING_MODE =     CMD(0x07, 0, 0x40, 0, 0x61, 0x02, None) # XOR: 0x63, Z21: 2.9
    LAN_X_BC_TRACK_SHORT_CIRCUIT =  CMD(0x07, 0, 0x40, 0, 0x61, 0x08, None) # XOR: 0x69, Z21: 2.10
    LAN_X_UNKNOWN_COMMAND =         CMD(0x07, 0, 0x40, 0, 0x61, 0x82, None) # XOR: 0xE3, Z21: 2.11
    #LAN_X_STATUS_CHANGED =          CMD(0x08, 0, 0x40, 0, 0x62, 0x22, Status, XOR-Byte) # Z21: 2.11

    LAN_X_SET_STOP =                CMD(0x06, 0, 0x40, 0, 0x80, None) # XOR: 0x80, Z21: 2.13
    LAN_X_BC_STOPPED =              CMD(0x07, 0, 0x40, 0, 0x81, 0, None) # XOR: 0x81, Z21: 2.14
    LAN_X_GET_FIRMWARE_VERSION =    CMD(0x07, 0, 0x40, 0, 0xF1, 0x0A, None) # XOR: 0xFB, Z21: 2.15
    LAN_SET_BROADCASTFLAGS =        CMD(0x08, 0, 0x50, 0, 0) # Add 32 bits broadcast flags, Z21: 216
    LAN_GET_BROADCASTFLAGS =        CMD(0x04, 0, 0x51, 0) # Z21: 2.17

    LAN_SYSTEMSTATE_DATACHANGED =   CMD(0x14, 0, 0x84, 0, 0) # Add 16 bytes data, Z21: 2.18
    LAN_SYSTEMSTATE_GETDATA =       CMD(0x04, 0, 0x85, 0) # Z21: 2.19
    LAN_GET_HWINFO =                CMD(0x04, 0, 0x1A, 0) # Z21: 2.20
    LAN_GET_CODE =                  CMD(0x04, 0, 0x18, 0) # Z21: 2.21

    # Z21: 3 Settings
    LAN_GET_LOCOMODE =              CMD(0x06, 0, 0x60, 0) # Add 16 bits loco address, big endian, Loco #0, Z21: 3.1
    LAN_SET_LOCOMODE =              CMD(0x07, 0, 0x61, 0) # Add 16 bits loco address, big endian, Mode 8 bit, Loco #0, Z21: 3.1
    LAN_GET_TURNOUTMODE =           CMD(0x06, 0, 0x70, 0) # Add 16 bits Accessory Decoder Address, big endian), Z21: 3.3
    LAN_SET_TURNOUTMODE =           CMD(0x06, 0, 0x71, 0) # Add 16 bits Accessory Decoder Address, (big endian) Mode 8 bit, Z21: 3.4

    # Z21: 4 Driving
    LAN_X_GET_LOCO_INFO =           CMD(0x09, 0, 0x40, 0, 0xE3, 0xF0) # Add address MSB, address LSB and XOR-Byte, Z21: 4.1
    LAN_X_SET_LOCO_DRIVE =          CMD(0x0A, 0, 0x40, 0, 0xE4) # Add DCC steps, address MSB, address LSB, RVVV VVVV, XOR-Byte, Z21: 4.2
    LAN_X_SET_LOCO_FUNCTION =       CMD(0x0A, 0, 0x40, 0, 0xE4, 0xF8) # Add address MSB, address LSB, TTNN NNNN, XOR-Byte, Z21: 4.3.1
    LAN_X_SET_LOCO_FUNCTION_GROUP = CMD(0x0A, 0, 0x40, 0, 0xE4), # Add group, address MSB, address LSB, Functions, XOR-Byte, Z21: 4.3.2
    LAN_X_SET_LOCO_BINARY_STATE =   CMD(0x0A, 0, 0x40, 0, 0xE5, 0x5F) # Add address MSB, address LSB, FLLL LLLL, HHHH HHHH, XOR-Byte, Z21: 4.3.3
    # LAN_X_LOCO_INFO Z21: 4.4
    LAN_X_SET_LOCO_E_STOP =         CMD(0x08, 0, 0x40, 0, 0x92) # Add address MSB, address LSB, XOR-Byte, Z21: 4.5
    LAN_X_PURGE_LOCO =              CMD(0x09, 0, 0x40, 0, 0xE3, 0x44) # Add address MSB, address LSB, XOR-Byte, Z21: 4.6

    # Z21: 5 Switching
    # LAN_X_GET_TURNOUT_INFO Z21: 5.1
    # LAN_X_SET_TURNOUT Z21: 5.2
    # LAN_X_TURNOUT_INFO Z21: 5.3
    # LAN_X_SET_EXT_ACCESSORY Z21: 5.4
    # LAN_X_GET_EXT_ACCESSORY_INFO Z21: 5.5
    # LAN_X_EXT_ACCESSORY_INFO Z21 5.6

    # Z21: 6 Reading and writing Decoder CVs
    LAN_X_CV_READ =                 CMD(0x09, 0, 0x40, 0, 0x23, 0x11) # Add address MSB, address LSB, XOR-Byte, Z21: 6.1
    LAN_X_CV_WRITE =                CMD(0x0A, 0, 0x40, 0, 0x24, 0x12) # Add address MSB, address LSB, value, XOR-Byte, Z21: 6.1
    LAN_X_CV_NACK_SC =              CMD(0x07, 0, 0x40, 0, 0x61, 0x21, None) # XOR: 0x73, Z21: 6.3
    LAN_X_CV_NACK =                 CMD(0x07, 0, 0x40, 0, 0x61, 0x13, None) # XOR: 0x72, Z21: 6.4
    LAN_X_CV_RESULT =               CMD(0x0A, 0, 0x40, 0, 0x64, 0x14) # Add address MSB, address LSB, value, XOR-Byte, Z21: 6.5
    # LAN_X_CV_POM_WRITE_BYTE Z21: 6.6
    # LAN_X_CV_POM_WRITE_BIT Z21: 6.7
    # LAN_X_CV_POM_READ_BYTE Z21: 6.8
    # LAN_X_CV_POM_ACCESSORY_WRITE_BYTE Z21: 6.9
    # LAN_X_CV_POM_ACCESSORY_WRITE_BIT Z21: 6.10
    # LAN_X_CV_POM_ACCESSORY_READ_BYTE Z21: 6.11
    # LAN_X_MM_WRITE_BYTE Z21: 6.12
    # LAN_X_DCC_READ_REGISTER Z21: 6.13
    # LAN_X_DCC_WRITE_REGISTER Z21: 6.14

    # Z21: 7 Feedback - R-BUS
    # LAN_RMBUS_DATACHANGED Z21: 7.1
    # LAN_RMBUS_GETDATA Z21: 7.2
    # LAN_RMBUS_PROGRAMMODULE Z21: 7.3

    # Z21: 8 RailCom
    # LAN_RAILCOM_DATACHANGED Z21: 8.1
    # LAN_RAILCOM_GETDATA Z21: 8.2

    # Z21: 9 LocoNet
    # LAN_LOCONET_Z21_RX Z21: 9.1
    # LAN_LOCONET_Z21_TX Z12: 9.2
    # LAN_LOCONET_FROM_LAN Z12: 9.3
    # LAN_LOCONET_DISPATCH_ADDR Z21: 9.4
    # LAN_LOCONET_DETECTOR Z21: 9.5

    # Z21: 10 CAN
    # LAN_CAN_DETECTOR Z21: 10.1
    # LAN_CAN_DEVICE_GET_DESCRIPTION Z21: 10.2.1
    # LAN_CAN_DEVICE_SET_DESCRIPTION Z21: 10.2.2
    # LAN_CAN_BOOSTER_SYSTEMSTATE_CHGD Z21: 10.2.3
    # LAN_CAN_BOOSTER_SET_TRACKPOWER Z21: 10.2.4

    # Z21: zLink
    # LAN_ZLINK_GET_HWINFO Z21: 11.1.1.1
    # LAN_BOOSTER_GET_DESCRIPTION Z21: 11.2.1
    # LAN_BOOSTER_SET_DESCRIPTION Z21: 11.2.2
    # LAN_BOOSTER_SYSTEMSTATE_GETDATA Z21: 11.2.3
    # LAN_BOOSTER_SYSTEMSTATE_DATACHANGED Z21: 11.2.4
    # LAN_BOOSTER_SET_POWER Z21: 11.2.5    
    # LAN_DECODER_GET_DESCRIPTION Z21: 11.3.1
    # LAN_DECODER_SET_DESCRIPTION Z21: 11.3.2
    # LAN_DECODER_SYSTEMSTATE_GETDATA Z21: 11.3.3
    # LAN_DECODER_SYSTEMSTATE_DATACHANGED Z21: 11.3.4

    # Z21: Fast Clock
    # LAN_FAST_CLOCK_CONTROL Z21: 12.1
    # LAN_GET_FAST_CLOCK_TIME Z21: 12.1.1
    # LAN_SET_FAST_CLOCK_TIME Z21: 12.1.2
    # LAN_START_FAST_CLOCK_TIME Z21: 12.1.3
    # LAN_STOP_FAST_CLOCK_TIME Z21: 12.1.4
    # LAN_FAST_CLOCK_DATA Z21: 12.2
    # LAN_FAST_CLOCK_SETTINGS_GET Z21: 12.3
    # LAN_FAST_CLOCK_SETTINGS_SET Z21: 12.4

    def __init__(self, host, port=PORT, verbose=False):
        """Constructor of Z21 object, holding the open LAN socket to the DR5000 and offering a more abstract interface
        to the Z21 commands (or a logical sequence of commands.)"""
        self.host = host
        self.port = port # Port for Z21, default on 
        self.s = socket(AF_INET, SOCK_DGRAM) # Keep the socket opeb, e.g. to the DR5000 device via LAN
        self.s.connect((self.host, self.port))
        self.verbose = verbose # Optionally show what it is doing.

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.host}, {self.port})>'

    def _get_version(self):
        """See Z21 LAN Protocol Specification: 2.3"""
        self.send(self.LAN_GET_VERSION)
        return self.receiveInt()
    version = property(_get_version)

    def _get_serialNumber(self):
        """See Z21 LAN Protocol Specification: 2.11"""
        self.send(self.LAN_GET_SERIAL_NUMBER)
        return self.receiveInt()
    serialNumber = property(_get_serialNumber)

    def _get_status(self):
        """See Z21 LAN Protocol Specification: 2.11"""
        csEmergencyStop = 0x01 # The emergency stop is switched on
        csTrackVoltageOff = 0x02 # The track voltage is switched off
        csShortCircuit = 0x04 # Short-circuit
        csProgrammingModeActive = 0x20 # The programming mode is active        
        self.send(self.LAN_X_GET_STATUS)
        status = self.receiveInt()
        return dict(
            csEmergencyStop=bool(status & csEmergencyStop),
            csTrackVoltageOff=bool(status & csTrackVoltageOff),
            csShortCircuit=bool(status & csShortCircuit),
            csProgrammingModeActive=bool(status & csProgrammingModeActive),
            )
    status = property(_get_status)

    def send(self, cmd):
        """Send the command to the LAN device."""
        self.s.send(cmd)

    def receiveInt(self):
        # receive and process response
        incomingPacket = self.s.recv(1024) # Read packet from the Z21 device.
        return int.from_bytes(incomingPacket[4:], BYTEORDER) # Skip the package header

    def close(self):
        """Close the socket LAN connection to the Z21 device."""
        self.s.close()

    def wait(self, t):
        """Wait for @t number of seconds"""
        time.sleep(t)

    def stop(self, loco):
        """Perform a natural stop, by setting the speed to 0"""
        self.locoDrive(loco, 0)

    def eStop(self, loco):
        """Perform an emergency stop, by setting the speed to 1"""
        self.locoDrive(loco, 1)

    def setTrackPowerOff(self):
        """Set track power off"""
        cmd = self.LAN_X_SET_TRACK_POWER_OFF
        if self.verbose:
            printCmd('setTrackPowerOff cmd: ', cmd)
        self.send(cmd)

    def setTrackPowerOn(self):
        """Set track power on"""
        cmd = self.LAN_X_SET_TRACK_POWER_ON
        if self.verbose:
            printCmd('setTrackPowerOn cmd: ', cmd)
        self.send(cmd)

    def locoDrive(self, loco, speed, forward=True, steps=128):
        """Set the loco speed. @loco is the integer loco address. Speed depends on the defined number of steps. 
        Speed can be negative, which then reverses the driving direction (in the same way that the @forward 
        boolean flag works). @steps choice is in (14, 28, 128), where 128 is default.
        If the head light is set on when moving, it is not turn off for speed == 0
        """
        speedSteps = {14: 0x10, 28: 0x12, 128: 0x13}
        assert steps in speedSteps
        if steps == 128:
            if speed < 0:
                speed = -speed
                forward = not forward
            speed = max(0, min(speed, 126))
            if speed > 1: # Shift for extra E-stop on 0x01
                speed += 1
            bSpeed = speed 
            if forward:
                bSpeed |= 0x80
        elif steps == 14:
            return # For now
        elif steps == 28:
            return # For now
        else:
            speed = 0

        self.setHeadLight(loco, bool(speed not in (0, 1))) # If moving, independent from direction

        cmd = self.LAN_X_SET_LOCO_DRIVE + speedSteps[steps].to_bytes(1, BYTEORDER) + ADDRESS(loco) + bSpeed.to_bytes(1, BYTEORDER)
        cmd += XOR(cmd)
        if self.verbose:
            printCmd(f'locoDrive(loco={loco}, speed={speed} forward={forward}) cmd: ', cmd)
        self.send(cmd) 

    def setHeadLight(self, loco, value=ON):
        """Turn head light on/off, assuming default function=0"""
        self.locoFunction(loco, 0, value) # Standard headlight function, depending on driving direction
        if self.verbose:
            print(f'setHeadLight(loco={loco}, value={value})')

    def setLight(self, loco, value=ON):
        """Turn main light on/off, assuming default function=1"""
        self.locoFunction(loco, 1, value) # Standard headlight function, depending on driving direction
        if self.verbose:
            print(f'setLight(loco={loco}, value={value})')

    def locoFunction(self, loco, function, value):
        """Set the loco function value. @loco is the integer loco address and @function is the id, if supported by the loco-decoder.

        @value in (0, False, 'off') --> off, 
        @value in (1, True, 'on') --> on
        @value in (-1, 'toggle') --> toggle
        """
        if value in (0, False, OFF):
            functionCode = 0x00 # TT = 00 --> off
        elif value in (1, True, ON):
            functionCode = 0x40 # TT = 01 --> on
        elif value in (-1, TOGGLE):
            functionCode = 0x80 # TT = 10 --> toggle
        else:
            raise ValueError(f'locoFunction: Wrong value {value}')
        functionCode |= function
        cmd = self.LAN_X_SET_LOCO_FUNCTION + ADDRESS(loco) + functionCode.to_bytes(1, BYTEORDER)
        cmd += XOR(cmd)
        if self.verbose:
            printCmd(f'locoFunction(loco={loco}, function={function}, value={value}) cmd: ', cmd)
        self.send(cmd)

class LokSound5(Z21):
    """Subclassing for specifically LocSound5 decoder functionality."""
    def locoFunction(self, loco, function, value):
        """Set the loco function value. @loco is the integer loco address. 
        @value in (0, False, 'off') --> off, 
        @value in (1, True, 'on') --> on
        @value in (-1, 'toggle') --> toggle
        """
        if value in (0, False, OFF):
            functionCode = 0x00 # TT = 00 --> off
        elif value in (1, True, ON):
            functionCode = 0x40 # TT = 01 --> on
        elif value in (-1, TOGGLE):
            functionCode = 0x80 # TT = 10 --> toggle
        else:
            raise ValueError(f'locoFunction: Wrong value {value}')
        functionCode |= function
        cmd = self.LAN_X_SET_LOCO_FUNCTION + ADDRESS(loco) + functionCode.to_bytes(1, BYTEORDER)
        cmd += XOR(cmd)
        if self.verbose:
            printCmd(f'locoFunction(loco={loco}, function={function}, value={value}) cmd: ', cmd)
        self.send(cmd)

if __name__ == "__main__":
    def test():

        HOST = '192.168.178.242' # URL on LAN of the Z21/DR5000
        z21 = Z21(HOST, verbose=True)
        loco = 3
        print('Start Z21', z21)
        print('Version', z21.version)
        print('Serial number', z21.serialNumber)
        print('Status',  z21.status)
        z21.setTrackPowerOn()
        z21.locoFunction(loco, 2, True) # Horn
        z21.wait(2)
        z21.locoFunction(loco, 2, False) # Horn
        z21.locoFunction(loco, 3, True) # Horn
        z21.wait(2)
        z21.locoFunction(loco, 3, False) # Horn
        z21.locoFunction(loco, 4, True) # Horn
        z21.wait(2)
        z21.locoFunction(loco, 4, False) # Horn
        z21.locoFunction(loco, 12, True) # Horn
        z21.wait(2)
        z21.locoFunction(loco, 12, False) # Horn
        
        return

        z21.wait(3)
        #z21.locoFunction(loco, 0, True) # Turn on front/back headlight, depending on driving direction
        z21.locoDrive(loco, 70)
        z21.wait(6)
        z21.stop(loco)
        z21.setHeadLight(loco, OFF) # Same as z21.locoFunction(loco, 0, OFF)
        z21.setLight(loco, ON) # Same as z21.locoFunction(loco, 2, ON)
        z21.locoFunction(loco, 2, True)
        z21.wait(3)
        z21.locoFunction(loco, 2,False)

        z21.wait(8)
        z21.locoDrive(loco, -50) # Drive backwards
        z21.wait(8)
        z21.locoDrive(loco, 3) # Drive very slow
        z21.wait(8)
        z21.locoDrive(loco, 110, forward=True)
        z21.wait(6)
        z21.stop(loco) # Slow natural stop

        z21.locoFunction(loco, 2, True)
        z21.wait(0.5)
        z21.locoFunction(loco, 2,False)
        z21.wait(0.25)
        z21.locoFunction(loco, 2, True)
        z21.wait(0.5)
        z21.locoFunction(loco, 2,False)
        z21.wait(0.25)
        z21.locoFunction(loco, 2, True)
        z21.wait(0.5)
        z21.locoFunction(loco, 2,False)

        z21.wait(6)
        z21.locoDrive(loco, -80)

        #z21.locoFunction(loco, 1, False)
        #z21.locoFunction(loco, 2, False)
        #z21.locoFunction(loco, 3, False)
        z21.wait(6)
        z21.eStop(loco) # Emergency stop
        z21.locoFunction(loco, 0, False) # Turn off front/back headlight, depending on driving direction
        print('Status', z21.status)
        z21.wait(6)
        z21.setTrackPowerOff()
        z21.close()

    test()