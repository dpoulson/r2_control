#!/usr/bin/python
# 
import smbus,time
from subprocess import * 
from time import sleep, strftime
from datetime import datetime
from Adafruit_I2C import Adafruit_I2C



class i2cMonitor:

  def __init__(self, address=0x04, debug=False):
    self.i2c = Adafruit_I2C(address, 1)
    self.address = address
    self.debug = debug
    if __debug__:
      print "Monitoring...."
    self.clear()


