#!/usr/bin/python

import os
from Adafruit_PWM_Servo_Driver import PWM
import time
import csv
import collections

servo_config_file = "servo.conf"
pipePath = "/tmp/r2_commands.pipe"

Servos = collections.namedtuple('Servo', 'address, channel, name, servoMin, servoMax')

servo_list = Servos(address='0x40', channel = 7, name = "PP2", servoMin = 140, servoMax = 660)

def init():
   # Load in CSV of Servo definitions
   ifile = open(servo_config_file, "rb")
   reader = csv.reader(ifile)
   


pwm = PWM(0x40, debug=False)
pwm.setPWMFreq(60) 

def servo_command(servo_name, position):
   actual_position = int(((servo_list.servoMax - servo_list.servoMin)*float(position)) + servo_list.servoMin)
   print "Setting servo %s to position = %s" % (servo_name, actual_position)
   pwm.setPWM(servo_list.channel, 0, actual_position)



# Main loop

rp = open(pipePath, 'r')
while(True):
   response = rp.readline()
   command = response.rstrip('\r\n ')
   if command != "":
      command_name = command.split(',')[0]
      command_position = command.split(',')[1]
      servo_command(command_name, command_position)

rp.close()


