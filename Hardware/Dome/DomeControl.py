"""Module for doing some dome automation and position sensing"""
from builtins import str
from builtins import object
import configparser
import os
from future import standard_library
from flask import Blueprint, request
from r2utils import mainconfig
from .DomeThread import DomeThread
standard_library.install_aliases()


_configfile = mainconfig.mainconfig['config_dir'] + 'dome.cfg'

_config = configparser.SafeConfigParser({'address': '0x1c',
                                         'logfile': 'dome.log',
                                         'dome_address': '129',
                                         'port': '/dev/ttyUSB0',
                                         'type': 'Syren'})
_config.read(_configfile)

if not os.path.isfile(_configfile):
    print("Config file does not exist")
    with open(_configfile, 'wt', encoding="utf-8") as configfile:
        _config.write(configfile)

_defaults = _config.defaults()

_logdir = mainconfig.mainconfig['logdir']
_logfile = _defaults['logfile']

api = Blueprint('dome', __name__, url_prefix='/dome')
''' clamp - clamp a value between a min and max '''


def clamp(n, minn, maxn):
    """ Clamp value between two limits """
    if n < minn:
        if __debug__:
            print("Clamping min")
        return minn
    elif n > maxn:
        if __debug__:
            print(f"Clamping max {str(n)}")
        return maxn
    else:
        return n


@api.route('/center', methods=['GET'])
def _dome_center():
    """ GET to set the dome to face forward"""
    message = ""
    if request.method == 'GET':
        message += _dome.Position(0)
    return message


@api.route('/position', methods=['GET'])
def _dome_get_position():
    """ GET to retrieve current position"""
    message = ""
    if request.method == 'GET':
        message += _dome.GetPosition()
    return message


@api.route('/position/<degrees>', methods=['GET'])
def _dome_position(degrees):
    """ GET to set the dome to face a certain way"""
    message = ""
    if request.method == 'GET':
        message += _dome.Position(degrees)
    return message


@api.route('/turn/<stick>', methods=['GET'])
def _dome_turn(stick):
    """ GET to set the dome turning"""
    message = ""
    if request.method == 'GET':
        message += _dome.Turn(stick)
    return message


@api.route('/random/<value>', methods=['GET'])
def _dome_random(value):
    """ GET to set the dome random on/off"""
    message = ""
    if request.method == 'GET':
        message += _dome.Random(value)
    return message


@api.route('/random', methods=['GET'])
def _dome_random_status():
    """ GET to set the dome random status"""
    message = ""
    if request.method == 'GET':
        message += _dome.GetRandom()
    return message


class _DomeControl(object):

    def __init__(self):
        self.dome = DomeThread(129, "Syren", "/dev/ttyUSB0")
        self.dome.start()

    def _read_position(self):
        """ Read the dome position"""
        return "Ok"

    def Position(self, position):
        """ Set position of dome """
        self.dome.SetPosition(position)
        return "Ok"

    def Random(self, value):
        """ Set random position """
        self.dome.SetRandom(value)
        return "Ok"

    def GetRandom(self):
        """ Get random position """
        return self.dome.GetRandom()

    def GetPosition(self):
        """ Set current position """
        return self.dome.GetPosition()

    def Turn(self, stick):
        """ Turns the dome depending on the value of stick """
        self.dome_serial.driveCommand(clamp(stick, -0.99, 0.99))
        return "Ok"


_dome = _DomeControl()
