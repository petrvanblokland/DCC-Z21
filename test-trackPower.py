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
c = Z21(HOST, verbose=True) # New controller object with open LAN socket 

c.setTrackPowerOn()
c.wait(6)
c.setTrackPowerOff()

c.close()


