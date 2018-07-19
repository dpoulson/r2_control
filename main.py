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
import requests
sys.path.append("./classes/")
from flask import Flask, request, render_template
from datetime import timedelta

from config import mainconfig

modules = mainconfig['modules'].split(",")
plugins = mainconfig['plugins'].split(",")
i2c_bus = mainconfig['busid']
logtofile = mainconfig['logtofile']
logdir = mainconfig['logdir']
logfile = mainconfig['logfile']

config = ConfigParser.RawConfigParser()
config.read('config/main.cfg')

plugin_names = {
        'flthy':'FlthyHPControl',
        'scripts':'ScriptControl',
        'audio':'AudioLibrary',
        'vader':'VaderPSIControl'
        }

def check_internet():
    try:
        host = socket.gethostbyname("www.google.com")
        s = socket.create_connection((host, 80), 2)
        internet_connection = True
    except:
        internet_connection = False
    return internet_connection


def send_telegram(message):
    global internet_connection
    if check_internet():
        try:
    	    send_message = 'https://api.telegram.org/bot' + config.get('telegram', 'token') + '/sendMessage?chat_id=' + config.get('telegram', 'chat_id') + '&parse_mode=Markdown&text=' + message
    	    requests.get(send_message)
	except:
	    if __debug__:
	       print "Thought we had an internet connection, but sending Telegram failed"
    else:
	if __debug__:
		print "Tried to send Telegram, but no internet connection"


def system_status():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = str(timedelta(seconds=uptime_seconds))
    try:
        with open('/sys/class/power_supply/sony_controller_battery_00:19:c1:5f:78:b9/capacity', 'r') as b:
                remote_battery = int(b.readline().split()[0])
    except:
        remote_battery = 0
    status = "Current Status\n"
    status += "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n"
    status += "Uptime: \t%s\n" % uptime_string
    status += "Main Battery: \t%5.3f (balance: %5.3f)\n" % (monitor.queryBattery(), monitor.queryBatteryBalance())
    status += "Remote Battery: %s%%\t\n" % remote_battery
    status += "Wifi: \t\t\n"
    status += "Internet: \t%s \n" % check_internet()
    status += "Location: \t\n"
    status += "Volume: \t%s\n" % p.audio.ShowVolume()
    status += "--------------\n"
    status += "Scripts Running:\n"
    #status += scripts.list_running()
    return status

# If logtofile is set, open log file
if logtofile:
    if __debug__:
        print "Opening log file: Dir: %s - Filename: %s" % (logdir, logfile)
    f = open(logdir + '/' + logfile, 'at')
    f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : ****** r2_control started ******\n")
    f.flush


######################################
# initialise modules

# Initialise server controllers
if "body" in modules:
    from ServoControl import ServoControl
    pwm_body = ServoControl(int(config.get('body', 'address'), 16), config.get('body', 'config_file'))
if "dome" in modules:
    from ServoControl import ServoControl
    pwm_dome = ServoControl(int(config.get('dome', 'address'), 16), config.get('dome', 'config_file'))

# Monitoring
if "monitoring" in modules:
    from i2cMonitor import i2cMonitor
    monitor = i2cMonitor(int(config.get('monitoring', 'address'), 16), float(config.get('monitoring', 'interval')))

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

for x in plugins:
    p = __import__(plugin_names[x], fromlist=[ x, 'api'])
    app.register_blueprint(p.api)
    

#######################
# System API calls
@app.route('/shutdown/now', methods=['GET'])
def shutdown():
    """GET to shutdown Raspberry Pi"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : ****** Shutting down ****** \n")
    if "telegram" in modules:
	send_telegram("Night night...")
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

@app.route('/sendstatus', methods=['GET'])
def sendstatus():
    """GET to send system status via telegram"""
    message = ""
    if request.method == 'GET':
        if "telegram" in modules:
            send_telegram(system_status())
            message = "Sent"
        else:
	    message = "Telegram module not configured"
    return message

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=__debug__, use_reloader=False)


