import ConfigParser
import smbus, time, struct, os
import datetime
import time
from config import mainconfig
from time import sleep
from flask import Blueprint, request

_configfile = 'config/smoke.cfg'

_config = ConfigParser.SafeConfigParser({'address': '0x05', 'logfile': 'smoke.log'})
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
    _f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : ****** Module Started: SmokeControl ******\n")
    _f.flush


api = Blueprint('smoke', __name__, url_prefix='/smoke')

@api.route('/on', methods=['GET'])
def _smoke_on():
    """ GET to send a command to the smoke system"""
    if _logtofile:
        _f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Smoke command : on\n")
    message = ""
    if request.method == 'GET':
        message += _smoke.sendRaw('S', '5')
    return message

@api.route('/on/<duration>', methods=['GET'])
def _smoke_on_duration(duration):
    """ GET to turn smoke on for a duration """
    if _logtofile:
        _f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Smoke command : on\n")
    message = ""
    if request.method == 'GET':
        message += _smoke.sendRaw('S', duration)
    return message


class _SmokeControl:

    def __init__(self, address, logdir):
        self.address = address
        self.bus = smbus.SMBus(int(mainconfig['busid']))
        self.logdir = logdir
        if __debug__:
            print "Initialising Smoke Control"

    def sendRaw(self, cmd, duration):
	command = int(hex(ord(cmd)),16)
        hexDuration = list()
        if __debug__:
            print "Duration: %s" % duration
        # We don't want to run for longer than 10 seconds, might burn out the coil 
        if int(duration) > 9:
            if __debug__:
               print "Too long, shortening duration"
            duration = '9'
        hexDuration.append(int(duration,16))
	if __debug__:
	    print "Command: %s | hexDuration: %s " % (command, hexDuration)
        try:
            self.bus.write_i2c_block_data(int(self.address,16), command, hexDuration)
	except:
	    print "Failed to send bytes"
        return "Ok"


_smoke = _SmokeControl(_defaults['address'], _defaults['logfile'])

