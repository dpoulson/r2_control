from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
import configparser
import os
import serial
from r2utils import mainconfig
from flask import Blueprint, request
from builtins import object
standard_library.install_aliases()


_configfile = mainconfig.mainconfig['config_dir'] + 'vocalizer.cfg'

_config = configparser.SafeConfigParser({'logfile': 'vocalizer.log', 'port': '/dev/ttyUSB1', 'baudrate': '9600'})
_config.read(_configfile)

if not os.path.isfile(_configfile):
    print("Config file does not exist (Vocalizer)")
    with open(_configfile, 'wt') as configfile:
        _config.write(configfile)

_defaults = _config.defaults()

_logdir = mainconfig.mainconfig['logdir']
_logfile = _defaults['logfile']

api = Blueprint('vocalizer', __name__, url_prefix='/voc')


@api.route('/', methods=['GET'])
@api.route('/happy', methods=['GET'])
def _play_happy():
    """GET to play HAPPY sound"""
    message = ""
    if request.method == 'GET':
        vocalizer.TriggerSound('happy')
    return message


@api.route('/sad', methods=['GET'])
def _play_sad():
    """GET to play SAD sound"""
    message = ""
    if request.method == 'GET':
        vocalizer.TriggerSound('sad')
    return message


@api.route('/angry', methods=['GET'])
def _play_angry():
    """GET to play ANGRY sound"""
    message = ""
    if request.method == 'GET':
        vocalizer.TriggerSound('angry')
    return message


@api.route('/scared', methods=['GET'])
def _play_scared():
    """GET to play SCARED sound"""
    message = ""
    if request.method == 'GET':
        vocalizer.TriggerSound('scared')
    return message

@api.route('/muse', methods=['GET'])
def _play_muse():
    """GET to play SCARED sound"""
    message = ""
    if request.method == 'GET':
        vocalizer.TriggerSound('muse')
    return message

@api.route('/muse/<any(enable, disable):command', methods=['GET'])
def _play_muse(command):
    """GET to play SCARED sound"""
    message = ""
    if request.method == 'GET':
        vocalizer.ControlMuse(command)
    return message

@api.route('/muse/<any(mingap, maxgap):command>/<int:value>', methods=['GET'])
def _play_muse(command, value=0):
    """GET to play SCARED sound"""
    message = ""
    if request.method == 'GET':
        vocalizer.ControlMuse(command, value)
    return message

@api.route('/overload', methods=['GET'])
def _play_overload():
    """GET to play OVERLOAD sound"""
    message = ""
    if request.method == 'GET':
        vocalizer.TriggerSound('overload')
    return message


class _Vocalizer(object):
    """
    The class for playing audio using a Vocalizer from Human-Cyborg Relations embedded boards

    These boards allow unique sounds to be generated for a droid

    """

    _conn = None

    def __init__(self, port, baudrate):
        """
        Init of Vocalizer class

        Parameters
        ----------
        port : str
             Port the vocalizer board is on
        """

        if __debug__:
            print("Initiating vocalizer")
        try:
            self._conn = serial.Serial(port, baudrate=baudrate)
        except Exception:
            print("Failed to open serial port %s" % port)

    def TriggerSound(self, data):
        """
        Play a sound

        Parameters
        ----------
        data : str
             type of sound to generate (happy, sad, angry, scared, or overload)
        """
        code = None
        if __debug__:
            print("Playing %s" % data)

        if data == "happy":
            code = "SH0"
        elif data == "sad":
            code = "SS0"
        elif data == "angry":
            code = "SM0"
        elif data == "scared":
            code = "SC0"
        elif data == "overload":
            code = "SE"
        elif data == "muse":
            code = "MM"
        else:
            code = "PSV"

        try:
            self._conn.write(code)
        except Exception:
            print("Failed to send command to vocalizer")

        if __debug__:
            print("Command sent to vocalizer")
        
    def ControlMuse(self, command, value=0):
        """
        Control muse efects

        Parameters
        ----------
        data : str
             type of sound to generate (happy, sad, angry, scared, or overload)
        """
        code = None
        if __debug__:
            print("Muse:  %s" % command)

        if command == "enable":
            code = "M1"
        elif data == "disable":
            code = "M0"
        elif data == "toggle":
            code = "MT"
        elif data == "mingap":
            code = "MN" + value
        elif data == "maxgap":
            code = "MX" + value
        else:
            code = "PSV"

        try:
            self._conn.write(code)
        except Exception:
            print("Failed to send command to vocalizer")

        if __debug__:
            print("Command sent to vocalizer")


vocalizer = _Vocalizer(_defaults['port'], _defaults['baudrate'])
