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
from builtins import object


_configfile = mainconfig.mainconfig['config_dir'] + 'teecees.cfg'

_config = configparser.SafeConfigParser({'address': '0x1c', 'logfile': 'vader.log'})
_config.read(_configfile)

if not os.path.isfile(_configfile):
    print("Config file does not exist")
    with open(_configfile, 'wt') as configfile:
        _config.write(configfile)

_defaults = _config.defaults()

_logdir = mainconfig.mainconfig['logdir']
_logfile = _defaults['logfile']

api = Blueprint('teecees', __name__, url_prefix='/teecees')


@api.route('/raw/<cmd>', methods=['GET'])
def _teecees_raw(cmd):
    """ GET to send a raw command to the teecees system"""
    message = ""
    if request.method == 'GET':
        message += _teecees.sendRaw(cmd)
    return message


@api.route('/sequence/<seq>', methods=['GET'])
def _teecees_seq(seq):
    """ GET to send a sequence command to the teecees system"""
    message = ""
    if request.method == 'GET':
        message += _teecees.sendSequence(seq)
    return message


class _TeeceesControl(object):

    def __init__(self, address, logdir):
        self.address = address
        self.bus = smbus.SMBus(int(mainconfig.mainconfig['busid']))
        self.logdir = logdir
        if __debug__:
            print("Initialising TeeCees Control")

    def sendSequence(self, seq):
        if seq.isdigit():
            if __debug__:
                print("Integer sent, sending command")
            cmd = 'S' + seq
            self.sendRaw(cmd)
        else: 
            if __debug__:
                print("Not an integer, decode and send command")
            if seq == "leia":
                if __debug__:
                    print("Leia mode")
                self.sendRaw('S1')
            elif seq == "disable":
                if __debug__:
                    print("Clear and Disable")
                self.sendRaw('S8')
            elif seq == "enable":
                if __debug__:
                    print("Clear and Enable")
                self.sendRaw('S9') 
        return "Ok"

    def sendRaw(self, cmd):
        arrayCmd = bytearray(cmd,'utf8')
        if __debug__:
            print(arrayCmd)
        for i in arrayCmd:
            if __debug__:
                print("Sending byte: %c " % i)
            try:
                bus.write_byte(self.address, i)
            except:
                print("Failed to send command to %s" % self.address)
        return "Ok"


_teecees = _TeeceesControl(_defaults['address'], _defaults['logfile'])

