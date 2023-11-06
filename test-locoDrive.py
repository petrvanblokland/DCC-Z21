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
from z21 import Z21

HOST = '192.168.178.242' # URL on LAN of the Z21/DR5000
c = Z21(HOST) # New controller object with open LAN socket 

c.setTrackPowerOn()
	
for loco in range(1, 10):
	print('Driving loco', loco)
	c.locoDrive(loco, 150) # Drive backwards

c.wait(10)

for loco in range(1, 10):
	print('Stropping loco', loco)
	c.locoDrive(loco, 150) # Drive backwards
	c.stop(loco)

c.setTrackPowerOff()

c.close()



