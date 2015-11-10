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

from flask import Flask, request, render_template
import ConfigParser
import os, sys
sys.path.append("./classes/")
import threading
import time
import collections
# from i2cLCD import i2cLCD
from Adafruit_PWM_Servo_Driver import PWM
from ServoControl import ServoControl
from TeeCee_I2C import TeeCeeI2C
from AudioLibrary import AudioLibrary
from Adafruit_MCP230xx import MCP230XX_GPIO
from Adafruit_CharLCD import Adafruit_CharLCD


config = ConfigParser.RawConfigParser()
config.read('config/main.cfg')
sounds_dir = config.get('audio', 'sounds_dir')

modules = config.sections()
i2c_bus = config.getint('DEFAULT', 'busid')
pipePath = config.get('DEFAULT', 'pipe')
debug_lcd = config.getboolean('DEFAULT', 'debug_lcd')

devices_list = []
Devices = collections.namedtuple('Device', 'mod_type, address, device_object')


######################################
# initialise modules
# Initialise server controllers
pwm_body = ServoControl(int(config.get('body', 'address'), 16), config.get('body', 'config_file'))
pwm_dome = ServoControl(int(config.get('dome', 'address'), 16), config.get('dome', 'config_file'))
# Initialise LCD
lcd = Adafruit_CharLCD(pin_rs=1, pin_e=2, pins_db=[3,4,5,6], GPIO=MCP230XX_GPIO(1, int(config.get('lcd', 'address'), 16), int(config.get('lcd', 'bit'))))
lcd.message("R2 Control\nBy Darren Poulson")
# Initialise Audio
r2audio = AudioLibrary(sounds_dir)

'''
x=0
for module in modules:
   if __debug__:
      print "Initialising module: %s" % module
   mod_type = config.get(module, 'type')
   address = config.get(module, 'address')
   if __debug__:
      print "Module is of type %s at address %s" % (mod_type, address)
   if mod_type == "lcd":
      if __debug__:
         print "LCD %s" % (address)
      bus=1
      address=0x20
      bits=8
      mcp = MCP230XX_GPIO(bus, address, bits)
      devices_list.append(Devices(mod_type = mod_type, address = address, device_object = Adafruit_CharLCD(pin_rs=1, pin_e=2, pins_db=[3,4,5,6], GPIO=mcp)))
   elif mod_type == "teecee":
      if __debug__:
         print "teecee %s" % (address)
      devices_list.append(Devices(mod_type = mod_type, address = address, device_object = TeeCeeI2C(address)))
   elif mod_type == "servo":
      servoconfig = config.get(module, 'config_file')
      if __debug__:
         print "Servo %s %s" % (address, servoconfig)
      devices_list.append(Devices(mod_type = mod_type, address = address, device_object = ServoControl(address, servoconfig)))
   elif mod_type == "audio":
      audioconfig = config.get(module, 'config_file')
      if __debug__:
         print "Audio %s" % (address)
      devices_list.append(Devices(mod_type = mod_type, address = address, device_object = AudioLibrary(audioconfig)))
   x += 1
'''

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    """GET to generate a list of endpoints and their docstrings"""
    urls = dict([(r.rule, app.view_functions.get(r.endpoint).func_doc)
                 for r in app.url_map.iter_rules()
                 if not r.rule.startswith('/static')])
    return render_template('index.html', urls=urls)

@app.route('/teecee/<int:effect>', methods=['GET'])
def teecee(effect):
   """GET to fire off dome lighting effect """
   if request.method == 'GET':
      for device in devices_list:
         if device.mod_type == "teecee":
            try:
               t=threading.Thread(target=device.device_object.TriggerEffect(int(effect)) )
               t.daemon = True
               t.start()
            except Exception:
               print "Error: unable to start thread"
      return "Teecee"

#############################
# Servo API calls
#

@app.route('/servo/', methods=['GET'])
@app.route('/servo/list', methods=['GET'])
def servo_list():
   """GET to list all current servos and position"""
   if __debug__:
      print "Listing servos"
   if request.method == 'GET':
      message = ""
      message += pwm_body.list_servos()
      message += pwm_dome.list_servos()
   return message

@app.route('/servo/<location>/<servo_name>/<servo_position>/<servo_duration>', methods=['GET'])
def servo_move(location, servo_name, servo_position, servo_duration):
   """GET will move a selected servo to the required position over a set duration"""
   if request.method == 'GET':
     pwm_body.servo_command(servo_name, servo_position, servo_duration) 
   return "Ok"

@app.route('/servo/close', methods=['GET'])
def servo_close():
   """GET to close all servos"""
   if request.method == 'GET':
      message = ""
      for device in devices_list:
         if device.mod_type == "servo":
             device.device_object.close_all_servos(device.address)
      return "Ok"

@app.route('/servo/open', methods=['GET'])
def servo_open():
   """GET to open all servos"""
   if request.method == 'GET':
      message = ""
      for device in devices_list:
         if device.mod_type == "servo":
             device.device_object.open_all_servos(device.address)
      return "Ok"



@app.route('/lcd/<message>', methods=['GET'])
def lcd(message):
   if request.method == 'GET':
      for device in devices_list:
         if device.mod_type == "lcd":
            try:
               t=threading.Thread(target=device.device_object.TriggerLCD(int(message)) )
               t.daemon = True
               t.start()
            except Exception:
               print "Error: unable to start thread"
      return "Ok"

@app.route('/script/', methods=['GET'])
@app.route('/script/list', methods=['GET'])
@app.route('/script/<name>', methods=['GET'])
def script(name):
   """GET to trigger the named script"""

@app.route('/audio/', methods=['GET'])
@app.route('/audio/list', methods=['GET'])
def audio_list():
   """GET gives a comma separated list of available sounds"""
   if request.method == 'GET':
      message = ""
      message += r2audio.ListSounds()
   return message

@app.route('/audio/<name>', methods=['GET'])
def audio(name):
   if request.method == 'GET':
      r2audio.TriggerSound(name) 
   return "Ok"

@app.route('/audio/random/', methods=['GET'])
@app.route('/audio/random/list', methods=['GET'])
def random_audio_list():
   """GET returns types of sounds available at random"""
   if request.method == 'GET':
      message = ""
      message += r2audio.ListRandomSounds()
   return message

@app.route('/audio/random/<name>', methods=['GET'])
def random_audio(name):
   if request.method == 'GET':
      r2audio.TriggerRandomSound(name) 
   return "Ok"




if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True, use_reloader=False)

