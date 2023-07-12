#!/usr/bin/python
from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
import threading
import time
standard_library.install_aliases()


class DomeThread(threading.Thread):

    def __init__(self, address, type, port):
        self.position_setpoint = 0
        self.current_position = 0
        self.random = False
        if __debug__:
            print("Initialising Dome thread")
        threading.Thread.__init__(self)
        return

    def set_position(self, new_position):
        if __debug__:
            print("Changing set position to: %s" % new_position)
        self.position_setpoint = new_position
        return

    def set_random(self, value):
        if __debug__:
            print("Setting random dome movement to: %s" % value)
        self.random = value
        return

    def get_position(self):
        msg = '%s,%s' % (self.position_setpoint, self.current_position)
        return msg

    def get_random(self):
        return str(self.random)

    def run(self):
        if __debug__:
            print("Starting Dome Thread")
        while True:
            print("Dome set to position: %s | Random: %s" % (self.position_setpoint, self.random))
            time.sleep(0.5)
        return
