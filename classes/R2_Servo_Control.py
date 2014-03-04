#!/usr/bin/python
#===============================================================================
# Copyright (C) 2013 Darren Poulson
#
# This file is part of R2_Control.
#
# R2_Control is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# R2_Control is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with R2_Control.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

import os, sys
import thread
from Adafruit_PWM_Servo_Driver import PWM
import time
import csv
import collections

tick_duration = 100

class ServoControl :

  servo_list = []

  Servos = collections.namedtuple('Servo', 'channel, name, servoMin, servoMax, servoHome, servoCurrent')

  def init_config(self, servo_config_file):
   "Load in CSV of Servo definitions"
   ifile = open('config/%s' % servo_config_file, "rb")
   reader = csv.reader(ifile)
   for row in reader:
      servo_channel = int(row[0])
      servo_name = row[1]
      servo_servoMin = int(row[2])
      servo_servoMax = int(row[3])
      servo_home = int(row[4])
      self.servo_list.append(self.Servos(channel = servo_channel, name = servo_name, servoMin = servo_servoMin, servoMax = servo_servoMax, servoHome = servo_home, servoCurrent = 0))
   ifile.close()


  def __init__(self, address, servo_config_file):
    self.i2c = PWM(0x40, debug=False)
    self.i2c.setPWMFreq(60)
    self.init_config(servo_config_file)


  # Send a command over i2c to turn a servo to a given position (percentage) over a set duration (seconds)
  def servo_command(self, servo_name, position, duration):
   current_servo = []
   try:
      position = float(position)
   except:
      print "Position not a float"
   try:
      duration = int(duration)
   except:
      print "Duration is not an int"
   for servo in self.servo_list:
      if servo.name == servo_name:
         current_servo = servo
   if position > 1 or position < 0 or not current_servo:
      print "Invalid name or position (%s, %s)" % (servo_name, position)
   else: 
      actual_position = int(((current_servo.servoMax - current_servo.servoMin)*position) + current_servo.servoMin)
      print "Duration: %s " % duration
      if duration > 0:
         ticks = (duration * 1000)/tick_duration 
         tick_position_shift = (actual_position - current_servo.servoCurrent )/ticks
         tick_actual_position = current_servo.servoCurrent + tick_position_shift
         print "Ticks:%s  Current Position: %s Position shift: %s Starting Position: %s" % (ticks, current_servo.servoCurrent, tick_position_shift, tick_actual_position)
         for x in range(0, ticks):
            print "Tick: %s Position: %s" % (x, tick_actual_position)
            self.i2c.setPWM(current_servo.channel, 0, tick_actual_position) 
            tick_actual_position += tick_position_shift
         for servo in self.servo_list:
           if servo.name == servo_name:
             servo.servoCurrent = tick_actual_position
      else:
         print "Setting servo %s(%s) to position = %s(%s) with duration = %s" % (servo_name, current_servo.channel, actual_position, position, duration)
         self.i2c.setPWM(current_servo.channel, 0, actual_position)
         current_servo.servoCurrent = actual_position


