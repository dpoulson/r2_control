from __future__ import print_function
from future import standard_library
import configparser
import os
standard_library.install_aliases()

_configdir = '/home/pi/.r2_config/'
if not os.path.exists(_configdir):
    os.makedirs(_configdir)
_configfile = _configdir + 'main.cfg'
_config = configparser.SafeConfigParser({'logtofile': True,
                                         'logdir': './logs',
                                         'logfile': 'debug.log',
                                         'busid': '1',
                                         'plugins': 'GPIO,Audio,Scripts',
                                         'config_dir': _configdir,
                                         'servos': 'body,dome',
                                         'telegram': False
                                         })

_config.add_section('Dome')
_config.set('Dome', 'address', '129')
_config.set('Dome', 'type', 'Syren')
_config.set('Dome', 'port', '/dev/ttyUSB0')
_config.add_section('Drive')
_config.set('Drive', 'address', '128')
_config.set('Drive', 'type', 'Sabertooth')
_config.set('Drive', 'port', '/dev/ttyACM0')

_config.read(_configfile)

if not os.path.isfile(_configfile):
    print("Config file does not exist (Main Config)")
    with open(_configfile, 'wt') as configfile:
        _config.write(configfile)


mainconfig = _config.defaults()
