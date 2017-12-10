#!/usr/bin/python
# 
import smbus, time, threading, struct, csv
from threading import Thread
from time import sleep


class i2cMonitor(threading.Thread):

    def monitor_loop(self):
        f = open(self.logdir + '/power.log', 'wt')
        while True:
            try:
                data = self.bus.read_i2c_block_data(0x04, 0)
            except:
                if __debug__:
                    print "Failed to read i2c data"
                sleep(1)
            self.extracted[0] = time.time()
            for i in range(0, 8):
                bytes = data[4 * i:4 * i + 4]
                self.extracted[i + 1] = struct.unpack('f', "".join(map(chr, bytes)))[0]
            if __debug__:
                print "Writing csv row"
            writer = csv.writer(f)
            writer.writerow(self.extracted)
            f.flush()
            sleep(self.interval)
        f.close()

    def __init__(self, address, interval, logdir):
        self.address = address
        self.interval = interval
        self.bus = smbus.SMBus(1)
        self.logdir = logdir
        self.extracted = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        if __debug__:
            print "Monitoring...."
        loop = Thread(target=self.monitor_loop)
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
