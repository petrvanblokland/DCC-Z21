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
from z21 import Layout, OFF, ON

host = '192.168.178.242' # URL on LAN of the Z21/DR5000
layout = Layout(host)
c = layout.c # Get controller object with open LAN socket 

loco = 3 # 2417 Brown
loco = 3 # LokSound5

#c.resetDecoder()

# Just in case it is on, currently still disturbing the reading of other packages.
c.broadcastFlags = 0 

c.setTrackPowerOn()
#print(c.systemState)

if 0:
    for n in range(20):
        c.locoFunction(loco, n, ON)
    c.wait(3)
    for n in range(20):
        c.locoFunction(loco, n, OFF)

if 0:
	c.locoFunction(loco, 1, ON) 
	c.locoFunction(loco, 2, OFF) # Horn
	#c.locoFunction(loco, 8, ON)
	#c.locoFunction(loco, 12, ON)
	#c.locoFunction(loco, 26, ON)
	#c.locoFunction(loco, 31, ON)

if 0:
	v = OFF
	c.setHeadRearLight(loco, ON)
	#c.wait(1)
	#c.setHeadRearLight(loco, OFF)
	c.setLighting(loco, ON) # Also main motor sound on
	c.setHorn(loco, OFF)
	c.locoFunction(loco, c.F3, v)
	c.locoFunction(loco, c.F4, v)
	c.locoFunction(loco, c.F5, v)
	c.locoFunction(loco, c.F6, v)
	c.locoFunction(loco, c.F7, v)
	c.locoFunction(loco, c.F8, v)
	c.locoFunction(loco, c.F9, v)
	c.locoFunction(loco, c.F10, v)
	c.locoFunction(loco, c.F11, v)
	c.locoFunction(loco, c.F12, v)
	c.locoDrive(loco, 80)
	c.brakeSoundThresholdOn = 70
	c.brakeSoundThresholdOff = 7
	c.locoDrive(loco, -30)
	c.wait(4)
	c.stop(loco)

#c.locoFunction(loco, c.F7, ON)
#c.locoFunction(loco, c.F8, ON)

c.cvMasterVolume = 160

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


    c.locoFunction(loco, 1, OFF)
    #c.locoFunction(loco, 2, ON) # Horn
    c.locoFunction(loco, 8, ON)
    if 0:
        c.locoFunction(loco, 3, ON) 
        c.locoFunction(loco, 4, ON) 
        c.locoFunction(loco, 7, ON) 
        c.locoFunction(loco, 9, ON) 
        c.locoFunction(loco, 10, ON) 
        c.locoFunction(loco, 6, ON)
        c.locoFunction(loco, 26, ON)
        c.locoFunction(loco, 12, ON)
        c.locoFunction(loco, 16, ON)
        c.locoFunction(loco, 28, ON)
        c.locoFunction(loco, 29, ON)
    print('Stopping loco', loco)
    for n in range(80, -4, -4):
        print(-n)
        c.wait(1)
        c.locoDrive(loco, -n) # Drive backwards
    #c.stop(loco)

#c.setTrackPowerOff()

if 0:
	c.locoFunction(loco, 2, OFF) # Horn
	c.stop(loco)
	c.locoFunction(loco, 1, OFF)
	c.wait(1)
	c.locoFunction(loco, 1, ON)

c.stop(loco)
c.close()



