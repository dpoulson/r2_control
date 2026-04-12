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
from builtins import str
import glob
import os
import time
import datetime
import logging
import logging.handlers
import importlib
from flask import Flask, request, render_template, jsonify
from r2utils import telegram, internet, mainconfig
from Hardware.Servo import ServoBlueprint

plugins = mainconfig.mainconfig['plugins'].split(",")
servos = mainconfig.mainconfig['servos'].split(",")
i2c_bus = mainconfig.mainconfig['busid']
logtofile = mainconfig.mainconfig['logtofile']
logdir = mainconfig.mainconfig['logdir']
logfile = mainconfig.mainconfig['logfile']
configdir = mainconfig.mainconfig['config_dir']


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
    with open('/proc/uptime', 'r', encoding="utf-8") as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = str(datetime.timedelta(seconds=uptime_seconds))
    remote_battery = ""
    try:
        controllers = glob.glob('/sys/class/power_supply/*')
        logging.debug(f"Controllers: {controllers}")
        for controller in controllers:
            path = controller + "/capacity"
            logging.debug(f"Controller path: {path}")
            with open(path, 'r', encoding="utf-8") as b:
                remote_battery += str(int(b.readline().split()[0])) + " "
                logging.debug(f"Remote battery: {remote_battery}")
    except Exception as e:
        logging.error(f"Error getting remote battery: {e}")
        remote_battery = ""

    status = "Current Status\n"
    status += "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n"
    status += f"Uptime: \t{uptime_string}\n"
    if "Monitoring" in plugins:
        status += "Main Battery: \t%5.3f (balance: %5.3f)\n" % (p['Monitoring'].monitoring.queryBattery(),
                                                                p['Monitoring'].monitoring.queryBatteryBalance())
    status += f"Remote Battery: {remote_battery}%\t\n"
    status += "Wifi: \t\t\n"
    status += f"Internet: \t{internet.check()} \n"
    status += "Location: \t\n"
    if "Audio" in plugins:
        status += f"Volume: \t{p['Audio'].audio.ShowVolume()}\n"
    status += "--------------\n"
    status += "Scripts Running:\n"
    if "Scripts" in plugins:
        status += p['Scripts'].scripts.list_running()
    return status


def system_status_csv():
    """ Collects the system status and returns a csv string """
    with open('/proc/uptime', 'r', encoding="utf-8") as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = str(datetime.timedelta(seconds=uptime_seconds))
    remote_battery = ""
    try:
        controllers = glob.glob('/sys/class/power_supply/*')
        logging.debug(f"Controllers: {controllers}")
        for controller in controllers:
            path = controller + "/capacity"
            logging.debug(f"Controller path: {path}")
            with open(path, 'r', encoding="utf-8") as b:
                remote_battery += str(int(b.readline().split()[0])) + " "
                logging.debug(f"Remote battery: {remote_battery}")
    except Exception as e:
        logging.error(f"Error getting remote battery: {e}")
        remote_battery = 0

    battery = 0
    batteryBalance = 0
    if "Monitoring" in plugins:
        battery = p['Monitoring'].monitoring.queryBattery()
        batteryBalance = p['Monitoring'].monitoring.queryBatteryBalance()

    status = f"{uptime_string},{battery},{batteryBalance},{remote_battery},{internet.check()},{p['Audio'].audio.ShowVolume()}"
    return status


# Setup logging
log_filename = logdir + '/' + logfile
# Create target Directory if don't exist
if not os.path.exists(logdir):
    os.mkdir(logdir)
    print(f"Creating logdir: {logdir}")
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=log_filename,
                    filemode=mainconfig.mainconfig.get('logmode', 'w'))
logging.info("**** Starting r2_control")


######################################
# initialise modules
if mainconfig.mainconfig['telegram'] == "True":
    # Enable telegram
    logging.info("Enabled Telegram")
    tg = telegram.Telegram()
    logging.info(tg)
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
logging.info(f"Servos loading.... {servos}")
for x in servos:
    if x != '':
        logging.info(f"Loading Servo Control Board: {x}")
        app.register_blueprint(ServoBlueprint.construct_blueprint(x), url_prefix="/" + x)

p = {}
for x in plugins:
    logging.info(f"Loading {x}")
    p[x] = __import__("Hardware." + plugin_names[x], fromlist=[str(x), 'api'])
    app.register_blueprint(p[x].api)

logging.info("Modules loaded:")
logging.info("============================================")
logging.info(p)
logging.info("============================================")


#######################
# System API calls
@app.route('/joystick', methods=['GET'])
@app.route('/joystick/list', methods=['GET'])
def joystick_list():
    """GET to display list of possible joysticks"""
    logging.info("Retrieving list of joysticks")
    return '\n'.join(list_joysticks())


@app.route('/joystick/current', methods=['GET'])
def joystick_current():
    """GET to display current joystick"""
    logging.info("Retrieving current joystick")
    with open("controllers/.current", "r", encoding="utf-8") as current_joy:
        current = current_joy.read()
    return current



@app.route('/joystick/<stick>', methods=['GET'])
def joystick_change(stick):
    """GET to change joystick to <stick> """
    logging.info("Changing joystick to " + stick)

    message = "Invalid stick"
    for valid in list_joysticks():
        logging.info("Checking controller type is valid: " + valid)
        if valid == stick:
            message = "Valid stick. Changed to " + stick
            with open("controllers/.current", "w", encoding="utf-8") as current_joy:
                current_joy.write(stick)
    return message


@app.route('/shutdown/now', methods=['GET'])
def shutdown():
    """GET to shutdown Raspberry Pi"""
    logging.info("****** Shutting down ******")
    if mainconfig.mainconfig['telegram']:
        tg.send("Night night...")
    os.system('shutdown now -h')
    with open(configdir + ".shutdown", "w", encoding="utf-8") as s:
        s.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        s.flush()
        s.close()
    return "Shutting down"


@app.route('/status', methods=['GET'])
@app.route('/status/display', methods=['GET'])
def sysstatus():
    """GET to display system status"""
    message = ""
    message = system_status()
    return message


@app.route('/status/send', methods=['GET'])
def sendstatus():
    """GET to send system status via telegram"""
    message = ""
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
    message = system_status_csv()
    return message


@app.route('/internet', methods=['GET'])
def sendstatusinternet():
    """GET to display internet status"""
    message = ""
    if internet.check():
        message = "True"
    else:
        message = "False"
    return message


@app.route('/config/get', methods=['GET'])
def get_config():
    """GET current system configuration"""
    import configparser
    def get_servo_addr(name):
        p = os.path.expanduser(f'~/.r2_config/servo_{name}.cfg')
        if os.path.exists(p):
            c = configparser.ConfigParser()
            c.read(p)
            return c.get('DEFAULT', 'address', fallback='')
        return ''

    config_data = {
        'plugins': mainconfig.mainconfig.get('plugins', ''),
        'servos': mainconfig.mainconfig.get('servos', ''),
        'drive_type': mainconfig._config.get('Drive', 'type', fallback=''),
        'drive_port': mainconfig._config.get('Drive', 'port', fallback=''),
        'dome_type': mainconfig._config.get('Dome', 'type', fallback=''),
        'dome_port': mainconfig._config.get('Dome', 'port', fallback=''),
        'available_ports': list(set(glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyAMA*') + glob.glob('/dev/serial*'))),
        'available_plugins': list(plugin_names.keys()),
        'servo_addresses': { s.strip(): get_servo_addr(s.strip()) for s in mainconfig.mainconfig.get('servos', '').split(',') if s.strip() }
    }
    
    plugin_configs = {}
    for p in mainconfig.mainconfig.get('plugins', '').split(','):
        p = p.strip().lower()
        if not p: continue
        cfg_path = os.path.expanduser(f'~/.r2_config/{p}.cfg')
        if os.path.exists(cfg_path):
            c = configparser.ConfigParser()
            c.read(cfg_path)
            p_dict = {}
            if c.defaults(): p_dict['DEFAULT'] = dict(c.defaults())
            for section in c.sections():
                p_dict[section] = dict(c.items(section))
            plugin_configs[p] = p_dict
    config_data['plugin_configs'] = plugin_configs

    return jsonify(config_data)


@app.route('/config/set', methods=['POST'])
def set_config():
    """POST to update configuration"""
    import threading
    import configparser
    
    data = request.form
    mainconfig.save_config(data)
    
    def set_servo_addr(name, val):
        if not val: return
        p = os.path.expanduser(f'~/.r2_config/servo_{name}.cfg')
        c = configparser.ConfigParser()
        if os.path.exists(p):
            c.read(p)
        c.set('DEFAULT', 'address', val)
        with open(p, 'w') as f:
            c.write(f)
            
    for key, val in data.items():
        if key.startswith('servo_addr_'):
            set_servo_addr(key[11:], val)
            
    plugin_updates = {}
    for key, val in data.items():
        if key.startswith('plugin_cfg__'):
            parts = key.split('__')
            if len(parts) == 4:
                _, p_name, section, p_key = parts
                if p_name not in plugin_updates:
                    plugin_updates[p_name] = {}
                if section not in plugin_updates[p_name]:
                    plugin_updates[p_name][section] = {}
                plugin_updates[p_name][section][p_key] = val
                
    for p_name, sections in plugin_updates.items():
        cfg_path = os.path.expanduser(f'~/.r2_config/{p_name}.cfg')
        c = configparser.ConfigParser()
        if os.path.exists(cfg_path):
            c.read(cfg_path)
        for section, keys in sections.items():
            if section != 'DEFAULT' and not c.has_section(section):
                c.add_section(section)
            for k, v in keys.items():
                c.set(section, k, v)
        with open(cfg_path, 'w') as f:
            c.write(f)
    
    def restart():
        import time
        time.sleep(1)
        os.system('systemctl restart r2_control.service')
        
    threading.Thread(target=restart).start()
    return "Ok"


if __name__ == '__main__':
    app.run(host='0.0.0.0', use_reloader=False, threaded=True)
