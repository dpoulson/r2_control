from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
import glob
import random
import configparser
from pygame import mixer  # Load the required library
import os
import datetime
import time
from r2utils import mainconfig
from flask import Blueprint, request
standard_library.install_aliases()
from builtins import str
from builtins import object


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
        audio.TriggerSound('happy')
    return message

@api.route('/sad', methods=['GET'])
def _play_sad():
    """GET to play SAD sound"""
    message = ""
    if request.method == 'GET':
        audio.TriggerSound('sad')
    return message

@api.route('/angry', methods=['GET'])
def _play_angry():
    """GET to play ANGRY sound"""
    message = ""
    if request.method == 'GET':
        audio.TriggerSound('angry')
    return message

@api.route('/scared', methods=['GET'])
def _play_scared():
    """GET to play SCARED sound"""
    message = ""
    if request.method == 'GET':
        audio.TriggerSound('scared')
    return message

@api.route('/overload', methods=['GET'])
def _play_overload():
    """GET to play OVERLOAD sound"""
    message = ""
    if request.method == 'GET':
        audio.TriggerSound('overload')
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
        except:
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
        else:
            code = "PSV"
        
        try:
            sent = self._conn.write(code)
        except:
            print("Failed to send command to vocalizer")
        
        if __debug__:
            print("Command sent to vocalizer")
        


vocalizer = _Vocalizer(_defaults['port'], _defaults['baudrate'])
