
import ConfigParser
import os, sys
import thread
import time
import collections
from pygame import mixer # Load the required library


class AudioLibrary :


  def init_config(self, audio_config_file):
    "Load in CSV of Servo definitions"
    config = ConfigParser.RawConfigParser()
    config.read('config/%s' % audio_config_file)

  def __init__(self, audio_config_file):
    if __debug__:
      print "Initiating audio"
    self.init_config(audio_config_file)

  def TriggerSound(self, data):
    if __debug__:
      print "Playing %s" % data
    audio_file = "./sounds/" + data + ".mp3"
    mixer.init()
    if __debug__:
      print "Init mixer"
    mixer.music.load(audio_file) # % (audio_dir, data))
    if __debug__:
      print "%s Loaded" % audio_file
    mixer.music.play()
    if __debug__:
      print "Play"
    

  def ListSounds(self):
    return "Sounds available:"


