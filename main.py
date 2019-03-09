#!/usr/bin/python
""" Main script for R2_Control """
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
from __future__ import print_function
import os
import time
import datetime
from future import standard_library
from flask import Flask, request, render_template
from r2utils import telegram, internet, mainconfig
standard_library.install_aliases()
from builtins import str
from configparser import ConfigParser


modules = mainconfig.mainconfig['modules'].split(",")
plugins = mainconfig.mainconfig['plugins'].split(",")
i2c_bus = mainconfig.mainconfig['busid']
logtofile = mainconfig.mainconfig['logtofile']
logdir = mainconfig.mainconfig['logdir']
logfile = mainconfig.mainconfig['logfile']

config = ConfigParser({'busid': '1', 'logfile': 'test.log', 'logdir': './logs',
                       'logtofile': True, 'modules': 'dome', 'plugins': 'Audio'})
config.read('config/main.cfg')

plugin_names = {
    'flthy': 'Lights.FlthyHPControl',
    'rseries': 'Lights.RSeriesLogicEngine',
    'psi_matrix': 'Lights.PSI_Matrix',
    'Scripts': 'Scripts',
    'Audio': 'Audio',
    'vader': 'Lights.VaderPSIControl',
    'teecees': 'Lights.TeeceesControl',
    'Dome': 'Dome',
    'GPIO': 'GPIO',
    'Smoke': 'Smoke'}


def list_joysticks():
    """ Returns a list of joysticks available """
    path = "controllers"
    result = []
    for root, dirs, files in os.walk(path):
        if ".isjoystick" in files:
            result.append(root.replace(path + "/", ''))
    return result


def system_status():
    """ Collects the system status and returns a formatted message """
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = str(datetime.timedelta(seconds=uptime_seconds))
    try:
        with open('/sys/class/power_supply/sony_controller_battery_00:19:c1:5f:78:b9/capacity',
                  'r') as b:
            remote_battery = int(b.readline().split()[0])
    except:
        remote_battery = 0

    status = "Current Status\n"
    status += "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n"
    status += "Uptime: \t%s\n" % uptime_string
    if "monitor" in modules:
        status += "Main Battery: \t%5.3f (balance: %5.3f)\n" % (monitor.queryBattery(),
                                                                monitor.queryBatteryBalance())
    status += "Remote Battery: %s%%\t\n" % remote_battery
    status += "Wifi: \t\t\n"
    status += "Internet: \t%s \n" % internet.check()
    status += "Location: \t\n"
    status += "Volume: \t%s\n" % p['audio'].audio.ShowVolume()
    status += "--------------\n"
    status += "Scripts Running:\n"
    status += p['scripts'].scripts.list_running()
    return status


# If logtofile is set, open log file
if logtofile:
    if __debug__:
        print("Opening log file: Dir: %s - Filename: %s" % (logdir, logfile))
    f = open(logdir + '/' + logfile, 'at')
    f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
            " : ****** r2_control started ******\n")
    f.flush


######################################
# initialise modules

# Initialise server controllers
if "body" in modules:
    from Hardware.Servo import ServoControl
    pwm_body = ServoControl.ServoControl(int(config.get('body', 'address'), 16),
                                         config.get('body', 'config_file'))
if "dome" in modules:
    from Hardware.Servo import ServoControl
    pwm_dome = ServoControl.ServoControl(int(config.get('dome', 'address'), 16),
                                         config.get('dome', 'config_file'))

# Monitoring
if "monitoring" in modules:
    from Hardware.Monitoring import i2cMonitor
    monitor = i2cMonitor.i2cMonitor(int(config.get('monitoring', 'address'), 16),
                                    float(config.get('monitoring', 'interval')))

app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    """GET to generate a list of endpoints and their docstrings"""
    urls = dict([(r.rule, app.view_functions.get(r.endpoint).__doc__)
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
        print("Listing servos")
    if request.method == 'GET':
        message += pwm_body.list_servos()
        message += pwm_dome.list_servos()
    return message


@app.route('/servo/dome/list', methods=['GET'])
def servo_list_dome():
    """GET to list all current servos and position"""
    message = ""
    if __debug__:
        print("Listing servos")
    if request.method == 'GET':
        message += pwm_dome.list_servos()
    return message


@app.route('/servo/body/list', methods=['GET'])
def servo_list_body():
    """GET to list all current servos and position"""
    message = ""
    if __debug__:
        print("Listing servos")
    if request.method == 'GET':
        message += pwm_body.list_servos()
    return message


@app.route('/servo/<part>/<servo_name>/<servo_position>/<servo_duration>', methods=['GET'])
def servo_move(part, servo_name, servo_position, servo_duration):
    """GET will move a selected servo to the required position over a set duration"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                " : Servo move: " + servo_name + "," + servo_position +
                "," + servo_duration + "\n")
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
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                " : Servo close: \n")
    if request.method == 'GET':
        pwm_body.close_all_servos(0)
        pwm_dome.close_all_servos(0)
        return "Ok"
    return "Fail"


@app.route('/servo/dome/close', methods=['GET'])
def servo_dome_close():
    """GET to close all dome servos"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                " : Servo close dome: \n")
    if request.method == 'GET':
        pwm_dome.close_all_servos(0)
        return "Ok"
    return "Fail"


@app.route('/servo/dome/close/<duration>', methods=['GET'])
def servo_dome_close_slow(duration):
    """GET to close all dome servos slowly"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                " : Servo close dome slow: \n")
    if request.method == 'GET':
        pwm_dome.close_all_servos(duration)
        return "Ok"
    return "Fail"


@app.route('/servo/body/close', methods=['GET'])
def servo_body_close():
    """GET to close all body servos"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                " : Servo close body: \n")
    if request.method == 'GET':
        pwm_body.close_all_servos(0)
        return "Ok"
    return "Fail"


@app.route('/servo/body/close/<duration>', methods=['GET'])
def servo_body_close_slow(duration):
    """GET to close all body servos slowly"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                " : Servo close body slow:\n")
    if request.method == 'GET':
        pwm_body.close_all_servos(duration)
        return "Ok"
    return "Fail"


@app.route('/servo/open', methods=['GET'])
def servo_open():
    """GET to open all servos"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                " : Servo open: \n")
    if request.method == 'GET':
        pwm_body.open_all_servos(0)
        pwm_dome.open_all_servos(0)
        return "Ok"
    return "Fail"


@app.route('/servo/dome/open', methods=['GET'])
def servo_dome_open():
    """GET to open all dome servos"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                " : Servo open dome: \n")
    if request.method == 'GET':
        pwm_dome.open_all_servos(0)
        return "Ok"
    return "Fail"


@app.route('/servo/dome/open/<duration>', methods=['GET'])
def servo_dome_open_slow(duration):
    """GET to open all dome servos slowly"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                " : Servo open dome slow: \n")
    if request.method == 'GET':
        pwm_dome.open_all_servos(duration)
        return "Ok"
    return "Fail"


@app.route('/servo/body/open', methods=['GET'])
def servo_body_open():
    """GET to open all body servos"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                " : Servo open body: \n")
    if request.method == 'GET':
        pwm_body.open_all_servos(0)
        return "Ok"
    return "Fail"


@app.route('/servo/body/open/<duration>', methods=['GET'])
def servo_body_open_slow(duration):
    """GET to open all body servos" slowly """
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                " : Servo open body slow: \n")
    if request.method == 'GET':
        pwm_body.open_all_servos(duration)
        return "Ok"
    return "Fail"


p = {}
for x in plugins:
    if __debug__:
        print("Loading %s" % x)
    p[x] = __import__("Hardware." + plugin_names[x], fromlist=[str(x), 'api'])
    app.register_blueprint(p[x].api)

if __debug__:
    print("Modules loaded:")
    print("============================================")
    print(p)
    print("============================================")


#######################
# System API calls
@app.route('/joystick', methods=['GET'])
@app.route('/joystick/list', methods=['GET'])
def joystick_list():
    """GET to display list of possible joysticks"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                " : Retrieving list of joysticks\n")
    if request.method == 'GET':
        return '\n'.join(list_joysticks())
    return "Fail"


@app.route('/joystick/current', methods=['GET'])
def joystick_current():
    """GET to display current joystick"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                " : Retrieving current joystick\n")
    if request.method == 'GET':
        with open("controllers/.current", "r") as current_joy:
            current = current_joy.read()
        return current
    return "Fail"


@app.route('/joystick/<stick>', methods=['GET'])
def joystick_change(stick):
    """GET to change joystick to <stick> """
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                " : Changing joystick to " + stick + "\n")
    if request.method == 'GET':
        message = "Invalid stick"
        for valid in list_joysticks():
            if __debug__:
                print("Checking controller type is valid: " + valid)
            if valid == stick:
                if __debug__:
                    print("Valid stick")
                message = "Valid stick. Changed to " + stick
                with open("controllers/.current", "w") as current_joy:
                    current_joy.write(stick)
                if "telegram" in modules:
                    telegram.send("Setting joystick to " + stick)
                print("End of loop")
    return message


@app.route('/shutdown/now', methods=['GET'])
def shutdown():
    """GET to shutdown Raspberry Pi"""
    if logtofile:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                " : ****** Shutting down ****** \n")
    if "telegram" in modules:
        telegram.send("Night night...")
    if request.method == 'GET':
        os.system('shutdown now -h')
        s = open("controllers/.shutdown", "w+")
        s.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        s.flush()
        s.close()
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
            telegram.send(system_status())
            message = "Sent"
        else:
            message = "Telegram module not configured"
    return message


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=__debug__, use_reloader=False, threaded=True)
