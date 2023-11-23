# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
#     Copyright (c) 2023+ TYPETR
#     Usage by MIT License
# ..............................................................................
#
#    TYPETR libZ21.py
#
#   [Layout.z21] <----- (LAN) -----> [DR5000]  <----- (2-wire rails) -----> [LokSound5]
#
from libZ21 import Layout

host = '192.168.178.242' # URL on LAN of the Z21/DR5000
layout = Layout(host, verbose=True)
z21 = layout.z21 # Get controller object with open LAN socket 

# Handle the broadcast flags.
# TODO: When flag 0x01 is on, there seems to be interference with "Normal" commands, expecting their packages.
# TODO: Split the flags into readable dictionary entries.
#c.broadcastFlags = 0
#f = c.broadcastFlags
#print(f)

z21.setTrackPowerOn()

z21.resetDecoder()

# Read the software feature scope of the Z21 (and z21 or z21start of course).
# This command is of particular interest for the hardware variant "z21 start", in order to be able to check whether 
# driving and switching via LAN is blocked or permitted.
#define Z21_NO_LOCK 0x00 // all features permitted
#define z21_START_LOCKED 0x01 // „z21 start”: driving and switching is blocked 
#define z21_START_UNLOCKED 0x02 // „z21 start”: driving and switching is permitted
print('LAN_GET_CODE', z21.lanGetCode)

print('... LAN_GET_HWINFO Hardware type: 0x%04x Firmware type: 0x%04x' % z21.hwInfo)
print(f'... Status: {z21.status}')
print(f'... Firmware version: {z21.firmwareVersion}')

print(f'... Current loco address: {z21.cvLocoAddress}')

z21.cvAcceleration = 13
if z21.cvAcceleration != 13:
    print(f'### cvAcceleration: {z21.cvAcceleration} Expected: {13}')
z21.cvDeceleration = 17
if z21.cvDeceleration != 17:
    print(f'### cvDeceleration: {z21.cvDeceleration} Expected: {17}')
if 0:
    loco = 4
    z21.cvLocoAddress = loco
    z21.wait(1)
    currentLoco = z21.cvLocoAddress
    if 1 or currentLoco != loco:
        print(f'### cvLocoAddress: {currentLoco} Expected: {loco}')
    z21.wait(2)
    loco = 3
    z21.cvLocoAddress = loco # Reset the loco address to original value.
    z21.wait(1)
    currentLoco = z21.cvLocoAddress
    if 1 or currentLoco != loco:
        print(f'### cvLocoAddress: {currentLoco} Expected: {loco}')


    print('LAN_X_CV_READ [CV1] Loco address', z21.cvLocoAddress) # Should now be loco address 4
    print('LAN_X_CV_READ [CV2] Start voltage', z21.cvStartVoltage)
    z21.cvStartVoltage = 9
    print('LAN_X_CV_READ [CV2] Start voltage', z21.cvStartVoltage)
    print('LAN_X_CV_READ [CV3] Acceleration', z21.cvAcceleration)
    z21.cvAcceleration = 13
    print('LAN_X_CV_READ [CV3] Acceleration', z21.cvAcceleration)
    print('LAN_X_CV_READ [CV4] Deceleration', z21.cvDeceleration)
    z21.cvDeceleration = 17
    print('LAN_X_CV_READ [CV4] Deceleration', z21.cvDeceleration)
    print('LAN_X_CV_READ [CV5] Maxiumum speed', z21.cvMaximumSpeed)
    z21.cvMaximumSpeed = 8
    print('LAN_X_CV_READ [CV5] Maxiumum speed', z21.cvMaximumSpeed) # Should now be 8
    #print(c.getLocoInfo(3))
    #print(c.systemState)

    z21.setTrackPowerOn()
    print(z21.getLocoInfo(3))
    print('Loco address', z21.getLocoAddress())
    printCmd('Get broadcast ', z21.getBroadcastFlags())
    z21.setBroadcastFlags(1)
    print('Loco address', z21.readCV(1), z21.getLocoAddress())
    printCmd('Get broadcast ', z21.getBroadcastFlags())
    print(z21.systemState)
    z21.setTrackPowerOff()
    print(z21.systemState)
    z21.close()
    
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
    z21.setHeadRearLight(loco, OFF) # Same as c.locoFunction(loco, 0, OFF)
    z21.setLighting(loco, ON) # Same as c.locoFunction(loco, 2, ON)
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

z21.setTrackPowerOff()
z21.close()



