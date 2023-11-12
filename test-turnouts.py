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

HOST = '192.168.178.242' # URL on LAN of the Z21/DR5000
layout = Layout(HOST)
c = layout.c # Get controller object with open LAN socket 

#c.setTrackPowerOn()

testTrackAddress = 1   
print(testTrackAddress, c.getTurnoutInfo(testTrackAddress))
c.wait(2)
c.setTurnout(testTrackAddress, 0)
c.wait(2)
c.setTurnout(testTrackAddress, 1)
c.wait(2)

#c.setTrackPowerOff()

c.close()



