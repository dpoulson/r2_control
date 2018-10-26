import ConfigParser
import smbus, time, struct, os
import datetime
import time
from config import mainconfig
from time import sleep
from flask import Blueprint, request

_configfile = 'config/smoke.cfg'

_config = ConfigParser.SafeConfigParser({'address': '0x18', 'logfile': 'smoke.log'})
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
        message += _smoke.sendRaw("S")
    return message

class _SmokeControl:

    def __init__(self, address, logdir):
        self.address = address
        self.bus = smbus.SMBus(int(mainconfig['busid']))
        self.logdir = logdir
        if __debug__:
            print "Initialising Smoke Control"

    def sendRaw(self, cmd):
	command = list(cmd)
	hexCommand = list()
	for i in command:
            h=int(hex(ord(i)),16)
	    hexCommand.append(h)	
	if __debug__:
	    print hexCommand
        try:
            self.bus.write_i2c_block_data(int(self.address,16), hexCommand[0], hexCommand[1:])
	except:
	    print "Failed to send bytes"
        return "Ok"


_smoke = _SmokeControl(_defaults['address'], _defaults['logfile'])

