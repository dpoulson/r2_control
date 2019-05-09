from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
from builtins import object
import configparser
import smbus
import os
import datetime
import time
from r2utils import mainconfig
from flask import Blueprint, request
standard_library.install_aliases()


_configfile = mainconfig.mainconfig['config_dir'] + 'vader.cfg'

_config = configparser.SafeConfigParser({'address': '0x1c', 'logfile': 'vader.log'})
_config.read(_configfile)

if not os.path.isfile(_configfile):
    print("Config file does not exist")
    with open(_configfile, 'wt') as configfile:
        _config.write(configfile)

_defaults = _config.defaults()

_logdir = mainconfig.mainconfig['logdir']
_logfile = _defaults['logfile']

api = Blueprint('vader', __name__, url_prefix='/vader')


@api.route('/raw/<cmd>', methods=['GET'])
def _vader_raw(cmd):
    """ GET to send a raw command to the vader HP system"""
    message = ""
    if request.method == 'GET':
        message += _vader.sendRaw(cmd)
    return message


@api.route('/sequence/<seq>', methods=['GET'])
def _vader_seq(seq):
    """ GET to send a sequence command to the vader HP system"""
    message = ""
    if request.method == 'GET':
        message += _vader.sendSequence(seq)
    return message


class _VaderPSIControl(object):

    def __init__(self, address, logdir):
        self.address = address
        self.bus = smbus.SMBus(int(mainconfig.mainconfig['busid']))
        self.logdir = logdir
        if __debug__:
            print("Initialising VaderPSI Control")

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


_vader = _VaderPSIControl(_defaults['address'], _defaults['logfile'])

