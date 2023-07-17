""" Module to control FlthyMcNasty HP Lights """
from builtins import hex
from builtins import object
import os
import configparser
import smbus
from flask import Blueprint, request
from future import standard_library
from r2utils import mainconfig
standard_library.install_aliases()

_configfile = mainconfig.mainconfig['config_dir'] + 'flthy.cfg'

_config = configparser.SafeConfigParser({'address': '0x19',
                                         'logfile': 'flthy.log',
                                         'reeltwo': 'false'})
if not os.path.isfile(_configfile):
    print("Config file does not exist")
    with open(_configfile, 'wt', encoding="utf-8") as configfile:
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
        message += _flthy.SendRaw(cmd)
    return message


@api.route('/sequence/<seq>', methods=['GET'])
def _flthy_seq(seq):
    """ GET to send a sequence command to the flthy HP system"""
    message = ""
    if request.method == 'GET':
        message += _flthy.SendSequence(seq)
    return message


@api.route('/<hp>/<hptype>/<seq>/<value>', methods=['GET'])
def _flthy_cmd(hp, hptype, seq, value):
    """ GET to send a command to the flthy HP system"""
    message = ""
    if request.method == 'GET':
        message += _flthy.SendCommand(hp, hptype, seq, value)
    return message


class _FlthyHPControl(object):
    """ FlthyMcNasty HP Control """

    def __init__(self, address, logdir, reeltwo):
        self.address = address
        self.reeltwo = reeltwo
        self.bus = smbus.SMBus(int(mainconfig.mainconfig['busid']))
        self.logdir = logdir
        if __debug__:
            print("Initialising FlthyHP Control")
            print(f"Address: {self.address} | Bus: {self.bus} | logdir: {self.logdir} | reeltwo: {self.reeltwo}")

    def SendSequence(self, seq):
        """ Send sequence command """
        if seq.isdigit():
            if __debug__:
                print("Integer sent, sending command")
            cmd = 'S' + seq
            self.SendRaw(cmd)
        else:
            if __debug__:
                print("Not an integer, decode and send command")
            if seq == "leia":
                if __debug__:
                    print("Leia mode")
                self.SendRaw('S1')
            elif seq == "disable":
                if __debug__:
                    print("Clear and Disable")
                self.SendRaw('S8')
            elif seq == "enable":
                if __debug__:
                    print("Clear and Enable")
                self.SendRaw('S9')
        return "Ok"

    def SendCommand(self, hp, hptype, seq, value):
        """ Decoding HP command """
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
                    hp_cmd = "F"
                elif hp == "top":
                    hp_cmd = "T"
                elif (hp == "rear") or (hp == "back"):
                    hp_cmd = "R"
                elif hp == "all":
                    hp_cmd = "A"
            else:
                if __debug__:
                    print("HP code used")
                hp_cmd = hp
        else:
            print("Illegal HP code")

        if (hptype.lower() in _type_list) or (type in ['0', '1']):
            if __debug__:
                print("Type selection OK")
            if hptype.lower() in _type_list:
                hptype = hptype.lower()
                if __debug__:
                    print("Type word used")
                if hptype == "servo":
                    type_cmd = "1"
                elif hptype == "light":
                    type_cmd = "0"
            else:
                if __debug__:
                    print("Type code used")
                type_cmd = hptype
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
                    seq_cmd = "01"
                elif seq == "projector":
                    seq_cmd = "02"
                elif seq == "shortcircuit":
                    seq_cmd = "05"
            else:
                if __debug__:
                    print("Sequence code used")
                seq_cmd = seq
        else:
            print("Illegal type code")

        if type_cmd == "1":
            if (value.lower() in _position_list) or (value in ['1', '2', '3', '4', '5', '6', '7', '8']):
                if __debug__:
                    print(f"Servo command: {value}")
                if value.lower() in _position_list:
                    value = value.lower()
                else:
                    if __debug__:
                        print("Value code used")
                    value_cmd = value
        else:
            if (value.lower() in _colour_list) or (value in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']):
                if __debug__:
                    print(f"Light command: {value}")
                if value.lower() in _colour_list:
                    value = value.lower()
                else:
                    if __debug__:
                        print("Value code used")
                    value_cmd = value

        cmd = hp_cmd + type_cmd + seq_cmd + value_cmd
        self.SendRaw(cmd)
        return "OK"

    def SendRaw(self, cmd):
        """ Send a raw command """
        command = list(cmd)
        hexCommand = []
        if self.reeltwo is True:
            if __debug__:
                print("ReelTwo Mode")
            hexCommand.append(int(hex(ord('H')), 16))
            hexCommand.append(int(hex(ord('P')), 16))
        for i in command:
            h = int(hex(ord(i)), 16)
            hexCommand.append(h)
        if __debug__:
            print(hexCommand)
        try:
            self.bus.write_i2c_block_data(int(self.address, 16), hexCommand[0], hexCommand[1:])
        except Exception:
            print("Failed to send bytes")
        return "Ok"


_flthy = _FlthyHPControl(_defaults['address'], _defaults['logfile'], _config.getboolean('DEFAULT', 'reeltwo'))
