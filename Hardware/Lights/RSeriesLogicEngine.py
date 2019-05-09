from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
import smbus
import os
import datetime
import time
from r2utils import mainconfig
from flask import Blueprint, request
import configparser
standard_library.install_aliases()
from builtins import hex
from builtins import object


_configfile = mainconfig.mainconfig['config_dir'] + 'rseries.cfg'

_config = configparser.SafeConfigParser({'address': '0x20',
                                         'logfile': 'rseries.log',
                                         'reeltwo': 'false'})
_config.read(_configfile)

if not os.path.isfile(_configfile):
    print("Config file does not exist")
    with open(_configfile, 'wt') as configfile:
        _config.write(configfile)

_defaults = _config.defaults()

_logdir = mainconfig.mainconfig['logdir']
_logfile = _defaults['logfile']

api = Blueprint('rseries', __name__, url_prefix='/rseries')


@api.route('/raw/<cmd>', methods=['GET'])
def _rseries_raw(cmd):
    """ GET to send a raw command to the rseries system"""
    message = ""
    if request.method == 'GET':
        message += _rseries.sendRaw(cmd)
    return message


class _RSeriesLogicEngine(object):

    def __init__(self, address, logdir, reeltwo):
        self.address = address
        self.reeltwo = reeltwo
        self.bus = smbus.SMBus(int(mainconfig.mainconfig['busid']))
        self.logdir = logdir
        if __debug__:
            print("Initialising RSeries Control")
            print("Address: %s | Bus: %s | logdir: %s | reeltwo: %s" % (self.address, self.bus, self.logdir, self.reeltwo))

    def sendRaw(self, cmd):
        command = list(cmd)
        hexCommand = list()
        if self.reeltwo == True:
            if __debug__:
               print("ReelTwo Mode");
            hexCommand.append(int(hex(ord('L')), 16))
            hexCommand.append(int(hex(ord('E')), 16))
        for i in command:
            h = int(hex(ord(i)), 16)
            hexCommand.append(h)	
        if __debug__:
            print(hexCommand)
        try:
            self.bus.write_i2c_block_data(int(self.address, 16), hexCommand[0], hexCommand[1:])
        except:
            print("Failed to send bytes")
        return "Ok"


_rseries = _RSeriesLogicEngine(_defaults['address'], _defaults['logfile'], _config.getboolean('DEFAULT', 'reeltwo'))


