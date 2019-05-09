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


_configfile = mainconfig.mainconfig['config_dir'] + 'flthy.cfg'

_config = configparser.SafeConfigParser({'address': '0x19',
                                         'logfile': 'flthy.log',
                                         'reeltwo': 'false'})
if not os.path.isfile(_configfile):
    print("Config file does not exist")
    with open(_configfile, 'wt') as configfile:
        _config.write(configfile)

_config.read(_configfile)

_defaults = _config.defaults()

_hp_list = ['top', 'front', 'rear', 'back', 'all']
_type_list = ['light', 'servo']
_sequence_list = ['leia', 'projector', 'dimpulse', 'cycle', 'shortcircuit', 'colour', 'rainbow', 'disable', 'enable']
_colour_list = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta', 'orange', 'purple', 'white', 'random']
_position_list = ['top', 'bottom', 'center', 'left', 'right']

_logdir = mainconfig.mainconfig['logdir']
_logfile = _defaults['logfile']

api = Blueprint('flthy', __name__, url_prefix='/flthy')


@api.route('/raw/<cmd>', methods=['GET'])
def _flthy_raw(cmd):
    """ GET to send a raw command to the flthy HP system"""
    message = ""
    if request.method == 'GET':
        message += _flthy.sendRaw(cmd)
    return message


@api.route('/sequence/<seq>', methods=['GET'])
def _flthy_seq(seq):
    """ GET to send a sequence command to the flthy HP system"""
    message = ""
    if request.method == 'GET':
        message += _flthy.sendSequence(seq)
    return message


@api.route('/<hp>/<type>/<seq>/<value>', methods=['GET'])
def _flthy_cmd(hp, type, seq, value):
    """ GET to send a command to the flthy HP system"""
    message = ""
    if request.method == 'GET':
        message += _flthy.sendCommand(hp, type, seq, value)
    return message


class _FlthyHPControl(object):

    def __init__(self, address, logdir, reeltwo):
        self.address = address
        self.reeltwo = reeltwo
        self.bus = smbus.SMBus(int(mainconfig.mainconfig['busid']))
        self.logdir = logdir
        if __debug__:
            print("Initialising FlthyHP Control")
            print("Address: %s | Bus: %s | logdir: %s | reeltwo: %s" % (self.address, self.bus, self.logdir, self.reeltwo))

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

    def sendCommand(self, hp, type, seq, value):
        # Decoding HP command
        if __debug__:
            print("HP: %s" % hp)
        if (hp.lower() in _hp_list) or (hp in ['T', 'F', 'R', 'A']):
            if __debug__:
                print("HP selection OK")
            if hp.lower() in _hp_list:
                hp = hp.lower()
                if __debug__:
                    print("HP word used")
                if hp == "front":
                    hpCmd = "F"
                elif hp == "top":
                    hpCmd = "T"
                elif (hp == "rear") or (hp == "back"):
                    hpCmd = "R"
                elif hp == "all":
                    hpCmd = "A"
            else:
                if __debug__:
                    print("HP code used")
                hpCmd = hp
        else:
            print("Illegal HP code")

        if (type.lower() in _type_list) or (type in ['0', '1']):
            if __debug__:
                print("Type selection OK")
            if type.lower() in _type_list:
                type = type.lower()
                if __debug__:
                    print("Type word used")
                if type == "servo":
                    typeCmd = "1"
                elif type == "light":
                    typeCmd = "0"
            else:
                if __debug__:
                    print("Type code used")
                typeCmd = type
        else:
            print("Illegal type code")

        if (seq.lower() in _sequence_list) or (seq in ['01', '02', '03', '04', '05', '06', '07', '98', '99']):
            if __debug__:
                print("Sequence selection OK")
            if seq.lower() in _sequence_list:
                seq = seq.lower()
                if __debug__:
                    print("Sequence word used")
                if seq == "leia":
                    seqCmd = "01"
                elif seq == "projector":
                    seqCmd = "02"
                elif seq == "shortcircuit":
                    seqCmd = "05"
            else:
                if __debug__:
                    print("Sequence code used")
                seqCmd = seq
        else:
            print("Illegal type code")

        if typeCmd == "1":
            if (value.lower() in _position_list) or (value in ['1', '2', '3', '4', '5', '6', '7', '8']):
                if __debug__:
                    print("Servo command: %s " % value)
                if value.lower() in _position_list:
                    value = value.lower()
                else:
                    if __debug__:
                        print("Value code used")
                    valueCmd = value
        else:
            if (value.lower() in _colour_list) or (value in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']):
                if __debug__:
                    print("Light command: %s " % value)
                if value.lower() in _colour_list:
                    value = value.lower()
                else:
                    if __debug__:
                        print("Value code used")
                    valueCmd = value

        cmd = hpCmd + typeCmd + seqCmd + valueCmd
        self.sendRaw(cmd) 
        return "OK"

    def sendRaw(self, cmd):
        command = list(cmd)
        hexCommand = list()
        if self.reeltwo == True:
            if __debug__:
               print("ReelTwo Mode");
            hexCommand.append(int(hex(ord('H')), 16))
            hexCommand.append(int(hex(ord('P')), 16))
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


_flthy = _FlthyHPControl(_defaults['address'], _defaults['logfile'], _config.getboolean('DEFAULT', 'reeltwo'))

