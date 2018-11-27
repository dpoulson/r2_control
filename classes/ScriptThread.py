#!/usr/bin/python
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import threading
import time
import random
import csv
import urllib.request, urllib.error, urllib.parse

script = ""
loop = False
lock = threading.Lock()

keywords = ['dome', 'body', 'lights', 'sound', 'sleep', 'flthy']


class ScriptThread(threading.Thread):
    def __init__(self, script, loop):
        print("Initialising script thread with looping set to: %s" % loop)
        self.script = script
        self.loop = int(loop)
        self._stopevent = threading.Event()
        threading.Thread.__init__(self)
        return

    def run(self):
        print("Starting script thread %s" % self.script)
        while not self._stopevent.isSet():
            ifile = open('scripts/%s.scr' % self.script, "rb")
            reader = csv.reader(ifile)
            if self.loop != 1:
                with lock:
                    print("....With lock")
                    for row in reader:
                        self.parse_row(row)
            else:
                for row in reader:
                    self.parse_row(row)
            if self.loop == 1:
                if __debug__:
                    print("Looping...")
            else:
                self._stopevent.set()
        print("Stopping script %s" % self.script)
        return

    def stop(self, timeout=None):
        if __debug__:
            print("Stop called on %s" % self.script)
        self._stopevent.set()
        # threading.Thread.join(self, timeout)

    def parse_row(self, row):
        print("Row: %s" % row)
        if len(row) != 0:
            if row[0] in keywords:
                if row[0] == "sleep":
                    if row[1] == "random":
                        stime = random.randint(int(row[2]), int(row[3]))
                        if __debug__:
                            print("Random sleep time: %s" % stime)
                        time.sleep(float(stime))
                    else:
                        time.sleep(float(row[1]))
                if row[0] == "body":
                    if row[1] == "all":
                        urllib.request.urlopen("http://localhost:5000/servo/body/%s" % row[2])
                    else:
                        urllib.request.urlopen("http://localhost:5000/servo/body/%s/%s/%s" % (row[1], row[2], row[3]))
                if row[0] == "dome":
                    if row[1] == "all":
                        urllib.request.urlopen("http://localhost:5000/servo/dome/%s" % row[2])
                    else:
                        urllib.request.urlopen("http://localhost:5000/servo/dome/%s/%s/%s" % (row[1], row[2], row[3]))
                if row[0] == "sound":
                    if row[1] == "random":
                        urllib.request.urlopen("http://localhost:5000/audio/random/%s" % row[2])
                    else:
                        urllib.request.urlopen("http://localhost:5000/audio/%s" % row[1])
                if row[0] == "flthy":
                    urllib.request.urlopen("http://localhost:5000/flthy/raw/%s" % row[1])
                if row[0] == "smoke":
                    urllib.request.urlopen("http://localhost:5000/smoke/on/%s" % row[1])
        return

