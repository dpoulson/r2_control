#!/usr/bin/python
#===============================================================================
# Copyright (C) 2014 Darren Poulson
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


import ConfigParser
import os, sys
sys.path.append("./classes/")
import thread
import time
import collections
# from i2cLCD import i2cLCD
from Adafruit_PWM_Servo_Driver import PWM
from R2_Servo_Control import ServoControl

config = ConfigParser.RawConfigParser()
config.read('config/main.cfg')

modules = config.sections()
i2c_bus = config.getint('DEFAULT', 'busid')
pipePath = config.get('DEFAULT', 'pipe')
debug = config.getboolean('DEFAULT', 'debug')
debug_lcd = config.getboolean('DEFAULT', 'debug_lcd')

keywords = []
devices = []
######################################
# initialise modules
x=0
for module in modules:
   if debug:
      print "Initialising module: %s" % module
   command = config.get(module, 'command')
   mod_type = config.get(module, 'type')
   address = config.get(module, 'address')
   keywords.append(command)
   if debug:
      print "Module uses command: %s, and is of type %s at address %s" % (command, mod_type, address)
   if mod_type == "lcd":
      print "LCD %s %s" % (command, address)
   elif mod_type == "teecee":
      print "teecee %s %s" % (command, address)
   elif mod_type == "servo":
      servoconfig = config.get(module, 'config_file')
      print "Servo %s %s %s" % (command, address, servoconfig)
      devices.append(ServoControl(address, servoconfig))
      print "Servo %s %s" % (command, address)
   x += 1


def run_module(keyword, data):
   print "Running........"

######################################
# Create pipe
# Check the pipe file exists, if it doesn't, create it.
try:
   os.mkfifo(pipePath)
except:
   if debug: 
      print "FIFO already exists"
os.chmod(pipePath,0666)

rp = open(pipePath, 'r')

######################################
# Main loop
while(True):
   response = rp.readline()
   command = response.rstrip('\r\n ')
   command_module = command.split(',')[0]
   if command_module != "":
      if debug: 
         print "Processing command..."
      if command_module in keywords:
         if debug:
            print "In keywords" 
         if command_module == "RELOAD":
            if debug:
               print "Reloading config file"
   	    config_reload()
         elif command_module == "QUIT":
            print "Quitting..."
            break
         elif command_module == "HOME":
            servo_home()
         else: 
            command_data = command.split(',',1)[1]
            if debug:
	       print "Module called: %s\tData Sent: %s" % (command_module, command_data)
	    run_module(command_module, command_data)
      else:
         if debug:
            print "Invalid Keyword"
	

rp.close()


