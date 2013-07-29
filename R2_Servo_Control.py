#!/usr/bin/python

import os
from Adafruit_PWM_Servo_Driver import PWM
import time
import csv
import collections

servo_config_file = "servo.conf"
pipePath = "/tmp/r2_commands.pipe"

Servos = collections.namedtuple('Servo', 'address, channel, name, servoMin, servoMax')

servo_list = []


def init_config():
   # Load in CSV of Servo definitions
   ifile = open(servo_config_file, "rb")
   reader = csv.reader(ifile)
   for row in reader:
      servo_address = row[0]
      servo_channel = int(row[1])
      servo_name = row[2]
      servo_servoMin = int(row[3])
      servo_servoMax = int(row[4])
      servo_list.append(Servos(address=servo_address, channel = servo_channel, name = servo_name, servoMin = servo_servoMin, servoMax = servo_servoMax))
   ifile.close()




def servo_command(servo_name, position):
   current_servo = []
   for servo in servo_list:
      if servo.name == servo_name:
         current_servo = servo
   if float(position) > 1 or float(position) < 0 or not current_servo:
      print "Invalid name or position (%s, %s)" % (servo_name, position)
   else: 
      actual_position = int(((current_servo.servoMax - current_servo.servoMin)*float(position)) + current_servo.servoMin)
      print "Setting servo %s(%s) to position = %s(%s)" % (servo_name, current_servo.channel, actual_position, position)
      pwm.setPWM(current_servo.channel, 0, actual_position)



# Main loop

init_config()

# Initialise servo controllers
pwm = PWM(0x40, debug=False)
pwm.setPWMFreq(60)  

rp = open(pipePath, 'r')
while(True):
   response = rp.readline()
   command = response.rstrip('\r\n ')
   if command != "":
      print "Processing command..."
      if command == "RELOAD":
         print "Reloading config file"
         servo_list = []
         init_config()
      elif command == "QUIT":
         break
      else: 
         command_name = command.split(',')[0]
         command_position = command.split(',')[1]
         servo_command(command_name, command_position)



rp.close()


