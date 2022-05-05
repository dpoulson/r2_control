#!/usr/bin/python
# 
from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
import smbus
import time
import threading
import struct
import os
import csv
import configparser
from threading import Thread
from time import sleep
from r2utils import mainconfig
from r2utils import telegram
standard_library.install_aliases()
from builtins import map
from builtins import range
from flask import Blueprint, request


_configfile = mainconfig.mainconfig['config_dir'] + 'monitoring.cfg'

_config = configparser.SafeConfigParser({'address': '0x04',
                                         'logfile': 'monitoring.log',
                                         'interval': 0.5})
_config.read(_configfile)

if not os.path.isfile(_configfile):
    print("Config file does not exist (Monitoring)")
    with open(_configfile, 'wt') as configfile:
        _config.write(configfile)

_defaults = _config.defaults()

_logdir = mainconfig.mainconfig['logdir']
_logfile = _defaults['logfile']

api = Blueprint('monitoring', __name__, url_prefix='/monitoring')

@api.route('/', methods=['GET'])
@api.route('/battery', methods=['GET'])
def _battery():
    """GET gives a comma separated list of stats"""
    message = ""
    if request.method == 'GET':
        message += str(monitoring.queryBattery())
    return message

@api.route('/balance', methods=['GET'])
def _balance():
    """GET gives the current battery balance"""
    message = ""
    if request.method == 'GET':
        message += str(monitoring.queryBatteryBalance())
    return message


class _Monitoring(object):

    def monitor_loop(self, extracted):
        f = open(self.logdir + '/power.log', 'at')
        data = [0, 0, 0, 0, 0, 0, 0, 0]
        while True:
            try:
                data = self.bus.read_i2c_block_data(0x04, 0)
            except:
                if __debug__:
                    print("Failed to read i2c data")
                sleep(1)
            extracted[0] = time.time()
            for i in range(0, 8):
                bytes = bytearray(data[4 * i:4 * i + 4])
                extracted[i + 1] = struct.unpack('f', bytes)
            if __debug__:
                print("Writing csv row")
            writer = csv.writer(f)
            writer.writerow(self.extracted)
            f.flush()
            sleep(self.interval)
            # If telegram messaging is active, do a few checks and notify
            if self.telegram:
                if __debug__:
                    print("Telegram enabled")
                if (self.extracted[5] != 0) and (self.extracted[5] < 21) and not self.lowbat:
                    if __debug__:
                        print("Battery low")
                    telegram.send("Battery below 21V")
                    self.lowbat = True

    def __init__(self, address, interval):
        # Check for telegram config
        self.telegram = False
        self.address = address
        self.interval = float(interval)
        self.logdir = mainconfig.mainconfig['logdir']
        self.lowbat = False
        self.extracted = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        try:
            self.bus = smbus.SMBus(int(mainconfig.mainconfig['busid']))
        except:
            print("Failed to connect to device on bus")
        if __debug__:
            print("Initialising Monitoring")
            print("Address: %s | Bus: %s | logdir: %s" % (self.address, self.bus, self.logdir))
        if self.telegram:
            telegram.send("Monitoring started")
        loop = Thread(target=self.monitor_loop, args=(self.extracted, ))
        loop.daemon = True
        loop.start()

    def queryBattery(self):
        return self.extracted[5][0]

    def queryBatteryBalance(self):
        return self.extracted[7][0] - self.extracted[6][0]

    def queryCurrentMain(self):
        return self.extracted[1][0]

    def queryCurrentLeft(self):
        return self.extracted[2][0]

    def queryCurrentRight(self):
        return self.extracted[3][0]

    def queryCurrentDome(self):
        return self.extracted[4][0]


monitoring = _Monitoring(_defaults['address'], _defaults['interval'])
