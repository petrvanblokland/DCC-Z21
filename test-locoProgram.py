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

print(f'Loco {c.locoAddress}')

startVoltage = 3
if c.startVoltage != startVoltage:
    print(f'Set start voltage {startVoltage} --> {c.startVoltage}')
    c.startVoltage = startVoltage

acceleration = 28
if c.acceleration != acceleration:
    print(f'Set Acceleration {acceleration} --> {c.acceleration}')
    c.acceleration = acceleration

deceleration = 21
if c.deceleration != deceleration:
    print(f'Set Deceleration {deceleration} --> {c.deceleration}')
    c.deceleration = deceleration

maximumSpeed = 255
if c.maximumSpeed != maximumSpeed:
    print(f'Set Deceleration {maximumSpeed} --> {c.maximumSpeed}')
    c.maximumSpeed = maximumSpeed

masterVolume = 180
if c.masterVolume != masterVolume:
    print(f'Set MasterVolum {masterVolume} --> {c.masterVolume}')
    c.masterVolume = masterVolume

#print(c.readCV(32))

#c.setTrackPowerOff()

c.close()



