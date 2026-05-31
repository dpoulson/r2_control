"""Module for playing mp3 files from a directory"""
import os
import configparser
import glob
import random
from builtins import str
from builtins import object
from flask import Blueprint, request
from pygame import mixer
from r2utils import mainconfig
import logging


_configfile = mainconfig.mainconfig['config_dir'] + 'audio.cfg'

_config = configparser.ConfigParser({'sounds_dir': './sounds/',
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
    """Get a list of all available sound files in the library."""
    message = ""
    if request.method == 'GET':
        message += audio.ListSounds()
    return message


@api.route('/<name>', methods=['GET'])
def _audio(name):
    """Play the sound file specified by <name> (e.g. 'Happy007')."""
    success = False
    if request.method == 'GET':
        success = audio.TriggerSound(name)
    if success:
        return "Ok"
    return "Sound file not found or invalid", 404


@api.route('/random/', methods=['GET'])
@api.route('/random/list', methods=['GET'])
def _random_audio_list():
    """Get the list of available random sound categories (e.g. 'alarm', 'happy', 'scream')."""
    types = ""
    if request.method == 'GET':
        types = ', '.join(_Random_Sounds)
    return types


@api.route('/random/<name>', methods=['GET'])
def _random_audio(name):
    """Play a random sound from the category specified by <name> (e.g. 'alarm')."""
    success = False
    if request.method == 'GET':
        success = audio.TriggerRandomSound(name)
    if success:
        return "Ok"
    return "Random sound category not found or invalid", 404


@api.route('/volume', methods=['GET'])
def _get_volume():
    """Get the current audio volume level (as a float between 0.0 and 1.0)."""
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
    Change the audio volume level.
    
    Expected inputs for <level>:
    - 'up' or 'down' (to increment/decrement by 0.025)
    - a float between '0.0' and '1.0' (e.g. '0.5' for 50% volume)
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
        import os
        try:
            if __debug__:
                print(f"Playing {data}")
            audio_file = self.sounds_dir + data + ".mp3"
            if not os.path.exists(audio_file):
                logging.error(f"Sound file does not exist: {audio_file}")
                return False
            # mixer.init()
            if __debug__:
                print("Init mixer")
            mixer.music.load(audio_file)  # % (audio_dir, data))
            if __debug__:
                print(f"{audio_file} Loaded")
            mixer.music.play()
            if __debug__:
                print("Play")
            return True
        except Exception as e:
            logging.error(f"Failed to play sound '{data}': {e}")
            return False

    def TriggerRandomSound(self, data):
        """
        Take one of the prefixes and play a random sound from the library

        Parameters
        ----------
        data : str
             Sound group prefix
        """
        try:
            if data not in _Random_Sounds:
                logging.error(f"Invalid random sound category: {data}")
                return False
            idx = _Random_Sounds.index(data)
            prefix = _Random_Files[idx]
            print(f"Random index: {idx}, prefix={prefix}, sounds_dir={self.sounds_dir}")
            file_list = glob.glob(self.sounds_dir + prefix + "*.mp3")
            if not file_list:
                logging.error(f"No sound files found for category prefix: {prefix}")
                return False
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
            return True
        except Exception as e:
            logging.error(f"Failed to play random sound category '{data}': {e}")
            return False

    def ListSounds(self):
        """ Returns the list of sounds available """
        files = ', '.join(glob.glob(self.sounds_dir + "*.mp3"))
        files = files.replace(self.sounds_dir, "", -1)
        files = files.replace(".mp3", "", -1)
        return files

    def ShowVolume(self):
        """ Returns current volume as a float """
        return mixer.music.get_volume()


audio = _AudioLibrary(_defaults['sounds_dir'], _defaults['volume'])

def get_telemetry():
    """Returns telemetry data for the main /status/json endpoint."""
    return {
        "volume": audio.ShowVolume()
    }
