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

HOST = '192.168.178.242' # URL on LAN of the Z21/DR5000
c = Z21(HOST) # New controller object with open LAN socket 

loco = 3 # 2400 Brown
loco = 5 # LokSound5

# Just in case it is on, currently still disturbing the reading of other packages.
c.broadcastFlags = 0 

c.setTrackPowerOn()
print(c.systemState)
#print('LAN_GET_LOCOMODE:', c.getLocoMode(loco))
c.setHeadLight(loco)
c.wait(2)
c.locoDrive(loco, 180) # Drive backwards
c.wait(10)
c.stop(loco)
c.wait(1)
c.setHeadLight(loco, OFF)


if 0:	
	for loco in range(1, 10):
		print('Driving loco', loco)
		c.locoDrive(loco, 150) # Drive backwards

	c.wait(10)

	for loco in range(1, 10):
		print('Stropping loco', loco)
		c.locoDrive(loco, 150) # Drive backwards
		c.stop(loco)

#c.setTrackPowerOff()

c.close()



