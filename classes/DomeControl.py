import ConfigParser
import smbus, time, struct, os
import datetime
import time
from config import mainconfig
from time import sleep
from flask import Blueprint, request
from SabertoothPacketSerial import SabertoothPacketSerial

_configfile = 'config/dome.cfg'

_config = ConfigParser.SafeConfigParser({'address': '0x1c', 'logfile': 'dome.log', 'dome_address': '129', 'port': '/dev/ttyUSB0', 'type': 'Syren'})
_config.read(_configfile)

if not os.path.isfile(_configfile):
    print "Config file does not exist"
    with open(_configfile, 'wb') as configfile:
        _config.write(configfile)

_defaults = _config.defaults()

_logtofile = mainconfig['logtofile']
_logdir = mainconfig['logdir']
_logfile = _defaults['logfile']

if _logtofile:
    if __debug__:
        print "Opening log file: Dir: %s - Filename: %s" % (_logdir, _logfile)
    _f = open(_logdir + '/' + _logfile, 'at')
    _f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : ****** Module Started: DOME ******\n")
    _f.flush



api = Blueprint('dome', __name__, url_prefix='/dome')

''' clamp - clamp a value between a min and max '''
def clamp(n, minn, maxn):
    if n < minn:
        if __debug__:
            print "Clamping min"
        return minn
    elif n > maxn:
        if __debug__:
            print "Clamping max " + str(n)
        return maxn
    else:
        return n

@api.route('/center', methods=['GET'])
def _dome_center():
    """ GET to set the dome to face forward"""
    if _logtofile:
        _f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Dome center command\n")
    message = ""
    if request.method == 'GET':
        message += _dome.position(0)
    return message

@api.route('/position/<degrees>', methods=['GET'])
def _dome_center(degrees):
    """ GET to set the dome to face a certain way"""
    if _logtofile:
        _f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Dome position command : " + degrees + "\n")
    message = ""
    if request.method == 'GET':
        message += _dome.position(degrees)
    return message

@api.route('/turn/<stick>', methods=['GET'])
def _dome_turn(stick):
    """ GET to set the dome turning"""
    if _logtofile:
        _f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Dome turn command : " + stick + "\n")
    message = ""
    if request.method == 'GET':
        message += _dome.turn(stick)
    return message


class _DomeControl:

    def __init__(self, address, logfile, dome_address, dome_type, dome_port):
        self.address = address
        self.bus = smbus.SMBus(int(mainconfig['busid']))
        self.logfile = logfile
        self.dome_serial = SabertoothPacketSerial(address=int(dome_address), type=dome_type, port=dome_port)
        if __debug__:
            print "Initialising Dome Control"

    def _read_position(self):
        """ Read the dome position"""
        return "Ok"

    def position(self, position):
        return "Ok"

    def turn(self, stick):
        """ Turns the dome depending on the value of stick """
        self.dome_serial.driveCommand(clamp(stick, -0.99, 0.99))
        return "Ok"


_dome = _DomePSIControl(address=_defaults['address'], logfile=_defaults['logfile'], dome_address=_defaults['dome_address'], dome_type=_defaults['type'], dome_port=_defaults['port'])

