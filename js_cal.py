#!/usr/bin/python

#import modules
import sys
sys.path.append('/home/pi/r2_control/classes/')
from Adafruit_PWM_Servo_Driver import PWM
import time
import os

channel = sys.argv[1]
print "Channel %s" % channel

def driveServo(channel, pulse):
   if __debug__:
      print "Channel %s : pulse %5.5f" % (channel,pulse)
   pwm.setPWM(channel, 0, int(pulse))

pwm = PWM(0x40, debug=True)
pwm.setPWMFreq(50) # Set frequency to 60 Hz

while True:
   global pulse
   pulse = raw_input("Enter value > ")
   driveServo(int(channel),float(pulse))

