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

from flask import Flask, request
import ConfigParser
import os, sys
sys.path.append("./classes/")
import thread
import time
import collections
# from i2cLCD import i2cLCD
from Adafruit_PWM_Servo_Driver import PWM
from R2_Servo_Control import ServoControl
from TeeCee_I2C import TeeCeeI2C
from AudioLibrary import AudioLibrary

config = ConfigParser.RawConfigParser()
config.read('config/main.cfg')

modules = config.sections()
i2c_bus = config.getint('DEFAULT', 'busid')
pipePath = config.get('DEFAULT', 'pipe')
debug = config.getboolean('DEFAULT', 'debug')
debug_lcd = config.getboolean('DEFAULT', 'debug_lcd')

devices_list = []
Devices = collections.namedtuple('Device', 'mod_type, address, device_object')


######################################
# initialise modules
x=0
for module in modules:
   if debug:
      print "Initialising module: %s" % module
   mod_type = config.get(module, 'type')
   address = config.get(module, 'address')
   if debug:
      print "Module is of type %s at address %s" % (mod_type, address)
   if mod_type == "lcd":
      print "LCD %s" % (address)
   elif mod_type == "teecee":
      if debug:
         print "teecee %s" % (address)
      devices_list.append(Devices(mod_type = mod_type, address = address, device_object = TeeCeeI2C(address)))
   elif mod_type == "servo":
      servoconfig = config.get(module, 'config_file')
      if debug:
         print "Servo %s %s" % (address, servoconfig)
      devices_list.append(Devices(mod_type = mod_type, address = address, device_object = ServoControl(address, servoconfig)))
   elif mod_type == "audio":
      audioconfig = config.get(module, 'config_file')
      if debug:
         print "Audio %s" % (address)
      devices_list.append(Devices(mod_type = mod_type, address = address, device_object = AudioLibrary(audioconfig)))
   x += 1

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>Welcome to R2D2 REST API.</h1><p>Endpoints: <ul><li>/teecee</li><li><a href=\"/servo/list\">/servo</a></li><li>/lcd</li><li><a href=\"/audio/list\">/audio</a></li></ul></p>"

@app.route('/teecee/<int:effect>', methods=['GET'])
def teecee(effect):
   if request.method == 'GET':
      for device in devices_list:
         if device.mod_type == "teecee":
            try:
               thread.start_new_thread( device.device_object.TriggerEffect(int(effect)) )
            except Exception:
               print "Error: unable to start thread"
      return "Teecee"


@app.route('/servo/<servo_name>/<servo_position>/<servo_duration>', methods=['GET'])
def servo(servo_name, servo_position, servo_duration):
   if request.method == 'GET':
      for device in devices_list:
         if device.mod_type == "servo":
            #servo_name = request.data.split(',')[0]
            #servo_position = request.data.split(',')[1]
            #try:
            #   servo_duration = request.data.split(',')[2]
            #except:
            #   servo_duration = 0
            try:
               thread.start_new_thread( device.device_object.servo_command(servo_name, servo_position, servo_duration) )
            except Exception:
               print "Error: unable to start thread"
      return "Ok"

@app.route('/servo/list', methods=['GET'])
def servo_list():
   if request.method == 'GET':
      message = ""
      for device in devices_list:
         if device.mod_type == "servo":
             message += device.device_object.list_servos(device.address)
      return message

       

@app.route('/lcd/<message>', methods=['GET'])
def lcd(message):
   if request.method == 'GET':
      for device in devices_list:
         if device.mod_type == "lcd":
            try:
               thread.start_new_thread( device.device_object.TriggerLCD(int(message)) )
            except Exception:
               print "Error: unable to start thread"
      return "Ok"

@app.route('/audio/<name>', methods=['GET'])
def audio(name):
   if request.method == 'GET':
      for device in devices_list:
         if device.mod_type == "audio":
            if debug:
               print "Audio %s " % (name)
            try:
               thread.start_new_thread( device.device_object.TriggerSound(name) )
            except Exception:
               print "Error: unable to start thread"
      return "Ok"

@app.route('/audio/list', methods=['GET'])
def audio_list():
   if request.method == 'GET':
      message = ""
      for device in devices_list:
         if device.mod_type == "audio":
             message += device.device_object.ListSounds()
      return message






if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)

