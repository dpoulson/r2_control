#!/usr/bin/python
from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
import threading
from queue import Queue, Empty
import time
import Adafruit_PCA9685
standard_library.install_aliases()


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
            print("Initialising thread")
        self.q = q
        self.Address = Address
        self.Max = Max
        self.Min = Min
        self.Home = Home
        self.current_position = Home
        self.original_position = Home
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
            if __debug__:
                print("Failed to initialise the i2c device %s/%s" % (self.Address, self.Channel))
        return

    def sendCommand(self):
        current_time = int(round(time.time() * 1000))
        if self.processing:
            if __debug__:
                print("Processing and sending command")
            if self.destination_time <= current_time:
                position = self.destination_position
            else:
                if __debug__:
                    print("Current time: %s | destination_start: %s | destination_time: %s | destination_position: %s | original_position: %s" % (current_time, self.destination_start, self.destination_time, self.destination_position, self.original_position))
                    print("(current_time - self.destination_start): %s " % (current_time - self.destination_start))
                    print("(self.destination_time - self.destination_start): %s " %
                          (self.destination_time - self.destination_start))
                progress = float(current_time - self.destination_start) / float(self.destination_time - self.destination_start)
                if __debug__:
                    print("Currently %s way through this move" % progress)
                if self.original_position > self.destination_position:
                    if __debug__:
                        print("Closing slowly...")
                    position = int(round(self.original_position -
                                         ((self.original_position - self.destination_position) * progress)))
                else:
                    if __debug__:
                        print("Opening slowly....")
                    position = int(round(((self.destination_position - self.original_position) * progress) +
                                         self.original_position))
                if __debug__:
                    print("Current position request: %s " % position)
            try:
                self.i2c.set_pwm(self.Channel, 0, position)
                self.current_position = position
            except:
                print("Failed to send command %s/%s -> %s " % (self.Address, self.Channel, position))
#            if self.destination_position == self.current_position:
#               if __debug__:
#                   print("Reached final position")
#               self.processing = False
        if (self.destination_time + 200 < current_time) and self.processing == True:
            # Reset the servo and set processing to False
            if __debug__:
                print("Resetting servo")
            try:
                self.i2c.set_pwm(self.Channel, 4096, 0)
                self.processing = False
            except:
                if __debug__:
                    print("Failed to send command (reset) %s/%s" % (self.Address, self.Channel))
        return

    def run(self):
        if __debug__:
            print("Starting Thread")
        while True:
            self.sendCommand()
            try:
                command = self.q.get(False)
                position = command[0]
                duration = command[1]
                if position > 1 or position < 0:
                    print("Invalid position (%s)" % position)
                else:
                    self.destination_position = int(((self.Max - self.Min) * position) + self.Min)
                    self.processing = True
                self.destination_start = int(round(time.time() * 1000))
                self.destination_time = self.destination_start + (duration * 1000)
                self.original_position = self.current_position
                if __debug__:
                    print("Duration:    %s " % duration)
                    print("Destination: %s " % self.destination_position)
                    print("Original:    %s " % self.original_position)
                    print("Start time:  %s " % self.destination_start)
                    print("End time:    %s " % self.destination_time)
            except Empty:
                if self.processing != False:
                    self.sendCommand()

        return

