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
from libZ21 import Layout, OFF, ON

VERBOSE = False
host = '192.168.178.242' # URL on LAN of the Z21/DR5000
layout = Layout(host, verbose=VERBOSE)
z21 = layout.z21 # Get controller object with open LAN socket 

z21.setTrackPowerOn()

# This assumes the loco to be positions on the programmers track
# Try to set the CV values to default, as described in the LokSound5 manual
# If the value already has its default value, then do nothing.

print(f'Loco {z21.cvLocoAddress}')

if 0:
    startVoltage = 3
    if z21.cvStartVoltage != startVoltage:
        print(f'Set start voltage {startVoltage} --> {z21.cvStartVoltage}')
        z21.cvStartVoltage = startVoltage

    acceleration = 28
    if z21.cvAcceleration != acceleration:
        print(f'Set Acceleration {acceleration} --> {z21.cvAcceleration}')
        z21.cvAcceleration = acceleration

    deceleration = 21
    if z21.cvDeceleration != deceleration:
        print(f'Set Deceleration {deceleration} --> {z21.cvDeceleration}')
        z21.cvDeceleration = deceleration

    maximumSpeed = 255
    if z21.cvMaximumSpeed != maximumSpeed:
        print(f'Set Maximum speed {maximumSpeed} --> {z21.cvMaximumSpeed}')
        z21.cvMaximumSpeed = maximumSpeed

    mediumSpeed = 128
    if z21.cvMediumSpeed != mediumSpeed:
        print(f'Set Medium speed {mediumSpeed} --> {z21.cvMediumSpeed}')
        z21.cvMediumSpeed = mediumSpeed

    print(f'CV Version Number {z21.cvVersionNumber}') # Read only

    manufacturersId = 8 # Setting this value will reset decoder to manufacturer default values.
    print(f'CV Manufacturers ID {z21.cvManufacturersId}') # Read only. Use c.resetDecoder() function instead.
    z21.resetDecoder()

    print(f'CV Motor PWM Frequenz {z21.motorPWMFrequenz}')
    z21.motorPWMFrequenz = 40

    masterVolume = 60 # Low volume. Default is 180
    if z21.cvMasterVolume != masterVolume:
        print(f'CV Set MasterVolume {masterVolume} --> {z21.cvMasterVolume}')
        z21.cvMasterVolume = masterVolume

    print(f'CV Brake Sound Threshold On {z21.brakeSoundThresholdOn}')
    z21.brakeSoundThresholdOn = 60
    print(f'CV Brake Sound Threshold Off {z21.brakeSoundThresholdOff}')
    z21.brakeSoundThresholdOff = 5

#print(z21.readCV(32))

#z21.setTrackPowerOff()

z21.close()



