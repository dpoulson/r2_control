import smbus, time, threading, struct, csv
from threading import Thread
from time import sleep


class FlthyHPControl(threading.Thread):

    def __init__(self, address, logdir):
        self.address = address
        self.bus = smbus.SMBus(1)
        self.logdir = logdir
        if __debug__:
            print "Initialising FlthyHP Control"

    def playSequence(self, seq):
        return "Ok"

    def sendCommand(self, cmd):
        return "Ok"

