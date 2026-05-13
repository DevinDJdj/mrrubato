#transcribe commands into timeline.
from datetime import datetime, timedelta
import os
import logging
import time
import re

logger = logging.getLogger(__name__)

class timewindow:
    def __init__(self, lang_helper=None):
        self.lang_helper = lang_helper
        self.defstring = r"[~!@#$%^&*<>/:;\-\+=]"
        self.currenttime = time.time()
        self.starttime = time.time() - 86400 #default to 24 hours ago
        self.endtime = time.time()
        self.window = 86400 #default to 24 hours, in seconds.
        self.windowindex = 2 #1 day..
        # 1, 6, 4, 7, 4, 3, 4, 5, 6, 4
        #quantize time: 1 hour, 6 hours, 1 day, 1 week, 30 days, 3 months, 1 year, 5 years, 30 years, 120 years
        self.windows = [3600, 3600*6, 86400, 604800, 2592000, 7776000, 31536000, 157680000, 946080000, 3784320000] 

        #/60 interval: 1 min, 6 min, 24 min, ~3 hours, 12 hours, 36 hours, ~6 days, ~30 days, 6 months, 2 years

    
    def getTime(self, relativesecs=0):
        return self.currenttime + relativesecs

    def setTime(self, newtime):
        self.currenttime = newtime
        if (newtime < self.starttime+self.window*0.1): #if we jump too far back, just reset to the middle of the window.
            self.starttime = newtime - self.window/2
            self.endtime = newtime + self.window/2
        if (newtime > self.endtime-self.window*0.1): #if we jump too far forward, just reset to the middle of the window.
            self.starttime = newtime - self.window/2
            self.endtime = newtime + self.window/2
    
    def tick(self, speed=1.0):
#        self.currenttime += speed * 1
        return self.currenttime

    def timeJump(self, jump=1): #relative to window size, so 0.1 is 10% of window size.
        if (jump < -6):
            jump = -6
        if (jump > 6):
            jump = 6
        jumpindex = self.windowindex - 1
        if (jumpindex < 0):
            jumpindex = 0
        newtime = self.currenttime + jump*self.windows[jumpindex]
        logger.info(f"Time Jump: {jump} Window: {self.window} New Time: {newtime}")
        self.setTime(newtime)
        return newtime

    def timeZoom(self, zoom=1.0):
        #quantize zoom windows to predefined human friendly values.  zoom in or out by going to next window size.
        #not sure if 5 years or 25 years will actually work in most cases..
        if (zoom >= 1):
            self.windowindex += 1
        else:
            self.windowindex -= 1
        if (self.windowindex < 0):
            self.windowindex = 0
        if (self.windowindex >= len(self.windows)):
            self.windowindex = len(self.windows)-1
        self.window = self.windows[self.windowindex]
#        self.window *= zoom
        self.starttime = self.currenttime - self.window/2
        if (self.starttime < 0):
            self.starttime = 0 #can't have negative time. start at 1970..
        self.endtime = self.currenttime + self.window/2
        #should be no real max time 64 bit int 200 billion years..
        return self.window
