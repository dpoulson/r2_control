import ConfigParser
import smbus, time, struct, os
import datetime
import time
from config import mainconfig
from time import sleep
from flask import Blueprint, request

_configfile = 'config/dome.cfg'

_config = ConfigParser.SafeConfigParser({'address': '0x1c', 'logfile': 'dome.log'})
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

@api.route('/center', methods=['GET'])
def _dome_center():
    """ GET to set the dome to face forward"""
    if _logtofile:
        _f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Dome raw command : " + cmd + "\n")
    message = ""
    if request.method == 'GET':
        message += _dome.send()
    return message

class _DomeControl:

    def __init__(self, address, logdir):
        self.address = address
        self.bus = smbus.SMBus(int(mainconfig['busid']))
        self.logdir = logdir
        if __debug__:
            print "Initialising Dome Control"

    def send(self, cmd):
        arrayCmd = bytearray(cmd,'utf8')
        if __debug__:
            print arrayCmd
        for i in arrayCmd:
            if __debug__:
                print "Sending byte: %c " % i
            try:
                bus.write_byte(self.address, i)
            except:
                print "Failed to send command to %s" % self.address
        return "Ok"


_dome = _DomePSIControl(_defaults['address'], _defaults['logfile'])

