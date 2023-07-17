"""Module for talking to the Vocalizer board"""
from builtins import object
import configparser
import os
import serial
from flask import Blueprint, request
from future import standard_library
from r2utils import mainconfig
standard_library.install_aliases()


_configfile = mainconfig.mainconfig['config_dir'] + 'vocalizer.cfg'

_config = configparser.SafeConfigParser({'logfile': 'vocalizer.log', 'port': '/dev/ttyUSB1', 'baudrate': '9600'})
_config.read(_configfile)

if not os.path.isfile(_configfile):
    print("Config file does not exist (Vocalizer)")
    with open(_configfile, 'wt', encoding="utf-8") as configfile:
        _config.write(configfile)

_defaults = _config.defaults()

_logdir = mainconfig.mainconfig['logdir']
_logfile = _defaults['logfile']

api = Blueprint('vocalizer', __name__, url_prefix='/voc')


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
    """GET to play MUSE sound"""
    message = ""
    if request.method == 'GET':
        vocalizer.TriggerSound('muse')
    return message


@api.route('/muse/<any(enable, disable):command>', methods=['GET'])
def _play_muse_toggle(command):
    """GET to toggle MUSE effects"""
    message = ""
    if request.method == 'GET':
        vocalizer.ControlMuse(command)
    return message


@api.route('/muse/<any(mingap, maxgap):command>/<int:value>', methods=['GET'])
def _play_muse_timing(command, value=0):
    """GET to set min and max MUSE times"""
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
            print(f"Initiating vocalizer: {port} / {baudrate}")
        try:
            self._conn = serial.Serial(str(port), baudrate=int(baudrate))
        except Exception:
            print(f"Failed to open serial port {port}")

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
            print(f"Playing {data}")

        if data == "happy":
            code = "<SH0>"
        elif data == "sad":
            code = "<SS0>"
        elif data == "angry":
            code = "<SM0>"
        elif data == "scared":
            code = "<SC0>"
        elif data == "overload":
            code = "<SE>"
        elif data == "muse":
            code = "<MM>"
        else:
            code = "<PSV>"

        try:
            if __debug__:
                print(f"Sending: {code}")
            self._conn.write(code.encode())
        except Exception as e:
            print(f"Failed to send command to vocalizer: {e}")

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
            print(f"Muse: {command}")

        if command == "enable":
            code = "<M1>"
        elif command == "disable":
            code = "<M0>"
        elif command == "toggle":
            code = "<MT>"
        elif command == "mingap":
            code = "<MN" + value + ">"
        elif command == "maxgap":
            code = "<MX" + value +">"
        else:
            code = "<PSV>"

        try:
            self._conn.write(code)
        except Exception:
            print("Failed to send command to vocalizer")

        if __debug__:
            print("Command sent to vocalizer")


vocalizer = _Vocalizer(_defaults['port'], _defaults['baudrate'])
