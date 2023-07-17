""" Script Thread """
import threading
import time
import random
import csv
import urllib.request
import urllib.error
import urllib.parse
from future import standard_library
standard_library.install_aliases()

script = ""
loop = False
lock = threading.Lock()

keywords = ['dome', 'body', 'lights', 'sound', 'sleep', 'flthy', 'rseries', 'psi_matrix']


class ScriptThread(threading.Thread):
    def __init__(self, script, loop):
        print(f"Initialising script thread with looping set to: {loop}")
        self.script = script
        self.loop = int(loop)
        self._stopevent = threading.Event()
        threading.Thread.__init__(self)
        return

    def run(self):
        print(f"Starting script thread {self.script}")
        while not self._stopevent.isSet():
            ifile = open('scripts/%s.scr' % self.script, "rt", encoding="utf-8")
            reader = csv.reader(ifile)
            if self.loop != 1:
                with lock:
                    print("....With lock")
                    self.contents = list(reader)
            else:
                self.contents = list(reader)
            for row in self.contents:
                self.parse_row(row)
            if self.loop == 1:
                if __debug__:
                    print("Looping...")
            else:
                self._stopevent.set()
        print(f"Stopping script {self.script}")
        return

    def stop(self, timeout=None):
        if __debug__:
            print(f"Stop called on {self.script}")
        self._stopevent.set()
        # threading.Thread.join(self, timeout)

    def parse_row(self, row):
        print(f"Row: {row}")
        if len(row) != 0:
            if row[0] in keywords:
                if row[0] == "sleep":
                    if row[1] == "random":
                        stime = random.randint(int(row[2]), int(row[3]))
                        if __debug__:
                            print(f"Random sleep time: {stime}")
                        time.sleep(float(stime))
                    else:
                        time.sleep(float(row[1]))
                elif row[0] == "body":
                    if row[1] == "all":
                        urllib.request.urlopen(f"http://localhost:5000/body/{row[2]}")
                    else:
                        urllib.request.urlopen(f"http://localhost:5000/body/{row[1]}/{row[2]}/{row[3]}")
                elif row[0] == "dome":
                    if row[1] == "all":
                        urllib.request.urlopen(f"http://localhost:5000/dome/{row[2]}")
                    else:
                        urllib.request.urlopen(f"http://localhost:5000/dome/{row[1]}/{row[2]}/{row[3]}")
                elif row[0] == "sound":
                    if row[1] == "random":
                        urllib.request.urlopen(f"http://localhost:5000/audio/random/{row[2]}")
                    else:
                        urllib.request.urlopen(f"http://localhost:5000/audio/{row[1]}")
                elif row[0] == "flthy":
                    urllib.request.urlopen(f"http://localhost:5000/flthy/raw/{row[1]}")
                elif row[0] == "smoke":
                    urllib.request.urlopen(f"http://localhost:5000/smoke/on/{row[1]}")
                elif row[0] == "psi_matrix":
                    urllib.request.urlopen(f"http://localhost:5000/psi_matrix/raw/{row[1]}")
                elif row[0] == "rseries":
                    urllib.request.urlopen(f"http://localhost:5000/rseries/raw/{row[1]}")
                else:
                    if __debug__:
                        print("Do not understand")
        return
