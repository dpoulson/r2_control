#!/usr/bin/python

import os
from Adafruit_PWM_Servo_Driver import PWM
import time
import csv

servo_config_file = "servo.conf"

def init():
   # Load in CSV of Servo definitions
   ifile = open(servo_config_file, "rb")
   reader = csv.reader(ifile)
   

pipePath = "/tmp/r2_commands.pipe"

rp = open(pipePath, 'r')
while(True):
   response = rp.readline()
   command = response.strip
   if command != "":
      print "Got %s" % response
      response=""

rp.close()


