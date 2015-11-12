#!/usr/bin/python
import threading
import Queue
import time
import csv
import urllib2

script = ""
loop = False

keywords = ['dome', 'body', 'lights', 'sound', 'sleep']

class ScriptThread(threading.Thread):

  def __init__(self, script, loop):
    print "Initialising script thread"
    self.script = script
    self.loop = int(loop)
    self._stopevent = threading.Event()
    threading.Thread.__init__(self)
    return

  def run(self):
    print "Starting script thread %s" % self.script
    while not self._stopevent.isSet():
      ifile = open('scripts/%s.scr' % self.script, "rb")
      reader = csv.reader(ifile)
      for row in reader:
        self.parse_row(row)
      if self.loop == 1:
        if __debug__:
          print "Looping..."
      else:
        self._stopevent.set()
    print "Stopping script %s" % self.script  
    return

  def stop(self, timeout=None):
    if __debug__:
      print "Stop called on %s" % self.script
    self._stopevent.set()
    #threading.Thread.join(self, timeout)

  def parse_row(self, row):
    print "Row: %s" % row
    if len(row) != 0:
      if row[0] in keywords:
        if row[0] == "sleep":
          time.sleep(float(row[1]))
        if row[0] == "body":
          urllib2.urlopen("http://localhost:5000/servo/%s/%s/%s" % ( row[1], row[2], row[3] ) )
        if row[0] == "sound":
          if row[1] == "random":
            urllib2.urlopen("http://localhost:5000/audio/random/%s" % row[2] )
          else:
            urllib2.urlopen("http://localhost:5000/audio/%s" % row[1] )
    return
