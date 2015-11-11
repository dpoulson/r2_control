#!/usr/bin/python
import threading
import Queue
import time
import csv
import urllib2

script = ""

keywords = ['dome', 'body', 'lights', 'sound', 'sleep', 'end']

class ScriptThread(threading.Thread):

  def __init__(self, script):
    print "Initialising script thread"
    self.script = script
    self._stopevent = threading.Event()
    threading.Thread.__init__(self)
    return

  def run(self):
    print "Starting script thread %s" % self.script
    while not self._stopevent.isSet():
      ifile = open('scripts/%s' % self.script, "rb")
      reader = csv.reader(ifile)
      for row in reader:
        self.parse_row(row)
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
        if row[0] == "end":
          self._stopevent.set()
    return
