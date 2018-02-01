#!/usr/bin/python
# ===============================================================================
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
# ===============================================================================

import ConfigParser
import os
import sys
import time
import datetime
import socket
sys.path.append("./classes/")
from flask import Flask, request, render_template
from datetime import timedelta
from i2cMonitor import i2cMonitor
from ServoControl import ServoControl
from ScriptControl import ScriptControl
from AudioLibrary import AudioLibrary

config = ConfigParser.RawConfigParser()
config.read('config/main.cfg')

modules = config.sections()
i2c_bus = config.getint('DEFAULT', 'busid')
logtofile = config.getboolean('DEFAULT', 'logtofile')
logdir = config.get('DEFAULT', 'logdir')
logfile = config.get('DEFAULT', 'logfile')

devices_list = []

######################################
# initialise modules

# Initialise server controllers
if "body" in modules:
    pwm_body = ServoControl(int(config.get('body', 'address'), 16), config.get('body', 'config_file'))
if "dome" in modules:
    pwm_dome = ServoControl(int(config.get('dome', 'address'), 16), config.get('dome', 'config_file'))

# Lighting systems
if "teecees" in modules:
    print "Adding TeeCees"
if "rseries" in modules:
    print "Adding Rseries"
if "flthy" in modules:
    print "Adding Flthy"

# Initialise Audio
if "audio" in modules:
    r2audio = AudioLibrary(config.get('audio', 'sounds_dir'), config.get('audio', 'volume'))

# Initialise script object
if "scripts" in modules:
    scripts = ScriptControl(config.get('scripts', 'script_dir'))

# Monitoring
if "monitoring" in modules:
    monitor = i2cMonitor(int(config.get('monitoring', 'address'), 16), float(config.get('monitoring', 'interval')),
                         logdir)

####
# If logtofile is set, open log file
if logtofile:
    if __debug__:
        print "Opening log file: Dir: %s - Filename: %s" % (logdir, logfile)
    f = open(logdir + '/' + logfile, 'at')
    f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : ****** r2_control started ******\n")
    f.flush

def system_status():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = str(timedelta(seconds=uptime_seconds))
    with open('/sys/class/power_supply/sony_controller_battery_00:19:c1:5f:78:b9/capacity', 'r') as b:
        remote_battery = int(b.readline().split()[0])
    try:
        host = socket.gethostbyname("www.google.com")
        s = socket.create_connection((host, 80), 2)
        internet_connection = True
    except:
        internet_connection = False
    status = "Current Status\n"
    status += "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n"
    status += "Uptime: \t%s\n" % uptime_string
    status += "Main Battery: \t%5.3f (balance: %5.3f)\n" % (monitor.queryBattery(), monitor.queryBatteryBalance())
    status += "Remote Battery: %s%%\t\n" % remote_battery
    status += "Wifi: \t\t\n"
    status += "Internet: \t%s \n" % internet_connection
    status += "Location: \t\n"
    status += "Volume: \t%s\n" % r2audio.ShowVolume()
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
# Servo API calls
#

@app.route('/servo/', methods=['GET'])
@app.route('/servo/list', methods=['GET'])
def servo_list():
    """GET to list all current servos and position"""
    message = ""
    if __debug__:
        print "Listing servos"
    if request.method == 'GET':
        message += pwm_body.list_servos()
        message += pwm_dome.list_servos()
    return message


@app.route('/servo/dome/list', methods=['GET'])
def servo_list_dome():
    """GET to list all current servos and position"""
    message = ""
    if __debug__:
        print "Listing servos"
    if request.method == 'GET':
        message += pwm_dome.list_servos()
    return message


@app.route('/servo/body/list', methods=['GET'])
def servo_list_body():
    """GET to list all current servos and position"""
    message = ""
    if __debug__:
        print "Listing servos"
    if request.method == 'GET':
        message += pwm_body.list_servos()
    return message


@app.route('/servo/<part>/<servo_name>/<servo_position>/<servo_duration>', methods=['GET'])
def servo_move(part, servo_name, servo_position, servo_duration):
    """GET will move a selected servo to the required position over a set duration"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Servo move: " + servo_name + "," + servo_position + "," + servo_duration + "\n")
    if request.method == 'GET':
        if part == 'body':
            pwm_body.servo_command(servo_name, servo_position, servo_duration)
        if part == 'dome':
            pwm_dome.servo_command(servo_name, servo_position, servo_duration)
    return "Ok"


@app.route('/servo/close', methods=['GET'])
def servo_close():
    """GET to close all servos"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Servo close: \n")
    if request.method == 'GET':
        pwm_body.close_all_servos()
        pwm_dome.close_all_servos()
        return "Ok"


@app.route('/servo/dome/close', methods=['GET'])
def servo_dome_close():
    """GET to close all dome servos"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Servo close dome: \n")
    if request.method == 'GET':
        pwm_dome.close_all_servos()
        return "Ok"


@app.route('/servo/body/close', methods=['GET'])
def servo_body_close():
    """GET to close all body servos"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Servo close body: \n")
    if request.method == 'GET':
        pwm_body.close_all_servos()
        return "Ok"


@app.route('/servo/open', methods=['GET'])
def servo_open():
    """GET to open all servos"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Servo open: \n")
    if request.method == 'GET':
        pwm_body.open_all_servos()
        pwm_dome.open_all_servos()
        return "Ok"


@app.route('/servo/dome/open', methods=['GET'])
def servo_dome_open():
    """GET to open all dome servos"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Servo open dome: \n")
    if request.method == 'GET':
        pwm_dome.open_all_servos()
        return "Ok"


@app.route('/servo/body/open', methods=['GET'])
def servo_body_open():
    """GET to open all body servos"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Servo open body: \n")
    if request.method == 'GET':
        pwm_body.open_all_servos()
        return "Ok"


#############################
# Script API calls
#

@app.route('/script/', methods=['GET'])
@app.route('/script/list', methods=['GET'])
def script_list():
    """GET gives a comma separated list of available scripts"""
    message = ""
    if request.method == 'GET':
        message += scripts.list()
    return message


@app.route('/script/running', methods=['GET'])
def running_scripts():
    """GET a list of all running scripts and their ID"""
    message = ""
    if request.method == 'GET':
        message += scripts.list_running()
    return message


@app.route('/script/stop/<script_id>', methods=['GET'])
def stop_script(script_id):
    """GET a script ID to stop that script"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Script stop: " + script_id + "\n")
    message = ""
    if request.method == 'GET':
        if script_id == "all":
            message += scripts.stop_all()
        else:
            message += scripts.stop_script(script_id)
    return message


@app.route('/script/<name>/<loop>', methods=['GET'])
def start_script(name, loop):
    """GET to trigger the named script"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Script loop: " + name + "," + loop + "\n")
    message = ""
    if request.method == 'GET':
        message += scripts.run_script(name, loop)
    return message


#############################
# Audio API calls
#

@app.route('/audio/', methods=['GET'])
@app.route('/audio/list', methods=['GET'])
def audio_list():
    """GET gives a comma separated list of available sounds"""
    message = ""
    if request.method == 'GET':
        message += r2audio.ListSounds()
    return message


@app.route('/audio/<name>', methods=['GET'])
def audio(name):
    """GET to trigger the given sound"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Sound : " + name + "\n")
    if request.method == 'GET':
        r2audio.TriggerSound(name)
    return "Ok"


@app.route('/audio/random/', methods=['GET'])
@app.route('/audio/random/list', methods=['GET'])
def random_audio_list():
    """GET returns types of sounds available at random"""
    message = ""
    if request.method == 'GET':
        message += r2audio.ListRandomSounds()
    return message


@app.route('/audio/random/<name>', methods=['GET'])
def random_audio(name):
    """GET to play a random sound of a given type"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Sound random: " + name + "\n")
    if request.method == 'GET':
        r2audio.TriggerRandomSound(name)
    return "Ok"


@app.route('/audio/volume', methods=['GET'])
def get_volume():
    """GET returns current volume level"""
    message = ""
    if request.method == 'GET':
        message += r2audio.ShowVolume()
    return message


@app.route('/audio/volume/<level>', methods=['GET'])
def set_volume(level):
    """GET to set a specific volume level"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Volume set : " + level + "\n")
    message = ""
    if request.method == 'GET':
        message += r2audio.SetVolume(level)
    return message


@app.route('/shutdown/now', methods=['GET'])
def shutdown():
    """GET to shutdown Raspberry Pi"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : ****** Shutting down ****** \n")
    if request.method == 'GET':
        os.system('shutdown now -h')
    return "Shutting down"


@app.route('/status', methods=['GET'])
def sysstatus():
    """GET to display system status"""
    message = ""
    if request.method == 'GET':
        message = system_status()
    return message


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, use_reloader=False)


