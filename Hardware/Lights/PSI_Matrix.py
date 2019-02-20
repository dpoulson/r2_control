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


_configfile = 'config/psi_matrix.cfg'

_config = configparser.SafeConfigParser({'address': '0x06', 'logfile': 'psi_matrix.log'})
_config.read(_configfile)

if not os.path.isfile(_configfile):
    print("Config file does not exist")
    with open(_configfile, 'wt') as configfile:
        _config.write(configfile)

_defaults = _config.defaults()

_logtofile = mainconfig.mainconfig['logtofile']
_logdir = mainconfig.mainconfig['logdir']
_logfile = _defaults['logfile']

if _logtofile:
    if __debug__:
        print("Opening log file: Dir: %s - Filename: %s" % (_logdir, _logfile))
    _f = open(_logdir + '/' + _logfile, 'at')
    _f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
             " : ****** Module Started: PSI_MatrixControl ******\n")
    _f.flush


api = Blueprint('psi_matrix', __name__, url_prefix='/psi_matrix')


@api.route('/<cmd>/<duration>', methods=['GET'])
def _psi_matrix_cmd(cmd, duration):
    """ GET to turn psi_matrix on for a duration """
    if _logtofile:
        _f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                 " : PSI_Matrix command : " + cmd + "\n")
    message = ""
    if request.method == 'GET':
        message += _psi_matrix.sendRaw(cmd, duration)
    return message


class _PSI_MatrixControl(object):

    def __init__(self, address, logdir):
        self.address = address
        self.bus = smbus.SMBus(int(mainconfig.mainconfig['busid']))
        self.logdir = logdir
        if __debug__:
            print("Initialising PSI_Matrix Control")

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


_psi_matrix = _PSI_MatrixControl(_defaults['address'], _defaults['logfile'])

