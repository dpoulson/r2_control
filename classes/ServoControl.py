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
from Adafruit_PWM_Servo_Driver import PWM
from ServoThread import ServoThread
import threading
import Queue
import time
import csv
import collections

tick_duration = 100


class ServoControl :

  # servo_list = [] # All servos, listed here.

  Servo = collections.namedtuple('Servo', 'name, channel, Min, Max, home, Current, queue, thread')

  def init_config(self, address, servo_config_file):
   "Load in CSV of Servo definitions"
   ifile = open('config/%s' % servo_config_file, "rb")
   reader = csv.reader(ifile)
   for row in reader:
      servo_channel = int(row[0])
      servo_name = row[1]
      servo_Min = int(row[2])
      servo_Max = int(row[3])
      servo_home = int(row[4])
      queue=Queue.Queue()
      self.servo_list.append(self.Servo(name = servo_name, channel = servo_channel, Min = servo_Min, Max = servo_Max, home = servo_home, Current = servo_Min, queue=queue, thread = ServoThread(address, servo_Max, servo_Min, servo_home, servo_channel, queue)))
      for servo in self.servo_list:
         if servo.name == servo_name:
            servo.thread.daemon=True
            servo.thread.start()
      if __debug__:
         print "Added servo: %s %s %s %s %s" % (servo_channel, servo_name, servo_Min, servo_Max, servo_home)
   ifile.close()


  def __init__(self, address, servo_config_file):
    self.servo_list = []
#    self.i2c = PWM(address, debug=False)
#    self.i2c.setPWMFreq(60)
    self.init_config(address, servo_config_file)

  def list_servos(self):
    message = ""
    if __debug__:
       print "Listing servos for address:"
    for servo in self.servo_list:
       message += "%s,%s,%s\n" % ( servo.name, servo.channel, servo.servoCurrent )
    return message

  def close_all_servos(self, address):
    if __debug__:
       print "Closing all servos for address: %s" % address
    for servo in self.servo_list:
       if servo.address == address:
          self.i2c.setPWM(servo.channel, 0, servo.Min)
    return 

  def open_all_servos(self, address):
    if __debug__:
       print "Closing all servos for address: %s" % address
    for servo in self.servo_list:
       if servo.address == address:
          self.i2c.setPWM(servo.channel, 0, servo.Max)
    return

  # Send a command over i2c to turn a servo to a given position (percentage) over a set duration (seconds)
  #def servo_command(self, servo_name, position, duration):
  def servo_command(self, servo_name, position, duration):
   if __debug__:
      print "Moving %s to %s over duration %s" % ( servo_name, position, duration )
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
   current_servo.queue.put([position, duration])

"""
   if position > 1 or position < 0 or not current_servo:
      print "Invalid name or position (%s, %s)" % (servo_name, position)
   else: 
      actual_position = int(((current_servo.Max - current_servo.Min)*position) + current_servo.Min)
      if __debug__:
         print "Duration: %s " % duration
      if duration > 0:
         ticks = (duration * 1000)/tick_duration 
         tick_position_shift = (actual_position - current_servo.Current )/float(ticks)
         tick_actual_position = current_servo.Current + tick_position_shift
         if __debug__:
            print "Ticks:%s  Current Position: %s Position shift: %s Starting Position: %s End Position %s" % (ticks, current_servo.Current, tick_position_shift, tick_actual_position, actual_position)
         for x in range(0, ticks):
            if __debug__:
               print "Tick: %s Position: %s" % (x, tick_actual_position)
            self.i2c.setPWM(current_servo.channel, 0, int(tick_actual_position)) 
            tick_actual_position += tick_position_shift
         if __debug__:
            print "Finished move: Position: %s" % tick_actual_position
      else:
         if __debug__:
            print "Setting servo %s(%s) to position = %s(%s)" % (servo_name, current_servo.channel, actual_position, position)
#         self.i2c.setPWM(current_servo.channel, 0, actual_position)
         current_servo.queue.put([current_servo.channel, actual_position, duration])
      # Save current position of servo
      for servo in self.servo_list:
        if servo.name == servo_name:
          idx = self.servo_list.index(servo)
          if __debug__:
             print "Servo move finished. Servo.name: %s ServoCurrent %s Tick %s Index %s" % (servo.name, servo.Current, actual_position, idx)
          self.servo_list[idx] = self.servo_list[idx]._replace(Current=actual_position)
          if __debug__:
             print "New current: %s" % self.servo_list[idx].Current
#   time.sleep(0.5)
#   self.i2c.setPWM(current_servo.channel, 4096, 0)
"""


