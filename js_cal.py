#!/usr/bin/python

#import modules
import sys
sys.path.append('/home/pi/r2_control/classes/')
from Adafruit_PWM_Servo_Driver import PWM
import time
import os

channel = sys.argv[2]
bus = int(sys.argv[1], 16)
freq = 60
print "Channel %s : Frequency %s" % (channel,freq)

def driveServo(channel, pulse):
   period = 1/float(freq)
   bit_duration = period/4096
   pulse_duration = bit_duration*pulse*1000000
   if __debug__:
      print "Channel %s : pulse %5.5f : Duration: %s" % (channel,pulse,pulse_duration)
   try:
      pwm.setPWM(channel, 0, int(pulse))
   except:
      print "Failed to send command"

pwm = PWM(bus, debug=True)
pwm.setPWMFreq(freq) # Set frequency to 60 Hz

while True:
   global pulse
   pulse = raw_input("Enter value > ")
   driveServo(int(channel),float(pulse))

