import threading,os,platform,time
from PyQt4 import QtCore
from datetime import datetime
import RPi.GPIO as GPIO


class Speed(QtCore.QThread):
    Measured = QtCore.pyqtSignal(float)

    def __init__(self):
        QtCore.QThread.__init__(self)

        self.scaleFcator = 1

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23, GPIO.IN)
        GPIO.setup(24, GPIO.IN)

        GPIO.add_event_detect(23, GPIO.FALLING, callback=self.Sen1Triggered)
        GPIO.add_event_detect(24, GPIO.FALLING, callback=self.Sen2Triggered)

        self.timeout = 0
        self.sen1Triggerd = False
        self.s1TriggerTime = datetime.now()

    def run(self):
        while True:
            time.sleep(0.5)
            if self.timeout > 0:
                self.timeout -= 1
                if self.timeout == 0:
                    self.sen1Triggerd = False

    def Sen1Triggered(self, prm):
        if not self.sen1Triggerd:
            self.timeout = 6
            self.sen1Triggerd = True
            self.s1TriggerTime = datetime.now()

    def Sen2Triggered(self, prm):
        if self.sen1Triggerd:
            self.sen1Triggerd = False
            self.timeout = 0
            dt = datetime.now() - self.s1TriggerTime
            speed = 0.0001/(dt.total_seconds()*0.000277778)
            speed = speed *self.scaleFcator
            self.Measured.emit(speed)
