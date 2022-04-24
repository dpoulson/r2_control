#!/usr/bin/python

#import modules
import sys
sys.path.append('/home/pi/r2_control/classes/')
import Adafruit_PCA9685
import time
import os

channel = sys.argv[2]
bus = int(sys.argv[1], 16)
freq = 60
print("Channel %s : Frequency %s" % (channel,freq))

def driveServo(channel, pulse):
   period = 1/float(freq)
   bit_duration = period/4096
   pulse_duration = bit_duration*pulse*1000000
   if __debug__:
      print("Channel %s : pulse %5.5f : Duration: %s" % (channel,pulse,pulse_duration))
   try:
      i2c.set_pwm(channel, 0, int(pulse))
   except:
      print("Failed to send command")

i2c = Adafruit_PCA9685.PCA9685(address=bus, busnum=1)
i2c.set_pwm_freq(60)


while True:
   global pulse
   pulse = input("Enter value > ")
   driveServo(int(channel),float(pulse))

