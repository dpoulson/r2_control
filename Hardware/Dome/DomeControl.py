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
from SabertoothPacketSerial import SabertoothPacketSerial
standard_library.install_aliases()
from builtins import str
from builtins import object


_configfile = mainconfig.mainconfig['config_dir'] + 'dome.cfg'

_config = configparser.SafeConfigParser({'address': '0x1c', 'logfile': 'dome.log',
                                         'dome_address': '129', 'port': '/dev/ttyUSB0', 'type': 'Syren'})
_config.read(_configfile)

if not os.path.isfile(_configfile):
    print("Config file does not exist")
    with open(_configfile, 'wt') as configfile:
        _config.write(configfile)

_defaults = _config.defaults()

_logdir = mainconfig.mainconfig['logdir']
_logfile = _defaults['logfile']

api = Blueprint('dome', __name__, url_prefix='/dome')
''' clamp - clamp a value between a min and max '''


def clamp(n, minn, maxn):
    if n < minn:
        if __debug__:
            print("Clamping min")
        return minn
    elif n > maxn:
        if __debug__:
            print("Clamping max " + str(n))
        return maxn
    else:
        return n


@api.route('/center', methods=['GET'])
def _dome_center():
    """ GET to set the dome to face forward"""
    message = ""
    if request.method == 'GET':
        message += _dome.position(0)
    return message


@api.route('/position/<degrees>', methods=['GET'])
def _dome_position(degrees):
    """ GET to set the dome to face a certain way"""
    message = ""
    if request.method == 'GET':
        message += _dome.position(degrees)
    return message


@api.route('/turn/<stick>', methods=['GET'])
def _dome_turn(stick):
    """ GET to set the dome turning"""
    message = ""
    if request.method == 'GET':
        message += _dome.turn(stick)
    return message


class _DomeControl(object):

    def __init__(self, address, logfile, dome_address, dome_type, dome_port):
        self.address = address
        self.bus = smbus.SMBus(int(mainconfig.mainconfig['busid']))
        self.logfile = logfile
        self.dome_serial = SabertoothPacketSerial(address=int(dome_address),
                                                  type=dome_type, port=dome_port)
        if __debug__:
            print("Initialising Dome Control")

    def _read_position(self):
        """ Read the dome position"""
        return "Ok"

    def position(self, position):
        return "Ok"

    def turn(self, stick):
        """ Turns the dome depending on the value of stick """
        self.dome_serial.driveCommand(clamp(stick, -0.99, 0.99))
        return "Ok"


_dome = _DomeControl(address=_defaults['address'], logfile=_defaults['logfile'],
                     dome_address=_defaults['dome_address'], dome_type=_defaults['type'],
                     dome_port=_defaults['port'])

