#!/usr/bin/python
import threading
import Queue
import time
import Adafruit_PCA9685
from config import mainconfig

q = Queue

Address = 0x40
Max = 0
Min = 0
Current = 0
Home = 0
Channel = 0


class ServoThread(threading.Thread):
    def __init__(self, Address, Max, Min, Home, Channel, q):
        if __debug__:
            print "Initialising thread"
        self.q = q
        self.Address = Address
        self.Max = Max
        self.Min = Min
        self.Home = Home
        self.current_position = Home
        self.Channel = Channel
        self.destination_position = Home
        self.destination_start = 0
        self.destination_time = 0
        self.processing = False
        threading.Thread.__init__(self)
        try: 
           self.i2c = Adafruit_PCA9685.PCA9685(address=Address)
           self.i2c.set_pwm_freq(60)
        except:
           print "Failed to initialise the i2c device"
        return

    def sendCommand(self):
        if self.processing:
            if __debug__:
                print "Processing and sending command"
            current_time = int(round(time.time() * 1000))
            if self.destination_time < current_time
                position = self.destination_position
            else:
                progress = (current_time - self.destination_start) / (self.destination_time - self.destination_start)
                if __debug__:
                    print "Currently %s way through this move" % progress
                position = self.destination_position * progress
            try:
                self.i2c.set_pwm(self.Channel, 0, position)
            except:
                print "Failed to send command"
            if self.destination_position == self.current_position:
                self.processing = False
            if self.destination_time + 500 < current_time
                if __debug__:
                    print "Servo reached destination, sending off command to device"
                try:
                    self.i2c.set_pwm(self.Channel, 4096, 0)
                except:
                    print "Failed to send command"
        return

    def run(self):
        if __debug__:
            print "Starting Thread"
        while True:
            self.sendCommand()
            try:
                command = self.q.get()
                position = command[0]
                duration = command[1]
                if position > 1 or position < 0:
                    print "Invalid position (%s)" % position
                else:
                    self.destination_position = int(((self.Max - self.Min) * position) + self.Min)
                if __debug__:
                    print "Duration: %s " % duration
                self.destination_start = int(round(time.time() * 1000))
                self.destination_time = self.destination_start + (duration * 1000)
            except Queue.Empty:
                self.sendCommand()

        return

