import ConfigParser
import smbus, time, struct, os
import datetime
import time
from config import mainconfig
from time import sleep
from flask import Blueprint, request

_configfile = 'config/flthy.cfg'

_config = ConfigParser.SafeConfigParser({'address': '0x19', 'logfile': 'flthy.log'})
_config.read(_configfile)

if not os.path.isfile(_configfile):
    print "Config file does not exist"
    with open(_configfile, 'wb') as configfile:
        _config.write(configfile)

_defaults = _config.defaults()

_hp_list       = ['top', 'front', 'rear', 'back', 'all']
_type_list     = ['light', 'servo']
_sequence_list = ['leia', 'projector', 'dimpulse', 'cycle', 'shortcircuit', 'colour', 'rainbow', 'disable', 'enable']
_colour_list   = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta', 'orange', 'purple', 'white', 'random']
_position_list = ['top', 'bottom', 'center', 'left', 'right']

_logtofile = mainconfig['logtofile']
_logdir = mainconfig['logdir']
_logfile = _defaults['logfile']

if _logtofile:
    if __debug__:
        print "Opening log file: Dir: %s - Filename: %s" % (_logdir, _logfile)
    _f = open(_logdir + '/' + _logfile, 'at')
    _f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : ****** Module Started: FlthyHP ******\n")
    _f.flush



api = Blueprint('flthy', __name__, url_prefix='/flthy')

@api.route('/raw/<cmd>', methods=['GET'])
def flthy_raw(cmd):
    """ GET to send a raw command to the flthy HP system"""
    if _logtofile:
        _f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Flthy raw command : " + cmd + "\n")
    message = ""
    if request.method == 'GET':
        message += _flthy.sendRaw(cmd)
    return message

@api.route('/sequence/<seq>', methods=['GET'])
def flthy_seq(seq):
    """ GET to send a sequence command to the flthy HP system"""
    if _logtofile:
        _f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Flthy sequence command : " + seq + "\n")
    message = ""
    if request.method == 'GET':
        message += _flthy.sendSequence(seq)
    return message

@api.route('/<hp>/<type>/<seq>/<value>', methods=['GET'])
def flthy_cmd(hp, type, seq, value):
    """ GET to send a command to the flthy HP system"""
    if _logtofile:
        _f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Flthy command : " + hp + " " + type + " " + seq + " " + value + "\n")
    message = ""
    if request.method == 'GET':
        message += _flthy.sendCommand(hp, type, seq, value)
    return message


class FlthyHPControl:

    def __init__(self, address, logdir):
        self.address = address
        self.bus = smbus.SMBus(1)
        self.logdir = logdir
        if __debug__:
            print "Initialising FlthyHP Control"

    def sendSequence(self, seq):
        if seq.isdigit():
            if __debug__:
                print "Integer sent, sending command"
            cmd = 'S' + seq
            self.sendRaw(cmd)
        else: 
            if __debug__:
                print "Not an integer, decode and send command"
            if seq == "leia":
                if __debug__:
                    print "Leia mode"
                self.sendRaw('S1')
            elif seq == "disable":
                if __debug__:
                    print "Clear and Disable"
                self.sendRaw('S8')
            elif seq == "enable":
                if __debug__:
                    print "Clear and Enable"
                self.sendRaw('S9') 
        return "Ok"

    def sendCommand(self, hp, type, seq, value):

        # Decoding HP command
        if __debug__:
            print "HP: %s" % hp
        if (hp.lower() in _hp_list) or (hp in ['T', 'F', 'R', 'A']):
            if __debug__:
                print "HP selection OK"
            if hp.lower() in _hp_list:
                hp = hp.lower()
                if __debug__:
                    print "HP word used"
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
                    print "HP code used"
                hpCmd = hp
        else:
            print "Illegal HP code"

        if (type.lower() in _type_list) or (type in ['0', '1']):
            if __debug__:
                print "Type selection OK"
            if type.lower() in _type_list:
                type = type.lower()
                if __debug__:
                    print "Type word used"
                if type == "servo":
                    typeCmd = "1"
                elif type == "light":
                    typeCmd = "0"
            else:
                if __debug__:
                    print "Type code used"
                typeCmd = type
        else:
            print "Illegal type code"

        if (seq.lower() in _sequence_list) or (seq in ['01', '02', '03', '04','05', '06', '07', '98', '99']):
            if __debug__:
                print "Sequence selection OK"
            if seq.lower() in _sequence_list:
                seq = seq.lower()
                if __debug__:
                    print "Sequence word used"
                if seq == "leia":
                    seqCmd = "01"
                elif seq == "projector":
                    seqCmd = "02"
                elif seq == "shortcircuit":
                    seqCmd = "05"
            else:
                if __debug__:
                    print "Sequence code used"
                seqCmd = seq
        else:
            print "Illegal type code"


        if typeCmd == "1":
            if (value.lower() in _position_list) or (value in ['1', '2', '3', '4','5', '6', '7', '8']):
                if __debug__:
                    print "Servo command: %s " % value
                if value.lower() in _position_list:
                    value = value.lower()
                else:
                    if __debug__:
                        print "Value code used"
                    valueCmd = value
        else:
            if (value.lower() in _colour_list) or (value in ['1', '2', '3', '4','5', '6', '7', '8', '9', '0']):
                if __debug__:
                    print "Light command: %s " % value
                if value.lower() in _colour_list:
                    value = value.lower()
                else:
                    if __debug__:
                        print "Value code used"
                    valueCmd = value


        cmd = hpCmd + typeCmd + seqCmd + valueCmd
        self.sendRaw(cmd) 
        return "OK"



    def sendRaw(self, cmd):
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


_flthy = FlthyHPControl(_defaults['address'], _defaults['logfile'])

