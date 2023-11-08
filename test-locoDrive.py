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
from z21 import Z21, OFF, ON

HOST = '192.168.178.242' # URL on LAN of the Z21/DR5000
c = Z21(HOST) # New controller object with open LAN socket 

loco = 3 # 2417 Brown
loco = 3 # LokSound5

# Just in case it is on, currently still disturbing the reading of other packages.
c.broadcastFlags = 0 

c.setTrackPowerOn()
print(c.systemState)

if 0:
    for n in range(20):
        c.locoFunction(loco, n, ON)
    c.wait(3)
    for n in range(20):
        c.locoFunction(loco, n, OFF)

c.locoFunction(loco, 1, ON) 
c.locoFunction(loco, 2, OFF) # Horn
c.locoFunction(loco, 8, ON)
c.locoFunction(loco, 12, ON)
c.locoFunction(loco, 26, ON)
c.locoFunction(loco, 31, ON)

c.cvMasterVolume = 180

if 0:
#print('LAN_GET_LOCOMODE:', c.getLocoMode(loco))
    c.setHeadRearLight(loco)
    c.wait(2)
    c.locoDrive(loco, 100) 
    c.wait(10)
    c.locoDrive(loco, 50) # Should trigger break sound
    c.wait(10)

    c.stop(loco)
    c.wait(1)
    c.setHeadRearLight(loco, OFF)


if 1:
    print('Driving loco', loco)
    c.locoDrive(loco, 80) # Drive backwards

    c.wait(1)


    c.locoFunction(loco, 1, ON)
    #c.locoFunction(loco, 2, ON) # Horn
    c.locoFunction(loco, 6, ON)
    c.locoFunction(loco, 8, ON)
    c.locoFunction(loco, 26, ON)
    c.locoFunction(loco, 12, ON)
    c.locoFunction(loco, 16, ON)
    c.locoFunction(loco, 28, ON)
    c.locoFunction(loco, 29, ON)
    print('Stopping loco', loco)
    for n in range(80, -2, -2):
        print(-n)
        c.wait(1)
        c.locoDrive(loco, -n) # Drive backwards
    #c.stop(loco)

#c.setTrackPowerOff()

c.locoFunction(loco, 2, OFF) # Horn
#c.stop(loco)

c.close()



