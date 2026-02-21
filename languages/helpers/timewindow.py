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
        self.currenttime += speed * 1
        return self.currenttime

    def timeJump(self, jump=0.1): #relative to window size, so 0.1 is 10% of window size.
        if (jump < -10):
            jump = -10
        if (jump > 10):
            jump = 10
        newtime = self.currenttime + jump*self.window
        logger.info(f"Time Jump: {jump} Window: {self.window} New Time: {newtime}")
        self.setTime(newtime)
        return newtime

    def timeZoom(self, zoom=1.0):
        self.window *= zoom
        self.starttime = self.currenttime - self.window/2
        self.endtime = self.currenttime + self.window/2
        return self.window
