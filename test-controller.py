# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
#     Copyright (c) 2023+ TYPETR
#     Usage by MIT License
# ..............................................................................
#
#    TYPETR z21.py
#
#   [Layout.c] <----- (LAN) -----> [DR5000]  <----- (2-wire rails) -----> [LokSound5]
#
from z21 import Layout

host = '192.168.178.242' # URL on LAN of the Z21/DR5000
layout = Layout(host)
c = layout.c # Get controller object with open LAN socket 

# Handle the broadcast flags.
# TODO: When flag 0x01 is on, there seems to be interference with "Normal" commands, expecting their packages.
# TODO: Split the flags into readable dictionary entries.
#c.broadcastFlags = 0
#f = c.broadcastFlags
#print(f)

c.setTrackPowerOn()

# Read the software feature scope of the Z21 (and z21 or z21start of course).
# This command is of particular interest for the hardware variant "z21 start", in order to be able to check whether 
# driving and switching via LAN is blocked or permitted.
#define Z21_NO_LOCK 0x00 // all features permitted
#define z21_START_LOCKED 0x01 // „z21 start”: driving and switching is blocked 
#define z21_START_UNLOCKED 0x02 // „z21 start”: driving and switching is permitted
print('LAN_GET_CODE', c.lanGetCode)


print('LAN_GET_HWINFO Hardware type: 0x%04x Firmware type: 0x%04x' % c.hwInfo)
print('Status',  c.status)
print('Firmware version', c.firmwareVersion)

print('LAN_X_CV_READ [CV1] Loco address', c.locoAddress)
c.locoAddress = 5
print('LAN_X_CV_READ [CV1] Loco address', c.locoAddress) # Should now be loco address 4
print('LAN_X_CV_READ [CV2] Start voltage', c.startVoltage)
c.startVoltage = 9
print('LAN_X_CV_READ [CV2] Start voltage', c.startVoltage)
print('LAN_X_CV_READ [CV3] Acceleration', c.acceleration)
c.acceleration = 13
print('LAN_X_CV_READ [CV3] Acceleration', c.acceleration)
print('LAN_X_CV_READ [CV4] Deceleration', c.deceleration)
c.deceleration = 17
print('LAN_X_CV_READ [CV4] Deceleration', c.deceleration)
print('LAN_X_CV_READ [CV5] Maxiumum speed', c.maximumSpeed)
c.maximumSpeed = 8
print('LAN_X_CV_READ [CV5] Maxiumum speed', c.maximumSpeed) # Should now be 8
#print(c.getLocoInfo(3))
#print(c.systemState)

c.setTrackPowerOff()
c.close()

if 0:
    HOST = '192.168.178.242' # URL on LAN of the Z21/DR5000
    c = Z21(HOST, verbose=True) # New connector object with open LAN socket 
    c.setTrackPowerOn()
    print(c.getLocoInfo(3))
    print('Loco address', c.getLocoAddress())
    printCmd('Get broadcast ', c.getBroadcastFlags())
    c.setBroadcastFlags(1)
    print('Loco address', c.readCV(1), c.getLocoAddress())
    printCmd('Get broadcast ', c.getBroadcastFlags())
    print(c.systemState)
    c.setTrackPowerOff()
    print(c.systemState)
    c.close()
    

    HOST = '192.168.178.242' # URL on LAN of the Z21/DR5000
    z21 = Z21(HOST, verbose=True) # New connector object with open LAN socket 
    loco = 3
    print('Start Z21', c)
    print('Version', c.version)
    print('Serial number', c.serialNumber)
    print('Status',  c.status)
    c.setTrackPowerOn()
    c.locoFunction(loco, 2, True) # Horn
    c.wait(2)
    c.locoFunction(loco, 2, False) # Horn
    c.locoFunction(loco, 3, True) # Horn
    c.wait(2)
    c.locoFunction(loco, 3, False) # Horn
    c.locoFunction(loco, 4, True) # Horn
    c.wait(2)
    c.locoFunction(loco, 4, False) # Horn
    c.locoFunction(loco, 12, True) # Horn
    c.wait(2)
    c.locoFunction(loco, 12, False) # Horn
    
    c.wait(3)
    #z21.locoFunction(loco, 0, True) # Turn on front/back headlight, depending on driving direction
    c.locoDrive(loco, 70)
    c.wait(6)
    c.stop(loco)
    c.setHeadRearLight(loco, OFF) # Same as c.locoFunction(loco, 0, OFF)
    c.setLighting(loco, ON) # Same as c.locoFunction(loco, 2, ON)
    c.locoFunction(loco, 2, True)
    c.wait(3)
    c.locoFunction(loco, 2,False)

    c.wait(8)
    c.locoDrive(loco, -50) # Drive backwards
    c.wait(8)
    c.locoDrive(loco, 3) # Drive very slow
    c.wait(8)
    c.locoDrive(loco, 110, forward=True)
    c.wait(6)
    c.stop(loco) # Slow natural stop

    c.locoFunction(loco, 2, True)
    c.wait(0.5)
    c.locoFunction(loco, 2,False)
    c.wait(0.25)
    c.locoFunction(loco, 2, True)
    c.wait(0.5)
    c.locoFunction(loco, 2,False)
    c.wait(0.25)
    c.locoFunction(loco, 2, True)
    c.wait(0.5)
    c.locoFunction(loco, 2,False)

    c.wait(6)
    c.locoDrive(loco, -80)

    #c.locoFunction(loco, 1, False)
    #c.locoFunction(loco, 2, False)
    #c.locoFunction(loco, 3, False)
    c.wait(6)
    c.eStop(loco) # Emergency stop
    c.locoFunction(loco, 0, False) # Turn off front/back headlight, depending on driving direction
    print('Status', c.status)
    c.wait(6)
    c.setTrackPowerOff()
    c.close()



