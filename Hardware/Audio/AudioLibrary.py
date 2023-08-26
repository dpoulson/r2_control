"""Module for playing mp3 files from a directory"""
import os
import configparser
import glob
import random
from builtins import str
from builtins import object
from flask import Blueprint, request
from future import standard_library
from pygame import mixer
from r2utils import mainconfig
standard_library.install_aliases()


_configfile = mainconfig.mainconfig['config_dir'] + 'audio.cfg'

_config = configparser.SafeConfigParser({'sounds_dir': './sounds/',
                                         'logfile': 'audio.log',
                                         'volume': '0.3'})
_config.read(_configfile)

if not os.path.isfile(_configfile):
    print("Config file does not exist (Audio)")
    with open(_configfile, 'wt', encoding="utf-8") as configfile:
        _config.write(configfile)

_defaults = _config.defaults()

_logdir = mainconfig.mainconfig['logdir']
_logfile = _defaults['logfile']

_Random_Sounds = ['alarm',
                  'happy',
                  'hum',
                  'misc',
                  'quote',
                  'razz',
                  'sad',
                  'sent',
                  'ooh',
                  'proc',
                  'whistle',
                  'scream']
_Random_Files = ['ALARM',
                 'Happy',
                 'HUM__',
                 'MISC_',
                 'Quote',
                 'RAZZ_',
                 'Sad__',
                 'SENT_',
                 'OOH__',
                 'PROC_',
                 'WHIST',
                 'SCREA']

api = Blueprint('audio', __name__, url_prefix='/audio')


@api.route('/', methods=['GET'])
@api.route('/list', methods=['GET'])
def _audio_list():
    """GET gives a comma separated list of available sounds"""
    message = ""
    if request.method == 'GET':
        message += audio.ListSounds()
    return message


@api.route('/<name>', methods=['GET'])
def _audio(name):
    """GET to trigger the given sound"""
    if request.method == 'GET':
        audio.TriggerSound(name)
    return "Ok"


@api.route('/random/', methods=['GET'])
@api.route('/random/list', methods=['GET'])
def _random_audio_list():
    """GET returns types of sounds available at random"""
    types = ""
    if request.method == 'GET':
        types = ', '.join(_Random_Sounds)
    return types


@api.route('/random/<name>', methods=['GET'])
def _random_audio(name):
    """GET to play a random sound of a given type"""
    if request.method == 'GET':
        audio.TriggerRandomSound(name)
    return "Ok"


@api.route('/volume', methods=['GET'])
def _get_volume():
    """GET returns current volume level"""
    message = ""
    if request.method == 'GET':
        cur_vol = mixer.music.get_volume()
        if __debug__:
            print(f"Current volume: {cur_vol}")
        message += str(cur_vol)
        if __debug__:
            print(f"Sending: {message}")
    return message


@api.route('/volume/<level>', methods=['GET'])
def _set_volume(level):
    """
    Changes the volume level

    Parameters
    ----------
    level : str
            Either a string of up/down to increment/decrement the volume, or
            an explicitly set volume between 0 and 1
    """
    if request.method == 'GET':
        if level == "up":
            if __debug__:
                print("Increasing volume")
            new_level = mixer.music.get_volume() + 0.025
        elif level == "down":
            if __debug__:
                print("Decreasing volume")
            new_level = mixer.music.get_volume() - 0.025
        else:
            if __debug__:
                print("Volume level explicitly states")
            new_level = float(level)
        if new_level < 0:
            new_level = 0
        if __debug__:
            print(f"Setting volume to: {new_level}")
        mixer.music.set_volume(float(new_level))
    return "Ok"


class _AudioLibrary(object):
    """
    The class for playing audio samples via pygame mixer

    Sounds are stored in a single directory. The following prefixes are used
    to group sets of sounds for random play. Any other filenames can be played
    as normal.

    'ALARM',
    'Happy',
    'HUM__',
    'MISC_',
    'Quote',
    'RAZZ_',
    'Sad__',
    'SENT_',
    'OOH__',
    'PROC_',
    'WHIST',
    'SCREA'
    """

    def __init__(self, sounds_dir, volume):
        """
        Init of AudioLibrary class

        Parameters
        ----------
        sounds_dir : str
             Directory containing sound files
        volume : float
             Initial volume level
        """

        if __debug__:
            print(f"Initiating audio: sounds_dir = {sounds_dir}")
        mixer.init()
        mixer.music.set_volume(float(volume))
        self.sounds_dir = sounds_dir

    def TriggerSound(self, data):
        """
        Play a sound

        Parameters
        ----------
        data : str
             Name of file (not including extension)
        """

        if __debug__:
            print(f"Playing {data}")
        audio_file = self.sounds_dir + data + ".mp3"
        # mixer.init()
        if __debug__:
            print("Init mixer")
        mixer.music.load(audio_file)  # % (audio_dir, data))
        if __debug__:
            print(f"{audio_file} Loaded")
        mixer.music.play()
        if __debug__:
            print("Play")

    def TriggerRandomSound(self, data):
        """
        Take one of the prefixes and play a random sound from the library

        Parameters
        ----------
        data : str
             Sound group prefix
        """

        idx = _Random_Sounds.index(data)
        prefix = _Random_Files[idx]
        print(f"Random index: {idx}, prefix={prefix}, sounds_dir={self.sounds_dir}")
        file_list = glob.glob(self.sounds_dir + prefix + "*.mp3")
        file_idx = len(file_list) - 1
        audio_file = file_list[random.randint(0, file_idx)]
        if __debug__:
            print(f"Playing {data}")
        mixer.init()
        if __debug__:
            print("Init mixer")
        mixer.music.load(audio_file)  # % (audio_dir, data))
        if __debug__:
            print(f"{audio_file} Loaded")
        mixer.music.play()
        if __debug__:
            print("Play")

    def ListSounds(self):
        """ Returns the list of sounds available """
        files = ', '.join(glob.glob(self.sounds_dir + "*.mp3"))
        files = files.replace(self.sounds_dir, "", -1)
        files = files.replace(".mp3", "", -1)
        return files


audio = _AudioLibrary(_defaults['sounds_dir'], _defaults['volume'])
