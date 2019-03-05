from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import configparser
import os

_configfile = 'config/main.cfg'
_config = configparser.SafeConfigParser({ 'logtofile': True,
                                         'logdir' : './logs',
                                         'logfile' : 'debug.log',
                                         'busid' : '1',
                                         'plugins' : '',
                                         'modules' : 'scripts,audio'
                                            })

_config.read(_configfile)

if not os.path.isfile(_configfile):
    print("Config file does not exist")
    with open(_configfile, 'wt') as configfile:
        _config.write(configfile)


mainconfig = _config.defaults()


