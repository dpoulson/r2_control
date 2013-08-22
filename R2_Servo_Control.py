#!/usr/bin/python
#===============================================================================
# Copyright (C) 2013 Darren Poulson
#
# This file is part of R2_Control.
#
# pyfa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyfa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyfa.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

import os, sys
import thread
from Adafruit_PWM_Servo_Driver import PWM
import time
import csv
import collections

servo_config_file = "servo.conf"
pipePath = "/tmp/r2_commands.pipe"
servo_list = []

Servos = collections.namedtuple('Servo', 'address, channel, name, servoMin, servoMax, servoHome, servoCurrent')

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
      servo_home = int(row[5])
      servo_list.append(Servos(address = servo_address, channel = servo_channel, name = servo_name, servoMin = servo_servoMin, servoMax = servo_servoMax, servoHome = servo_home, servoCurrent = servo_home))
   ifile.close()
   # Check the pipe file exists, if it doesn't, create it.
   try:
      os.mkfifo(pipePath)
   except:
      print "FIFO already exists"
   os.chmod(pipePath,0666)
   

# Send a command over i2c to turn a servo to a given position (percentage) over a set duration (seconds)
def servo_command(servo_name, position, duration):
   current_servo = []
   try:
      position = float(position)
   except:
      print "Position not a float"
   for servo in servo_list:
      if servo.name == servo_name:
         current_servo = servo
   if position > 1 or position < 0 or not current_servo:
      print "Invalid name or position (%s, %s)" % (servo_name, position)
   else: 
      actual_position = int(((current_servo.servoMax - current_servo.servoMin)*position) + current_servo.servoMin)
      print "Setting servo %s(%s) to position = %s(%s) with duration = %s" % (servo_name, current_servo.channel, actual_position, position, duration)
      pwm.setPWM(current_servo.channel, 0, actual_position)

# Set all servos to home position
def servo_home():
   for servo in servo_list:
      pwm.setPWM(servo.channel, 0, servo.servoHome)

# Initialise servo controllers
pwm = PWM(0x40, debug=False)
pwm.setPWMFreq(60)  

# Main loop

init_config()
servo_home()

rp = open(pipePath, 'r')

# Listen for commands on the pipe
while(True):
   response = rp.readline()
   command = response.rstrip('\r\n ')
   if command != "":
      print "Processing command..."
      if command == "RELOAD":
         print "Reloading config file"
         servo_list = []
         init_config()
         servo_home()
      elif command == "QUIT":
         print "Quitting..."
         break
      elif command == "HOME":
         servo_home()
      else: 
         command_name = command.split(',')[0]
         command_position = command.split(',')[1]
         try:
            command_duration = command.split(',')[2]
         except:
            command_duration = 0
	 try:
            thread.start_new_thread( servo_command, (command_name, command_position, command_duration) )
         except:
            print "Error: unable to start thread"

rp.close()


