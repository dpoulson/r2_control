
import ConfigParser
import os, sys
import thread
import time
import glob
import collections
import random
from pygame import mixer # Load the required library

Random_Sounds = ['alarm', 'happy', 'hum', 'misc', 'quote', 'razz', 'sad', 'sent', 'ooh', 'proc', 'whistle', 'scream']
Random_Files = ['ALARM', 'Happy', 'HUM__', 'MISC_', 'Quote', 'RAZZ_', 'Sad__', 'SENT_', 'OOH__', 'PROC_', 'WHIST', 'SCREA']


class AudioLibrary :


  def init_config(self, sounds_dir):
    "Load in CSV of Audio definitions"
    if __debug__:
      print "Setting sounds directory to %s" % sounds_dir

  def __init__(self, sounds_dir):
    if __debug__:
      print "Initiating audio"
    self.init_config(sounds_dir)
    mixer.init()
    mixer.music.set_volume(0.1)

  def TriggerSound(self, data):
    if __debug__:
      print "Playing %s" % data
    audio_file = "./sounds/" + data + ".mp3"
   # mixer.init()
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
  
  def ShowVolume(self):
    cur_vol = str(mixer.music.get_volume())
    return cur_vol    

  def SetVolume(self, level):
    if level == "up":
      if __debug__:
        print "Increasing volume"
      new_level = mixer.music.get_volume() + 0.025
    elif level == "down":
      if __debug__:
        print "Decreasing volume"
      new_level = mixer.music.get_volume() - 0.025
    else:
      if __debug__:
        print "Volume level explicitly states"
      new_level = level
    if new_level < 0:
      new_level = 0
    if __debug__:
      print "Setting volume to: %s" % new_level
    mixer.music.set_volume(float(new_level)) 
    return "Ok"

