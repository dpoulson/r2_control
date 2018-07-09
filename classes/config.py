import ConfigParser

_config = ConfigParser.SafeConfigParser({ 'logtofile': True,
                                         'logdir' : './logs',
                                         'logfile' : 'debug.log',
                                         'busid' : '1',
                                         'modules' : 'scripts,audio'
                                            })

_config.read('config/main.cfg')

mainconfig = _config.defaults()


