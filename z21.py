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

# LITTLE_ORDER is positional to be compatible with micropython
# https://docs.micropython.org/en/latest/library/builtins.html#int.from_bytes
LITTLE_ORDER = "little"
BIG_ORDER = 'big'

PORT = 21105 # Default port number for Z21
ON = 'on'
OFF = 'off'
TOGGLE = 'toggle'

#   S O M E  H E L P E R  M E T H O D S

def printCmd(sender, cmd):
    s = sender
    for b in cmd:
        s += '%02X ' % b
    print(s)

def loco2Bytes(loco):
    """Convert a loco address integer into a 2-byte array"""
    return loco.to_bytes(2, BIG_ORDER)

def bytes2Loco(bb):
    """Convert the 2-byte array to a loco address integer."""
    return int.from_bytes(bb, BIG_ORDER)

def XOR(b):
    """Answer the XOR-parity byte from the byte-array that is necessary for most Z21 commands."""
    xor = None
    for byte in bytes(b):
        if xor is None:
            xor = byte
        else:
            xor = xor ^ byte
    return xor.to_bytes(1, LITTLE_ORDER)

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
            byte = i.to_bytes(1, LITTLE_ORDER)
            b += byte
    if xor is not None:
        b += xor
    return b

#   B A S E  C L A S S  Z 2 1

class Z21:
    """The Z21 class implements all functionsto communicate with a Z21 supporting controller device,
    such as DR5000, through a LAN connection.

    [z21.py] <----- (LAN) -----> [DR5000]  <----- (2-wire rails) -----> [LokSound5]

    For now, we focus on the DR5000 and LokSound5 for practical reasons, but it's surely intended
    to extend the functions to other means of communication, other controllers and other decoders.
    """

    #   Z 2 1  C O M M A N D  T E M P L A T E S

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

    #   L A N  C O N T R O L L E R  C O M M U N I C A T I O N 

    def send(self, cmd):
        """Send the command to the LAN device."""
        self.s.send(cmd)

    def receiveInt(self):
        # receive and process response
        incomingPacket = self.s.recv(1024) # Read packet from the Z21 device.
        return int.from_bytes(incomingPacket[4:], LITTLE_ORDER) # Skip the package header

    def receiveBytes(self, cnt):
        return self.s.recv(cnt)
        
    def close(self):
        """Close the socket LAN connection to the Z21 device."""
        self.s.close()

    def wait(self, t):
        """Wait for @t number of seconds"""
        time.sleep(t)

    #   R E T R I E V I N G  D A T A

    # Retrieving data from the Z21 controller without additional parameters, is implemented here
    # as class-properties. This way z21.version is the short writing of calling z21._get_version()

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

    def _get_hwInfo(self):
        """Answer a tuple with the hardward/firmware type of the control center.
        HwType:
        #define D_HWT_Z21_OLD 0x00000200 // „black Z21” (hardware variant from 2012)
        #define D_HWT_Z21_NEW 0x00000201 // „black Z21”(hardware variant from 2013) (Also DR5000?)
        #define D_HWT_SMARTRAIL 0x00000202 // SmartRail (from 2012)
        #define D_HWT_z21_SMALL 0x00000203 // „white z21” starter set variant (from 2013)
        #define D_HWT_z21_START 0x00000204 // „z21 start” starter set variant (from 2016)
        #define D_HWT_SINGLE_BOOSTER 0x00000205 // 10806 „Z21 Single Booster” (zLink)
        #define D_HWT_DUAL_BOOSTER 0x00000206 // 10807 „Z21 Dual Booster” (zLink)
        #define D_HWT_Z21_XL 0x00000211 // 10870 „Z21 XL Series” (from 2020)
        #define D_HWT_XL_BOOSTER 0x00000212 // 10869 „Z21 XL Booster” (from 2021, zLink)
        #define D_HWT_Z21_SWITCH_DECODER 0x00000301 // 10836 „Z21 SwitchDecoder” (zLink)
        #define D_HWT_Z21_SIGNAL_DECODER 0x00000302 // 10836 „Z21 SignalDecoder” (zLink)

        The FW version is specified in BCD format.
        Example:
        0x0C 0x00 0x1A 0x00 0x00 0x02 0x00 0x00 0x20 0x01 0x00 0x00 means: „Hardware Type 0x200, Firmware Version 1.20“
        To read out the version of an older firmware, use the alternative command
        2.15 LAN_X_GET_FIRMWARE_VERSION. Apply following rules for older firmware versions:
        • V1.10 ... Z21 (hardware variant from 2012)
        • V1.11 ... Z21 (hardware variant from 2012)
        • V1.12 ... SmartRail (from 2012)
        """
        self.send(self.LAN_GET_HWINFO)
        bb = self.receiveBytes(12)
        hwInfo = int.from_bytes(bb[4:8], BIG_ORDER)
        fwInfo = int.from_bytes(bb[8:12], BIG_ORDER)
        return hwInfo, fwInfo
    hwInfo = property(_get_hwInfo)

    NO_LOCK = 0x00
    START_LOCKED = 0x01
    START_UNLOCKED = 0x02

    def _get_lanGetCode(self):
        """Read the software feature scope of the Z21 (and z21 or z21start of course).
        This command is of particular interest for the hardware variant "z21 start", in order to be able to check 
        whether driving and switching via LAN is blocked or permitted.
        #define Z21_NO_LOCK 0x00 // all features permitted
        #define z21_START_LOCKED 0x01 // „z21 start”: driving and switching is blocked 
        #define z21_START_UNLOCKED 0x02 // „z21 start”: driving and switching is permitted
        """
        self.send(self.LAN_GET_CODE)
        bb = self.receiveBytes(5)
        code = int.from_bytes(bb[4:], BIG_ORDER)
        if code in (self.NO_LOCK, self.START_LOCKED, self.START_UNLOCKED):
            return code
        return None # Unknown code
    lanGetCode = property(_get_lanGetCode)

    def _get_systemState(self):
        """Reports a change in the system status from the Z21 to the client.
        For usage convenience, this property method break the 16 byte data into a readable dictionary.
        This message is asynchronously reported to the client by the Z21 when the client
        • activated the corresponding broadcast, see 2.16 LAN_SET_BROADCASTFLAGS, Flag 0x00000100.
        • explicitly requested the system status, see 2.19 LAN_SYSTEMSTATE_GETDATA.

        #### VALUES MAY NOT BE RIGHT YET, CALIBRATE with other app
        """
        self.send(self.LAN_SYSTEMSTATE_GETDATA)
        bb = self.receiveBytes(20)
        
        centralState = int.from_bytes(bb[12:13], LITTLE_ORDER)
        centralStateEx = int.from_bytes(bb[13:14], LITTLE_ORDER)
        
        # SystemState.Capabilities provides an overview of the device's range of features.
        #If SystemState.Capabilities == 0, then it can be assumed that the device has an older firmware version. 
        # SystemState.Capabilities should not be evaluated when using older firmware versions!
        capabilities = int.from_bytes(bb[15:], LITTLE_ORDER)
        assert capabilities != 0  

        state = dict(
            mainCurrent=int.from_bytes(bb[:2], LITTLE_ORDER), # mA, Current on the main track
            progCurrent=int.from_bytes(bb[2:4], LITTLE_ORDER), # mA, Current on programming track
            filteredMainCurrent=int.from_bytes(bb[4:6], LITTLE_ORDER), # mA, smoothed current on the main track
            temperature=int.from_bytes(bb[6:8], LITTLE_ORDER), # °C, command station internal temperature
            supplyVoltage=int.from_bytes(bb[8:10], LITTLE_ORDER), # mV, supply voltage
            vccVoltage=int.from_bytes(bb[10:12], LITTLE_ORDER), # mV, internal voltage, identical to track voltage
            # Bitmask for CentralState
            csEmergencyStop=bool(centralState & 0x01), # The emergency stop is switched on
            csTrackVoltageOff=bool(centralState & 0x02), # The track voltage is switched off
            csShortCircuit=bool(centralState & 0x04), # Short-circuit
            csProgrammingModeActive=bool(centralState & 0x20), # The programming mode is active
            # Bitmask for CentralStateEx
            cseHighTemperature=bool(centralStateEx & 0x01), # Temperature too high
            csePowerLost=bool(centralStateEx & 0x02), # Input voltage too low
            cseShortCircuitExternal=bool(centralStateEx & 0x04), # S.C. at the external booster output
            cseShortCircuitInternal=bool(centralStateEx & 0x08), # S.C. at the main track or programming track
            cseRCN213=bool(centralStateEx & 0x20), # Turnout addresses according to RCN-213
            # Bitmask for Capabilities
            capDCC=bool(capabilities & 0x01), # Capable of DCC
            capMM=bool(capabilities & 0x02), # Capable of MM
            #capReserved 0x04 reserved for future development
            capRailCom=bool(capabilities & 0x04), # Railcom is active
            capLocoCmds=bool(capabilities & 0x08), # Accepts LAN commands for locomotive decoders
            capAccessoryCmds=bool(capabilities & 0x02), # Accepts LAN commands for assessory decoders
            capDetectorCmds=bool(capabilities & 0x02), # Accepts LAN commands for detectors
            capNeedsUnlockCode=bool(capabilities & 0x02), # Device needs activate code (z21start)
        )
        return state
    systemState = property(_get_systemState)

    #   R E T R I E V E  L O C O  D A T A

    LOCOMODE_DCC = 0
    LOCOMODE_MM = 1

    def getLocoMode(self, loco):
        """Read the output format for a given locomotive address.
        In the Z21, the output format (DCC, MM) is persistently stored for each locomotive 
        address. A maximum of 256 different locomotive addresses can be stored. Each address >= 256 
        is DCC automatically.

        Loco Address Mode
        0 ... DCC Format 
        1 ... MM Format
        """
        cmd = self.LAN_GET_LOCOMODE + loco2Bytes(loco)
        cmd += XOR(cmd)
        self.send(cmd)
        bb = self.receiveBytes(7)
        rLoco = int.from_bytes(bb[4:6], BIG_ORDER)
        assert rLoco == loco # Should always be identical.
        mode = int.from_bytes(bb[-1:], BIG_ORDER)
        assert mode in (self.LOCOMODE_DCC, self.LOCOMODE_MM)
        return mode

    def setLocoMode(self, loco, mode):
        """Set the output format for a given locomotive address. The format is stored in the Z21persistently.
        Note: each locomotive address >= 256 is and remains "Format DCC" automatically.
        Note: the speed steps (14, 28, 128) are also stored in the command station persistently. 
        This automatically happens with the loco driving command, see 4.2 LAN_X_SET_LOCO_DRIVE
        """
        assert mode in (self.LOCOMODE_DCC, self.LOCOMODE_MM)
        cmd = self.LAN_SET_LOCOMODE + loco2Bytes(loco) + mode.to_bytes(1, LITTLE_ORDER)
        cmd += XOR(cmd)
        self.send(cmd)

    def getLocoInfo(self, loco):
        """The following command can be used to poll the status of a locomotive. At the same time, 
        the client also "subscribes" to the locomotive information for this locomotive address (only 
        in combination with LAN_SET_BROADCASTFLAGS, Flag 0x00000001).
        This method answers a dictionary with all binary flags placed by the key/value.

        Note: loco address = (Adr_MSB & 0x3F) << 8 + Adr_LSB
        For locomotive addresses ≥ 128, the two highest bits in DB1 must be set to 1:
        DB1 = (0xC0 | Adr_MSB). For locomotive addresses < 128, these two highest bits have no meaning.
        Reply from Z21: see 4.4 LAN_X_LOCO_INFO

        LAN_X_LOCO_INFO
        This message is sent from the Z21 to the clients in response to the command 4.1 LAN_X_GET_LOCO_INFO. 
        However, it is also unsolicitedly sent to an associated client if
            • the locomotive status has been changed by one of the (other) clients or handset controls
            • and the associated client has activated the corresponding broadcast,
                see 2.16 LAN_SET_BROADCASTFLAGS, Flag 0x00000001
            • and the associated client has subscribed to the locomotive address with 4.1 LAN_X_GET_LOCO_INFO.
        The actual packet length n may vary depending on the data actually sent, with 7 ≤ n ≤ 14.
        From Z21 FW version 1.42 DataLen is ≥ 15 (n ≥ 8) for also transferring the status of F29, F30 and F31! 
        """
        cmd = self.LAN_X_GET_LOCO_INFO + loco2Bytes(loco)
        cmd += XOR(cmd)
        self.send(cmd)
        # Result format: LAN_X_LOCO_INFO
        bb = self.receiveBytes(1024) # Length of return package is not fixed.
        if self.verbose:
            printCmd('getLocoInfo ', cmd)
            printCmd('getLocoInfo result ', bb)
        info = dict(
            loco=int.from_bytes(bb[5:7], BIG_ORDER) & 0x3f,
        )
        return info

    #   T R A C K  P O W E R 

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

    #   L O C O  D R I V E

    def stop(self, loco):
        """Perform a natural stop, by setting the speed to 0"""
        self.locoDrive(loco, 0)

    def eStop(self, loco):
        """Perform an emergency stop, by setting the speed to 1"""
        self.locoDrive(loco, 1)

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
        else: # steps == 28:
            return # For now

        self.setHeadLight(loco, bool(speed not in (0, 1))) # If moving, independent from direction

        cmd = self.LAN_X_SET_LOCO_DRIVE + speedSteps[steps].to_bytes(1, LITTLE_ORDER) + loco2Bytes(loco) + bSpeed.to_bytes(1, LITTLE_ORDER)
        cmd += XOR(cmd)
        if self.verbose:
            printCmd(f'locoDrive(loco={loco}, speed={speed} forward={forward}) cmd: ', cmd)
        self.send(cmd) 

    #   L O C O  F U N C T I O N S

    def locoFunction(self, loco, function, value):
        """Set the loco function value. @loco is the integer loco address and @function is the id, if supported by the loco-decoder.

        @value in (0, False, 'off') --> off, 
        @value in (1, True, 'on') --> on
        @value in (-1, 'toggle') --> toggle

        Note: loco address = (Adr_MSB & 0x3F) << 8 + Adr_LSB
        For locomotive addresses ≥ 128, the two highest bits in DB1 must be set to 1:
        DB1 = (0xC0 | Adr_MSB). For locomotive addresses < 128, these two highest bits have no meaning.
        TT switch type: 00=off, 01=on, 10=toggle,11=not allowed NNNNNN Function index, 0x00=F0 (light), 0x01=F1 etc.
        With Motorola MMI only F0 can be switched. With MMII, F0 to F4 can be used.
        With DCC, F0 to F28 can be switched here. From Z21 FW version 1.42 the extended range from F0 to F31 can be used here.
        Reply from Z21:
        No standard reply, 4.4 LAN_X_LOCO_INFO to subscribed clients.
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
        cmd = self.LAN_X_SET_LOCO_FUNCTION + loco2Bytes(loco) + functionCode.to_bytes(1, LITTLE_ORDER)
        cmd += XOR(cmd)
        if self.verbose:
            printCmd(f'locoFunction(loco={loco}, function={function}, value={value}) cmd: ', cmd)
        self.send(cmd)

    def setHeadLight(self, loco, value=ON):
        """Turn head light on/off, assuming default function=0"""
        self.locoFunction(loco, 0, value) # Standard headlight function, decoder switches on driving direction
        if self.verbose:
            print(f'setHeadLight(loco={loco}, value={value})')

    def setLight(self, loco, value=ON):
        """Turn main light on/off, assuming default function=1"""
        self.locoFunction(loco, 1, value) # Standard light function
        if self.verbose:
            print(f'setLight(loco={loco}, value={value})')

    #   R E A D  /  W R I T E  C O N F I G U R A T I O N  V A R I A B L E S  ( C V )

    CV_LOCO_ADDRESS = 1 # Address of engine (For Multiprotocol decoders: Range 1-255 for Motorola). Range: 1-127. Default: 3
    CV_START_VOLTAGE = 2 # Sets the minimum speed of the engine. Range: 1-127. Default: 3
    CV_ACCELERATION = 3 # This value multiplied by 0.25 is the time from stop to maximum speed. For LokSound 5 DCC: The unit is 0.896 seconds. Range: 0-255. Default: 28
    CV_DECELERATION = 4 # This value multiplied by 0.25 is the time from maximum speed to stopFor LokSound 5 DCC: The unit is 0.896 seconds. Range: 0-255. Default: 21
    CV_MAXIMUM_SPEED = 5 # Maximum speed of the engine. Range: 0-255. Default: 255

    def setBroadcastFlags(self, d):
        cmd = self.LAN_SET_BROADCASTFLAGS + 0x00000001.to_bytes(4, LITTLE_ORDER)
        printCmd('setBroadcastFlags: ', cmd)
        self.send(cmd)

    def getBroadcastFlags(self):
        """Answer the broadcast flags as dictionary with more readable Python values.
        The dictionary can be used by self.setBroadcastFlags(flags), which packs the values 
        into the 32bits flags parameter.
        """
        cmd = self.LAN_GET_BROADCASTFLAGS
        self.send(cmd)
        bb = self.receiveBytes(8)
        flagsInt = int.from_bytes(bb[4:], LITTLE_ORDER)

        printCmd('Broadcast flags: ', bb[4:])
        return bb

    def readCV(self, cvId):
        """Read the @cvId value, assuming that the loco is on a programmaing track. No loco id is required.
        Note that this method corrects the id-offset, so instead of:
        CV-Address = (CVAdr_MSB << 8) + CVAdr_LSB, where 0=CV1, 1=CV2, 255=CV256, etc.
        the @cvId is the true CV address: 1=CV1, 2=CV2, 256=CV256, etc.
        """
        cmd = self.LAN_X_CV_READ + loco2Bytes(cvId-1) # Corrected address offset by 1
        cmd += XOR(cmd)
        self.send(cmd)
        printCmd('readCV cmd ', cmd)
        bb = self.receiveBytes(9)
        return int.from_bytes(bb[8:9], LITTLE_ORDER)

    def writeCV(self, cvId, cvValue):
        """Write the @cvId @value, assuming that the loco is on a programming track. No loco id is required.
        Note that this method corrects the id-offset, so instead of:
        CV-Address = (CVAdr_MSB << 8) + CVAdr_LSB, where 0=CV1, 1=CV2, 255=CV256, etc.
        the @cvId is the true CV address: 1=CV1, 2=CV2, 256=CV256, etc.
        """
        cmd = self.LAN_X_CV_WRITE + loco2Bytes(cvId-1) + cvValue.to_bytes(1, LITTLE_ORDER) # Corrected address offset by 1
        cmd += XOR(cmd)
        self.send(cmd)

    def getLocoAddress(self):
        return self.readCV(self.CV_LOCO_ADDRESS)

class LokSound5(Z21):
    """Subclassing for specifically LocSound5 decoder functionality. This inheriting class will know about
    specific functions of the LokSound5 and offers an more abstract level of interface. Similarly, there also
    can be defined groups or sequences of functions under a single method name.

    Future change: the main Z21 class should detect which decoder is used in a certain loco, and switch behaviour
    accordingly. We may need to introduce another level of abstraction later."""


if __name__ == "__main__":
    def test1():

        HOST = '192.168.178.242' # URL on LAN of the Z21/DR5000
        z21 = Z21(HOST, verbose=True) # New connector object with open LAN socket 
        z21.setTrackPowerOn()
        print(z21.getLocoInfo(3))
        print('Hardware type: 0x%04x Firmware type: 0x%04x' %z21.hwInfo)
        print('Lan Code', z21.lanGetCode)
        print('Loco address', z21.getLocoAddress())
        printCmd('Get broadcast ', z21.getBroadcastFlags())
        z21.setBroadcastFlags(1)
        print('Loco address', z21.readCV(1), z21.getLocoAddress())
        printCmd('Get broadcast ', z21.getBroadcastFlags())
        print(z21.systemState)
        z21.setTrackPowerOff()
        print(z21.systemState)
        z21.close()
        
    def test2():

        HOST = '192.168.178.242' # URL on LAN of the Z21/DR5000
        z21 = Z21(HOST, verbose=True) # New connector object with open LAN socket 
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

    test1()


