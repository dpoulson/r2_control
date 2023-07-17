""" Module for firing off Dome Thread """
from future import standard_library
import threading
import time
standard_library.install_aliases()


class DomeThread(threading.Thread):
    """ Class to control dome threads """

    def __init__(self, address, drivetype, port):
        self.position_setpoint = 0
        self.current_position = 0
        self.random = False
        if __debug__:
            print("Initialising Dome thread")
        threading.Thread.__init__(self)
        return

    def SetPosition(self, new_position):
        if __debug__:
            print(f"Changing set position to: {new_position}")
        self.position_setpoint = new_position
        return

    def SetRandom(self, value):
        if __debug__:
            print(f"Setting random dome movement to: {value}")
        self.random = value
        return

    def GetPosition(self):
        msg = '%s,%s' % (self.position_setpoint, self.current_position)
        return msg

    def GetRandom(self):
        return str(self.random)

    def run(self):
        if __debug__:
            print("Starting Dome Thread")
        while True:
            print(f"Dome set to position: {self.position_setpoint} | Random: {self.random}")
            time.sleep(0.5)
        return
