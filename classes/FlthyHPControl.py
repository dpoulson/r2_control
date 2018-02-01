import smbus, time, threading, struct, csv
from threading import Thread
from time import sleep


class FlthyHPControl(threading.Thread):

    def __init__(self, address):
        self.address = int(address)
        self.bus = smbus.SMBus(1)
        if __debug__:
            print "Initialising FlthyHP Control"

    def playSequence(self, seq):
        return "Ok"

    def sendCommand(self, hp, cmd):
        command = []
        for character in cmd:
            command.append(ord(character))
        print command
        if __debug__:
            print "Flthy: address = %s, hp = %s, command = %s" % (self.address, ord(hp), command)
        try:
            self.bus.write_i2c_block_data(self.address, ord(hp), command)
        except:
            print "Failed to write to Flthy HP"
        return "Ok"

