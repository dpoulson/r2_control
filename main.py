#!/usr/bin/python3
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
import glob
import os
import time
import datetime
import logging
import logging.handlers
from future import standard_library
from flask import Flask, request, render_template
from r2utils import telegram, internet, mainconfig
standard_library.install_aliases()
from builtins import str
from configparser import ConfigParser

plugins = mainconfig.mainconfig['plugins'].split(",")
servos = mainconfig.mainconfig['servos'].split(",")
i2c_bus = mainconfig.mainconfig['busid']
logtofile = mainconfig.mainconfig['logtofile']
logdir = mainconfig.mainconfig['logdir']
logfile = mainconfig.mainconfig['logfile']


plugin_names = {
    'flthy': 'Lights.FlthyHPControl',
    'rseries': 'Lights.RSeriesLogicEngine',
    'Scripts': 'Scripts.ScriptControl',
    'Audio': 'Audio.AudioLibrary',
    'Vocalizer': 'Audio.Vocalizer',
    'vader': 'Lights.VaderPSIControl',
    'teecees': 'Lights.TeeceesControl',
    'Dome': 'Dome',
    'GPIO': 'GPIO.GPIOControl',
    'Smoke': 'Smoke',
    'Monitoring': 'Monitoring'}


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
    remote_battery = ""
    try:
        controllers = glob.glob('/sys/class/power_supply/*')
        if __debug__:
            print("Controllers: %s" % controllers)
        for controller in controllers: 
            path = controller + "/capacity"
            if __debug__:
                print("Controller path: %s" % path)
            with open(path,'r') as b:
                remote_battery += str(int(b.readline().split()[0])) + " "
                if __debug__:
                    print("Remote battery: %s" % remote_battery)
    except:
        remote_battery = ""

    status = "Current Status\n"
    status += "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n"
    status += "Uptime: \t%s\n" % uptime_string
    if "Monitoring" in plugins:
        status += "Main Battery: \t%5.3f (balance: %5.3f)\n" % (p['Monitoring'].monitoring.queryBattery(),
                                                                p['Monitoring'].monitoring.queryBatteryBalance())
    status += "Remote Battery: %s%%\t\n" % remote_battery
    status += "Wifi: \t\t\n"
    status += "Internet: \t%s \n" % internet.check()
    status += "Location: \t\n"
    status += "Volume: \t%s\n" % p['Audio'].audio.ShowVolume()
    status += "--------------\n"
    status += "Scripts Running:\n"
    status += p['Scripts'].scripts.list_running()
    return status

def system_status_csv():
    """ Collects the system status and returns a csv string """
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = str(datetime.timedelta(seconds=uptime_seconds))
    try:
        with open('/sys/class/power_supply/sony_controller_battery_00:19:c1:5f:78:b9/capacity',
                  'r') as b:
            remote_battery = int(b.readline().split()[0])
    except:
        remote_battery = 0

    battery = 0
    batteryBalance = 0
    if "Monitoring" in plugins:
        battery = p['Monitoring'].monitoring.queryBattery()
        batteryBalance = p['Monitoring'].monitoring.queryBatteryBalance()

    status = "%s,%s,%s,%s,%s,%s" % (uptime_string, battery, batteryBalance, remote_battery, internet.check(), p['Audio'].audio.ShowVolume())
    return status

# Setup logging
log_filename = logdir + '/' + logfile
# Create target Directory if don't exist
if not os.path.exists(logdir):
    os.mkdir(logdir)
    print("Creating logdir " + logdir)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=log_filename,
                    filemode='w')
logging.info("**** Starting r2_control")


######################################
# initialise modules
print(mainconfig.mainconfig['telegram'])
if mainconfig.mainconfig['telegram'] == "True":
    # Enable telegram
    if __debug__:
        print("Enabled Telegram")
    tg = telegram.Telegram()
    if __debug__: 
        print(tg)
    tg.send("R2 Starting up....")
    
app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    """GET to generate a list of endpoints and their docstrings"""
    urls = dict([(r.rule, app.view_functions.get(r.endpoint).__doc__)
                 for r in app.url_map.iter_rules()
                 if not r.rule.startswith('/static')])
    return render_template('index.html', urls=urls)


# Initialise server controllers
from Hardware.Servo import ServoBlueprint
from Hardware.Servo import ServoControl
if __debug__:
    print("Servos loading.... %s" % servos)
for x in servos:
    if x != '':
        logging.info("Loading Servo Control Board: %s" % x)
        app.register_blueprint(ServoBlueprint.construct_blueprint(x), url_prefix="/" + x)
    
p = {}
for x in plugins:
    logging.info("Loading %s" % x)
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
    logging.info("Retrieving list of joysticks")
    if request.method == 'GET':
        return '\n'.join(list_joysticks())
    return "Fail"


@app.route('/joystick/current', methods=['GET'])
def joystick_current():
    """GET to display current joystick"""
    logging.info("Retrieving current joystick")
    if request.method == 'GET':
        with open("controllers/.current", "r") as current_joy:
            current = current_joy.read()
        return current
    return "Fail"


@app.route('/joystick/<stick>', methods=['GET'])
def joystick_change(stick):
    """GET to change joystick to <stick> """
    logging.info("Changing joystick to " + stick)
    if request.method == 'GET':
        message = "Invalid stick"
        for valid in list_joysticks():
            logging.info("Checking controller type is valid: " + valid)
            if valid == stick:
                message = "Valid stick. Changed to " + stick
                with open("controllers/.current", "w") as current_joy:
                    current_joy.write(stick)
                if "telegram" in modules:
                    telegram.send("Setting joystick to " + stick)
    return message


@app.route('/shutdown/now', methods=['GET'])
def shutdown():
    """GET to shutdown Raspberry Pi"""
    logging.info("****** Shutting down ******")
    if mainconfig.mainconfig['telegram']:
        tg.send("Night night...")
    if request.method == 'GET':
        os.system('shutdown now -h')
        s = open("/home/pi/.r2_config/.shutdown", "w+")
        s.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        s.flush()
        s.close()
    return "Shutting down"


@app.route('/status', methods=['GET'])
@app.route('/status/display', methods=['GET'])
def sysstatus():
    """GET to display system status"""
    message = ""
    if request.method == 'GET':
        message = system_status()
    return message


@app.route('/status/send', methods=['GET'])
def sendstatus():
    """GET to send system status via telegram"""
    message = ""
    if request.method == 'GET':
        if mainconfig.mainconfig['telegram']:
            tg.send(system_status())
            message = "Sent"
        else:
            message = "Telegram module not configured"
    return message


@app.route('/status/csv', methods=['GET'])
def sendstatuscsv():
    """GET to display a CSV of current stats"""
    message = ""
    if request.method == 'GET':
        message = system_status_csv()
    return message


@app.route('/internet', methods=['GET'])
def sendstatusinternet():
    """GET to display internet status"""
    message = ""
    if request.method == 'GET':
        if (internet.check()):
            message = "True"
        else:
            message = "False"
    return message


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=__debug__, use_reloader=False, threaded=True)
