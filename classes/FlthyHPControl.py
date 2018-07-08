import smbus, time, threading, struct, csv
from threading import Thread
from time import sleep


class FlthyHPControl:

    def __init__(self, address, logdir):
        self.address = address
        self.bus = smbus.SMBus(1)
        self.logdir = logdir
        if __debug__:
            print "Initialising FlthyHP Control"

    def sendSequence(self, seq):
        if seq.isdigit():
            if __debug__:
                print "Integer sent, sending command"
            cmd = 'S' + seq
            self.sendCommand(cmd)
        else: 
            if __debug__:
                print "Not an integer, decode and send command"
            if seq == "leia":
                if __debug__:
                    print "Leia mode"
                self.sendCommand('S1')
            if seq == "disable":
                if __debug__:
                    print "Clear and Disable"
                self.sendCommand('S8')
            if seq == "enable":
                if __debug__:
                    print "Clear and Enable"
                self.sendCommand('S9') 
        return "Ok"

    def sendCommand(self, cmd):
        arrayCmd = bytearray(cmd,'utf8')
        if __debug__:
            print arrayCmd
        for i in arrayCmd:
            if __debug__:
                print "Sending byte: %c " % i
            try:
                bus.write_byte(self.address, i)
            except:
                print "Failed to send command to %s" % self.address
        return "Ok"

