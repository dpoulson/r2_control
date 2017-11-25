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
# from flask.ext.classy import FlaskView
import ConfigParser
import os, sys
sys.path.append("./classes/")
import threading
import time
import collections
import socket
from datetime import timedelta

# from i2cLCD import i2cLCD
from Adafruit_PWM_Servo_Driver import PWM
from ServoControl import ServoControl
from ScriptControl import ScriptControl
from TeeCee_I2C import TeeCeeI2C
from AudioLibrary import AudioLibrary
from Adafruit_MCP230xx import MCP230XX_GPIO
from Adafruit_CharLCD import Adafruit_CharLCD


config = ConfigParser.RawConfigParser()
config.read('config/main.cfg')

modules = config.sections()
i2c_bus = config.getint('DEFAULT', 'busid')
pipePath = config.get('DEFAULT', 'pipe')
debug_lcd = config.getboolean('DEFAULT', 'debug_lcd')

devices_list = []

app = Flask(__name__, template_folder='templates')

######################################
# initialise modules
# Initialise server controllers
if "body" in modules:
  pwm_body = ServoControl(int(config.get('body', 'address'), 16), config.get('body', 'config_file'))
if "dome" in modules:
  pwm_dome = ServoControl(int(config.get('dome', 'address'), 16), config.get('dome', 'config_file'))
# Initialise LCD
if "lcd" in modules:
  lcd = Adafruit_CharLCD(pin_rs=1, pin_e=2, pins_db=[3,4,5,6], GPIO=MCP230XX_GPIO(1, int(config.get('lcd', 'address'), 16), int(config.get('lcd', 'bit'))))
  lcd.write("R2 Control\nBy Darren Poulson")
# Initialise Audio
if "audio" in modules:
  r2audio = AudioLibrary(config.get('audio', 'sounds_dir'), config.get('audio', 'volume'))
# Initialise script object
if "scripts" in modules:
  scripts = ScriptControl(config.get('scripts', 'script_dir'))


def system_status():
   with open('/proc/uptime', 'r') as f:
      uptime_seconds = float(f.readline().split()[0])
      uptime_string = str(timedelta(seconds = uptime_seconds))
   try:
      host = socket.gethostbyname("www.google.com")
      s = socket.create_connection((host, 80), 2)
      internet_connection = True
   except:
      internet_connection = False
   status = "Current Status\n"
   status += "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n"
   status += "Uptime: \t\t%s\n" % uptime_string
   status += "Main Battery: \t\n"
   status += "Remote Battery: \t\n"
   status += "Wifi: \t\t\n"
   status += "Internet: \t%s \n" % internet_connection
   status += "Location: \t\n"
   status += "Volume: \t\t%s\n" % r2audio.ShowVolume()
   status += "--------------\n"
   status += "Scripts Running:\n"
   status += scripts.list_running()
   return status

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    """GET to generate a list of endpoints and their docstrings"""
    urls = dict([(r.rule, app.view_functions.get(r.endpoint).func_doc)
                 for r in app.url_map.iter_rules()
                 if not r.rule.startswith('/static')])
    return render_template('index.html', urls=urls)

#############################
# Lights API calls
#


@app.route('/teecee/<int:effect>', methods=['GET'])
def teecee(effect):
   """GET to fire off dome lighting effect """
   if request.method == 'GET':
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

@app.route('/servo/dome/list', methods=['GET'])
def servo_list_dome():
   """GET to list all current servos and position"""
   if __debug__:
      print "Listing servos"
   if request.method == 'GET':
      message = ""
      message += pwm_dome.list_servos()
   return message

@app.route('/servo/body/list', methods=['GET'])
def servo_list_body():
   """GET to list all current servos and position"""
   if __debug__:
      print "Listing servos"
   if request.method == 'GET':
      message = ""
      message += pwm_body.list_servos()
   return message



@app.route('/servo/<part>/<servo_name>/<servo_position>/<servo_duration>', methods=['GET'])
def servo_move(part, servo_name, servo_position, servo_duration):
   """GET will move a selected servo to the required position over a set duration"""
   if request.method == 'GET':
     if part == 'body':
        pwm_body.servo_command(servo_name, servo_position, servo_duration) 
     if part == 'dome': 
        pwm_dome.servo_command(servo_name, servo_position, servo_duration)
   return "Ok"

@app.route('/servo/close', methods=['GET'])
def servo_close():
   """GET to close all servos"""
   if request.method == 'GET':
      message = ""
      pwm_body.close_all_servos()
      pwm_dome.close_all_servos() 
      return "Ok"

@app.route('/servo/dome/close', methods=['GET'])
def servo_dome_close():
   """GET to close all dome servos"""
   if request.method == 'GET':
      message = ""
      pwm_dome.close_all_servos()
      return "Ok"

@app.route('/servo/body/close', methods=['GET'])
def servo_body_close():
   """GET to close all body servos"""
   if request.method == 'GET':
      message = ""
      pwm_body.close_all_servos()
      return "Ok"


@app.route('/servo/open', methods=['GET'])
def servo_open():
   """GET to open all servos"""
   if request.method == 'GET':
      message = ""
      pwm_body.open_all_servos()
      pwm_dome.open_all_servos()
      return "Ok"

@app.route('/servo/dome/open', methods=['GET'])
def servo_dome_open():
   """GET to open all dome servos"""
   if request.method == 'GET':
      message = ""
      pwm_dome.open_all_servos()
      return "Ok"

@app.route('/servo/body/open', methods=['GET'])
def servo_body_open():
   """GET to open all body servos"""
   if request.method == 'GET':
      message = ""
      pwm_body.open_all_servos()
      return "Ok"



#############################
# LCD API calls
#


@app.route('/lcd/<message>', methods=['GET'])
def lcd_write(message):
   """GET to write a message to the LCD screen"""
   if request.method == 'GET':
     lcd.write("%s" % message)     
   return "Ok"


#############################
# Script API calls
#

@app.route('/script/', methods=['GET'])
@app.route('/script/list', methods=['GET'])
def script_list():
   """GET gives a comma separated list of available scripts"""
   if request.method == 'GET':
      message = ""
      message += scripts.list()
   return message

@app.route('/script/running', methods=['GET'])
def running_scripts():
   """GET a list of all running scripts and their ID"""
   if request.method == 'GET':
     message = ""
     message += scripts.list_running()
   return message

@app.route('/script/stop/<script_id>', methods=['GET'])
def stop_script(script_id):
   """GET a script ID to stop that script"""
   if request.method == 'GET':
     message = ""
     if script_id == "all":
        message += scripts.stop_all()
     else: 
        message += scripts.stop_script(script_id)
   return message


@app.route('/script/<name>/<loop>', methods=['GET'])
def start_script(name, loop):
   """GET to trigger the named script"""
   if request.method == 'GET':
     message = ""
     message += scripts.run_script(name, loop)
   return message


#############################
# Audio API calls
#

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
   """GET to trigger the given sound"""
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
   """GET to play a random sound of a given type"""
   if request.method == 'GET':
      r2audio.TriggerRandomSound(name) 
   return "Ok"

@app.route('/audio/volume', methods=['GET'])
def get_volume():
   if request.method == 'GET':
     message = ""
     message += r2audio.ShowVolume()
   return message

@app.route('/audio/volume/<level>', methods=['GET'])
def set_volume(level):
   if request.method == 'GET':
     message = ""
     message += r2audio.SetVolume(level)
   return message

@app.route('/shutdown/now', methods=['GET'])
def shutdown():
   if request.method == 'GET':
     os.system('shutdown now -h')
   return "Shutting down"

@app.route('/status', methods=['GET'])
def status():
   if request.method == 'GET':
     message = system_status()
   return message


if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True, use_reloader=False)
