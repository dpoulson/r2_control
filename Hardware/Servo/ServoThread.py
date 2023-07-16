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

ADDRESS = 0x40
MAX = 0
MIN = 0
CURRENT = 0
HOME = 0
CHANNEL = 0


class ServoThread(threading.Thread):
    def __init__(self, Address, Max, Min, Home, Channel, q):
        if __debug__:
            print("Initialising thread")
        self.q = q
        self.Address = ADDRESS
        self.Max = MAX
        self.Min = MIN
        self.Home = HOME
        self.current_position = HOME
        self.original_position = HOME
        self.Channel = CHANNEL
        self.destination_position = HOME
        self.destination_start = 0
        self.destination_time = 0
        self.processing = False
        threading.Thread.__init__(self)
        try:
            self.i2c = Adafruit_PCA9685.PCA9685(address=int(self.Address, 16), busnum=int(1))
            self.i2c.set_pwm_freq(60)
        except Exception:
            print("Failed to initialise servo at %s/%s" % (self.Address, self.Channel))
            raise Exception("Failed to initialise server")
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
                    print("Current time: %s | destination_start: %s | destination_time: %s | destination_position: %s | original_position: %s" %  # noqa: E501
                          (current_time, self.destination_start, self.destination_time, self.destination_position, self.original_position))  # noqa: E501
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
            except Exception:
                print("Failed to send command %s/%s -> %s " % (self.Address, self.Channel, position))
#            if self.destination_position == self.current_position:
#               if __debug__:
#                   print("Reached final position")
#               self.processing = False
        if (self.destination_time + 200 < current_time) and self.processing is True:
            # Reset the servo and set processing to False
            if __debug__:
                print("Resetting servo")
            try:
                self.i2c.set_pwm(self.Channel, 4096, 0)
                self.processing = False
            except Exception:
                if __debug__:
                    print("Failed to send command (reset) %s/%s" % (self.Address, self.Channel))
        return

    def run(self):
        if __debug__:
            print("Starting Thread")
        while True:
            try:
                command = self.q.get(False)
                position = command[0]
                duration = command[1]
                if position > 1 or position < 0:
                    print(f"Invalid position ({position})")
                else:
                    self.destination_position = int(((self.Max - self.Min) * position) + self.Min)
                    self.processing = True
                self.destination_start = int(round(time.time() * 1000))
                self.destination_time = self.destination_start + (duration * 1000)
                self.original_position = self.current_position
                if __debug__:
                    print(f"Duration:    {duration} ")
                    print(f"Destination: {self.destination_position} ")
                    print(f"Original:    {self.original_position} ")
                    print(f"Start time:  {self.destination_start} ")
                    print(f"End time:    {self.destination_time} ")
                self.sendCommand()                            # Main Command Loop
            except Empty:
                if self.processing is not False:
                    self.sendCommand()
            time.sleep(0.005)

        return
