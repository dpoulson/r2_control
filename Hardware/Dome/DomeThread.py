#!/usr/bin/python
from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
import threading
from queue import Queue, Empty
import time
standard_library.install_aliases()

class ServoThread(threading.Thread):
    def __init__(self, Address, Max, Min, Home, Channel, q):
        if __debug__:
            print("Initialising Dome thread")
        return

    def sendCommand(self):

        return

    def run(self):
        if __debug__:
            print("Starting Dome Thread")
        while True:

        return



