#!/usr/bin/python
# 
from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
import smbus
import time
import threading
import struct
import csv
from threading import Thread
from time import sleep
from r2utils import mainconfig
from r2utils import telegram
standard_library.install_aliases()
from builtins import map
from builtins import range


class i2cMonitor(threading.Thread):

    def monitor_loop(self):
        f = open(self.logdir + '/power.log', 'at')
        data = [0, 0, 0, 0, 0, 0, 0, 0]
        while True:
            try:
                data = self.bus.read_i2c_block_data(0x04, 0)
            except:
                if __debug__:
                    print("Failed to read i2c data")
                sleep(1)
            self.extracted[0] = time.time()
            for i in range(0, 8):
                bytes = data[4 * i:4 * i + 4]
                self.extracted[i + 1] = struct.unpack('f', "".join(map(chr, bytes)))[0]
            if __debug__:
                print("Writing csv row")
            writer = csv.writer(f)
            writer.writerow(self.extracted)
            f.flush()
            sleep(self.interval)
            # If telegram messaging is active, do a few checks and notify
            if self.telegram:
                if __debug__:
                    print("Telegram enabled")
                if (self.extracted[5] != 0) and (self.extracted[5] < 21) and not self.lowbat:
                    if __debug__:
                        print("Battery low")
                    telegram.send("Battery below 21V")
                    self.lowbat = True
            f.close()

    def __init__(self, address, interval):
        # Check for telegram config
        self.telegram = False
        self.address = address
        self.interval = interval
        self.logdir = mainconfig.mainconfig['logdir']
        self.lowbat = False
        self.extracted = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        try:
            self.bus = smbus.SMBus(int(mainconfig.mainconfig['busid']))
        except:
            print("Failed to connect to device on bus")
        if __debug__:
            print("Monitoring....")
        if self.telegram:
            telegram.send("Monitoring started")
        loop = Thread(target=self.monitor_loop)
        loop.daemon = True
        loop.start()

    def queryBattery(self):
        return self.extracted[5]

    def queryBatteryBalance(self):
        return self.extracted[7] - self.extracted[6]

    def queryCurrentMain(self):
        return self.extracted[1]

    def queryCurrentLeft(self):
        return self.extracted[2]

    def queryCurrentRight(self):
        return self.extracted[3]

    def queryCurrentDome(self):
        return self.extracted[4]

