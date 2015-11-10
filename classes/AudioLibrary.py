
import ConfigParser
import os, sys
import thread
import time
import glob
import collections
import random
from pygame import mixer # Load the required library

Random_Sounds = ['alarm', 'happy', 'hum', 'misc', 'quote', 'razz', 'sad', 'sent', 'ooh', 'proc', 'whistle']
Random_Files = ['ALARM', 'Happy', 'HUM__', 'MISC_', 'Quote', 'RAZZ_', 'Sad__', 'SENT_', 'OOH__', 'PROC_', 'WHIST']

class AudioLibrary :


  def init_config(self, sounds_dir):
    "Load in CSV of Audio definitions"
    if __debug__:
      print "Setting sounds directory to %s" % sounds_dir

  def __init__(self, sounds_dir):
    if __debug__:
      print "Initiating audio"
    self.init_config(sounds_dir)

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

  def TriggerRandomSound(self, data):
    idx=Random_Sounds.index(data)
    prefix=Random_Files[idx]
    print "Random index: %s, prefix=%s" % (idx, prefix)
    file_list=glob.glob("./sounds/"+prefix+"*.mp3")
    file_idx=len(file_list)-1
    audio_file = file_list[random.randint(0, file_idx)]
    if __debug__:
      print "Playing %s" % data
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
    files = ', '.join(glob.glob("./sounds/*.mp3"))
    files = files.replace("./sounds/" ,"", -1)
    files = files.replace(".mp3", "", -1)
    return files

  def ListRandomSounds(self):
    types = ', '.join(Random_Sounds)
    return types




