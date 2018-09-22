import ConfigParser
import os

_configfile = 'config/main.cfg'
_config = ConfigParser.SafeConfigParser({ 'logtofile': True,
                                         'logdir' : './logs',
                                         'logfile' : 'debug.log',
                                         'busid' : '1',
                                         'modules' : 'scripts,audio'
                                            })

_config.read(_configfile)

if not os.path.isfile(_configfile):
    print "Config file does not exist"
    with open(_configfile, 'wb') as configfile:
        _config.write(configfile)


mainconfig = _config.defaults()


