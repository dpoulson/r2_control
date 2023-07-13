import requests
import os
import configparser
from r2utils import internet, mainconfig


class Telegram(object):

    def __init__(self):
        _configfile = mainconfig.mainconfig['config_dir'] + 'telegram.cfg'
        _config = configparser.SafeConfigParser({'token': '',
                                                 'chat_id': ''})
        _config.read(_configfile)

        if not os.path.isfile(_configfile):
            print("Config file does not exist (telegram)")
            with open(_configfile, 'wt') as configfile:
                _config.write(configfile)

        _defaults = _config.defaults()
        self.preamble = 'https://api.telegram.org/bot' + _defaults['token']
        self.preamble += '/sendMessage?chat_id=' + _defaults['chat_id']
        self.preamble += '&parse_mode=Markdown&text='

    def send(self, message):
        """ Sends a telegram message """
        if __debug__:
            print("Trying to send a telegram")
        if internet.check():
            try:
                send_message = self.preamble + message
                requests.get(send_message)
                if __debug__:
                    print(send_message)
            except Exception:
                if __debug__:
                    print("Thought we had an internet connection, but sending Telegram failed")
        else:
            if __debug__:
                print("Tried to send Telegram, but no internet connection")
