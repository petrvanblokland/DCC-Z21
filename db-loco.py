# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
#     Copyright (c) 2023+ TYPETR
#     Usage by MIT License
# ..............................................................................
#
#    TYPETR z21.py
#
#   [Layout.z21] <----- (LAN) -----> [DR5000]  <----- (2-wire rails) -----> [LokSound5]
#
from vanilla import *
from libZ21 import Layout, OFF, ON

HOST = '192.168.178.242' # URL on LAN of the Z21/DR5000
W, H = 300, 400
M = 16
CW = 48
L = 24

class Assistant:
    
    def __init__(self):
        self.loco = 3
        self.layout = Layout(HOST)
        z21 = self.layout.z21 # Get Z21 Socket controller
        for f in (z21.F0, z21.F1, z21.F2, z21.F3, z21.F4, z21.F5, z21.F6, z21.F7, z21.F8,
                  z21.F9, z21.F10, z21.F11, z21.F12):
            z21.locoFunction(self.loco, f, OFF)
    
        self.w = Window((50, 50, W, H), 'Layout Controller')
        y = L/2
        self.w.trackPower = CheckBox((M, y, W/2, L), 'Track Power', value=True, callback=self.trackPowerCallback)
        z21.setTrackPowerOn()
        y += 1.5*L
        self.w.volumeSlider = Slider((M, y, -2*M-CW, L), minValue=0, maxValue=192, value=0, continuous=True, 
            tickMarkCount=10, callback=self.volumeUpdateCallback)
        self.w.volumeText = EditText((-M-CW, y, CW, L), callback=self.volumeTextCallback)   
        self.w.volumeText.set('30')    
            
        y += 1.5*L
        self.w.speedSlider = Slider((M, y, -2*M-CW, L), minValue=0, maxValue=120, value=0, continuous=True, 
            tickMarkCount=10, callback=self.speedUpdateCallback)
        self.w.speedText = EditText((-M-CW, y, CW, L), callback=self.speedTextCallback)   
        self.w.speedText.set('0')        
        y += L
        self.w.driveForward = CheckBox((W/2, y, W/2, L), 'Drive Forward', value=True, callback=self.speedUpdateCallback)
        self.w.function01 = CheckBox((M, y, W/2, L), 'Function 01', value=False, callback=self.function01Callback)
        y += L
        self.w.turnout = CheckBox((W/2, y, W/2, L), 'Lift test track', value=False, callback=self.turnoutCallback)
        self.w.function02 = CheckBox((M, y, W/2, L), 'Function 02', value=False, callback=self.function02Callback)
        y += L
        self.w.function03 = CheckBox((M, y, W/2, L), 'Function 03', value=False, callback=self.function03Callback)
        y += L
        self.w.function04 = CheckBox((M, y, W/2, L), 'Function 04', value=False, callback=self.function04Callback)
        y += L
        self.w.function05 = CheckBox((M, y, W/2, L), 'Function 05', value=False, callback=self.function05Callback)
        y += L
        self.w.function06 = CheckBox((M, y, W/2, L), 'Function 06', value=False, callback=self.function06Callback)
        y += L
        self.w.function07 = CheckBox((M, y, W/2, L), 'Function 07', value=False, callback=self.function07Callback)
        y += L
        self.w.function08 = CheckBox((M, y, W/2, L), 'Function 08', value=False, callback=self.function08Callback)
        y += L
        self.w.function09 = CheckBox((M, y, W/2, L), 'Function 09', value=False, callback=self.function09Callback)
        y += L
        self.w.function10 = CheckBox((M, y, W/2, L), 'Function 10', value=False, callback=self.function10Callback)
        y += L
        self.w.function11 = CheckBox((M, y, W/2, L), 'Function 11', value=False, callback=self.function11Callback)
        y += L
        self.w.function12 = CheckBox((M, y, W/2, L), 'Function 12', value=False, callback=self.function12Callback)
        self.w.resetDecoder = Button((W/2, y, W/2, 24), 'Reset decoder', callback=self.resetDecoderCallback)

        
        self.w.open()
    
    def trackPowerCallback(self, sender):
        if sender.get():
            self.layout.z21.setTrackPowerOn()
        else:
            self.layout.z21.setTrackPowerOff()
        
    def speedUpdateCallback(self, sender=None):
        slider = self.w.speedSlider
        speed = int(round(slider.get()))
        if not self.w.driveForward.get():
            speed = -speed
        self.w.speedText.set(str(speed))
        self.layout.z21.locoDrive(self.loco, speed)
        
    def speedTextCallback(self, sender=None):
        self.w.speedSlider.set(int(round(self.w.speedText.get())))
        self.speedUpdateCallback()

    def function01Callback(self, sender):
        self.layout.z21.locoFunction(self.loco, 1, sender.get())

    def function02Callback(self, sender):
        self.layout.z21.locoFunction(self.loco, 2, sender.get())

    def function03Callback(self, sender):
        self.layout.z21.locoFunction(self.loco, 3, sender.get())

    def function04Callback(self, sender):
        self.layout.z21.locoFunction(self.loco, 4, sender.get())

    def function05Callback(self, sender):
        self.layout.z21.locoFunction(self.loco, 5, sender.get())

    def function06Callback(self, sender):
        self.layout.z21.locoFunction(self.loco, 6, sender.get())

    def function07Callback(self, sender):
        self.layout.z21.locoFunction(self.loco, 7, sender.get())

    def function08Callback(self, sender):
        self.layout.z21.locoFunction(self.loco, 8, sender.get())

    def function09Callback(self, sender):
        self.layout.z21.locoFunction(self.loco, 9, sender.get())

    def function10Callback(self, sender):
        self.layout.z21.locoFunction(self.loco, 10, sender.get())

    def function11Callback(self, sender):
        self.layout.z21.locoFunction(self.loco, 11, sender.get())

    def function12Callback(self, sender):
        self.layout.z21.locoFunction(self.loco, 12, sender.get())
    
    def turnoutCallback(self, sender):
        turnoutId = 0 # Lifting loco on test track
        self.layout.z21.setTurnout(turnoutId, sender.get())

    def resetDecoderCallback(self, sender):
        self.layout.z21.resetDecoder()
        
        
    #    S O U N D 
    
    def volumeUpdateCallback(self, sender=None):
        slider = self.w.volumeSlider
        volume = int(round(slider.get()))
        self.w.volumeText.set(str(volume))
        self.layout.z21.cvMasterVolume = volume
        
    def volumeTextCallback(self, sender=None):
        self.w.volumeSlider.set(int(round(self.w.volumeText.get())))
        self.volumeUpdateCallback()

       
Assistant()