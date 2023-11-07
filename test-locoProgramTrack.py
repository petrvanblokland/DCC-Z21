# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
#     Copyright (c) 2023+ TYPETR
#     Usage by MIT License
# ..............................................................................
#
#    TYPETR z21.py
#
#   [z21.py] <----- (LAN) -----> [DR5000]  <----- (2-wire rails) -----> [LokSound5]
#
from z21 import Z21, OFF

VERBOSE = False
HOST = '192.168.178.242' # URL on LAN of the Z21/DR5000
c = Z21(HOST, verbose=VERBOSE) # New controller object with open LAN socket 

c.setTrackPowerOn()

# This assumes the loco to be positions on the programmers track
# Try to set the CV values to default, as described in the LokSound5 manual
# If the value already has its default value, then do nothing.

print(f'Loco {c.cvLocoAddress}')

if 0:
    startVoltage = 3
    if c.cvStartVoltage != startVoltage:
        print(f'Set start voltage {startVoltage} --> {c.cvStartVoltage}')
        c.cvStartVoltage = startVoltage

    acceleration = 28
    if c.cvAcceleration != acceleration:
        print(f'Set Acceleration {acceleration} --> {c.cvAcceleration}')
        c.cvAcceleration = acceleration

    deceleration = 21
    if c.cvDeceleration != deceleration:
        print(f'Set Deceleration {deceleration} --> {c.cvDeceleration}')
        c.cvDeceleration = deceleration

    maximumSpeed = 255
    if c.cvMaximumSpeed != maximumSpeed:
        print(f'Set Maximum speed {maximumSpeed} --> {c.cvMaximumSpeed}')
        c.cvMaximumSpeed = maximumSpeed

    mediumSpeed = 128
    if c.cvMediumSpeed != mediumSpeed:
        print(f'Set Medium speed {mediumSpeed} --> {c.cvMediumSpeed}')
        c.cvMediumSpeed = mediumSpeed

print(f'CV Version Number {c.cvVersionNumber}') # Read only

manufacturersId = 8 # Setting this value will reset decoder to manufacturer default values.
print(f'CV Manufacturers ID {c.cvManufacturersId}') # Read only. Use c.resetDecoder() function instead.
#c.resetDecoder()

masterVolume = 180
if c.cvMasterVolume != masterVolume:
    print(f'Set MasterVolum {masterVolume} --> {c.cvMasterVolume}')
    c.cvMasterVolume = masterVolume

#print(c.readCV(32))

#c.setTrackPowerOff()

c.close()



