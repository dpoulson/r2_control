#!/usr/bin/python
# 
import smbus,time,threading,struct
from threading import Thread
from subprocess import * 
from time import sleep, strftime
from datetime import datetime


class i2cMonitor(threading.Thread):

  def monitor_loop(self):
    global extracted
    while True:
        try:
            data = self.bus.read_i2c_block_data(0x04, 0);
        except:
            if __debug__:
                print "Failed to read i2c data"
            sleep(1)
        for i in range(0, 8):
            bytes = data[4*i:4*i+4]
            self.extracted[i] = struct.unpack('f', "".join(map(chr, bytes)))[0]
        sleep(self.interval)

  def __init__(self, address, interval, logdir):
    self.address = address
    self.interval = interval
    self.bus = smbus.SMBus(1)
    self.extracted = [0,0,0,0,0,0,0,0]
    if __debug__:
      print "Monitoring...."
    loop = Thread(target = self.monitor_loop)
    loop.start()

  def queryBattery(self):
      return self.extracted[4]

  def queryBatteryBalance(self):
      return self.extracted[6]-self.extracted[5]

  def queryCurrentMain(self):
      return self.extracted[0]

  def queryCurrentLeft(self):
      return self.extracted[1]

  def queryCurrentRight(self):
      return self.extracted[2]

  def queryCurrentDome(self):
      return self.extracted[3]

