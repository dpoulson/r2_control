from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
import configparser
import smbus
import os
import datetime
import time
from r2utils import mainconfig
from flask import Blueprint, request
standard_library.install_aliases()
from builtins import hex
from builtins import object


_configfile = mainconfig.mainconfig['config_dir'] + 'smoke.cfg'

_config = configparser.SafeConfigParser({'address': '0x05', 'logfile': 'smoke.log'})
_config.read(_configfile)

if not os.path.isfile(_configfile):
    print("Config file does not exist")
    with open(_configfile, 'wt') as configfile:
        _config.write(configfile)

_defaults = _config.defaults()

_logdir = mainconfig.mainconfig['logdir']
_logfile = _defaults['logfile']

api = Blueprint('smoke', __name__, url_prefix='/smoke')


@api.route('/on', methods=['GET'])
def _smoke_on():
    """ GET to send a command to the smoke system"""
    message = ""
    if request.method == 'GET':
        message += _smoke.sendRaw('S', '5')
    return message


@api.route('/on/<duration>', methods=['GET'])
def _smoke_on_duration(duration):
    """ GET to turn smoke on for a duration """
    message = ""
    if request.method == 'GET':
        message += _smoke.sendRaw('S', duration)
    return message


class _SmokeControl(object):

    def __init__(self, address, logdir):
        self.address = address
        self.bus = smbus.SMBus(int(mainconfig.mainconfig['busid']))
        self.logdir = logdir
        if __debug__:
            print("Initialising Smoke Control")

    def sendRaw(self, cmd, duration):
        command = int(hex(ord(cmd)),16)
        hexDuration = list()
        if __debug__:
            print("Duration: %s" % duration)
        # We don't want to run for longer than 10 seconds, might burn out the coil 
        if int(duration) > 9:
            if __debug__:
               print("Too long, shortening duration")
            duration = '9'
        hexDuration.append(int(duration,16))
        if __debug__:
            print("Command: %s | hexDuration: %s " % (command, hexDuration))
        try:
            self.bus.write_i2c_block_data(int(self.address,16), command, hexDuration)
        except:
            print("Failed to send bytes")
        return "Ok"


_smoke = _SmokeControl(_defaults['address'], _defaults['logfile'])

