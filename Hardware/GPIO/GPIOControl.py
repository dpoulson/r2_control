from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
import configparser
import os
import datetime
import time
import csv
import collections
import RPi.GPIO as GPIO
from r2utils import mainconfig
from flask import Blueprint, request
standard_library.install_aliases()
from builtins import object


_configfile = mainconfig.mainconfig['config_dir'] + 'gpio.cfg'

_config = configparser.SafeConfigParser({'logfile': 'gpio.log', 'gpio_configfile': 'gpio_pins.cfg'})

if not os.path.isfile(_configfile):
    print("Config file does not exist")
    with open(_configfile, 'wb') as configfile:
        _config.write(configfile)

_config.read(_configfile)
_defaults = _config.defaults()

_logdir = mainconfig.mainconfig['logdir']
_logfile = _defaults['logfile']

api = Blueprint('gpio', __name__, url_prefix='/gpio')


@api.route('/<gpio>/<state>', methods=['GET'])
def _gpio_on(gpio, state):
    """ GET to set the state of a GPIO pin """
    message = ""
    if request.method == 'GET':
        message += _gpio.setState(gpio, state)
    return message


class _GPIOControl(object):

    _GPIO_def = collections.namedtuple('_GPIO_def', 'name, pin')

    def __init__(self, gpio_configfile, logdir):
        self._logdir = logdir
        self._gpio_list = []
        try:
            ifile = open(mainconfig.mainconfig['config_dir'] + '%s' % gpio_configfile, "rt")
            reader = csv.reader(ifile)
            GPIO.setmode(GPIO.BCM)
            for row in reader:
                pin = row[0]
                name = row[1]
                self._gpio_list.append(self._GPIO_def(pin=pin, name=name))     # Add gpio pin number and name to dictionary,
                GPIO.setup(int(row[0]), GPIO.OUT)  # Set pin as an output
                GPIO.output(int(row[0]), int(row[2]))  # Third value in csv file is default, set pin to that
            if __debug__:
                print("Initialising GPIO Control")
        except:
            print("No pin config file: " + gpio_configfile)

    def setState(self, gpio, state):
        print(self._gpio_list)
        for gpios in self._gpio_list:
            print(gpios)
            if gpios.name == gpio:
                if __debug__:
                    print("Setting %s (pin %s) to %s" % (gpio, gpios.pin, state))
                GPIO.output(int(gpios.pin), int(state))
        return "Ok"


_gpio = _GPIOControl(_defaults['gpio_configfile'], _defaults['logfile'])

