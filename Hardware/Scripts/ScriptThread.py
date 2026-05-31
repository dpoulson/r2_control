""" Script Thread """
import threading
import time
import random
import csv
import urllib.request
import urllib.error
import urllib.parse
import json

script = ""
loop = False
lock = threading.Lock()

keywords = ['dome', 'body', 'sound', 'sleep', 'flthy', 'rseries', 'psi_matrix', 'smoke', 'autodome', 'script']


class ScriptThread(threading.Thread):
    def __init__(self, script, loop):
        print(f"Initialising script thread with looping set to: {loop}")
        self.script = script
        self.loop = int(loop)
        self._stopevent = threading.Event()
        self.contents = ""
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

    def _trigger_api(self, url, data=None, headers=None):
        try:
            if data is not None:
                req = urllib.request.Request(url, data=data, headers=headers or {})
                urllib.request.urlopen(req)
            else:
                urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            print(f"API request failed with HTTP status {e.code}: {e.reason} ({url})")
        except urllib.error.URLError as e:
            print(f"API request connection failed: {e.reason} ({url})")
        except Exception as e:
            print(f"Unexpected error triggering API: {e} ({url})")

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
                        self._trigger_api(f"http://localhost:5000/body/{row[2]}")
                    else:
                        self._trigger_api(f"http://localhost:5000/body/{row[1]}/{row[2]}/{row[3]}")
                elif row[0] == "dome":
                    if row[1] == "all":
                        self._trigger_api(f"http://localhost:5000/dome/{row[2]}")
                    else:
                        self._trigger_api(f"http://localhost:5000/dome/{row[1]}/{row[2]}/{row[3]}")
                elif row[0] == "sound":
                    if row[1] == "random":
                        self._trigger_api(f"http://localhost:5000/audio/random/{row[2]}")
                    else:
                        self._trigger_api(f"http://localhost:5000/audio/{row[1]}")
                elif row[0] == "flthy":
                    self._trigger_api(f"http://localhost:5000/flthy/raw/{row[1]}")
                elif row[0] == "smoke":
                    self._trigger_api(f"http://localhost:5000/smoke/on/{row[1]}")
                elif row[0] == "psi_matrix":
                    self._trigger_api(f"http://localhost:5000/psi_matrix/raw/{row[1]}")
                elif row[0] == "rseries":
                    self._trigger_api(f"http://localhost:5000/rseries/raw/{row[1]}")
                elif row[0] == "autodome":
                    action = row[1]
                    if action == "spin":
                        direction = row[2]
                        speed = float(row[3])
                        if len(row) > 4:
                            duration = float(row[4])
                            self._trigger_api(
                                "http://localhost:5000/autodome/spin",
                                data=json.dumps({"direction": direction, "speed": speed}).encode('utf-8'),
                                headers={'Content-Type': 'application/json'}
                            )
                            time.sleep(duration)
                            self._trigger_api(
                                "http://localhost:5000/autodome/spin",
                                data=json.dumps({"direction": direction, "speed": 0.0}).encode('utf-8'),
                                headers={'Content-Type': 'application/json'}
                            )
                        else:
                            self._trigger_api(
                                "http://localhost:5000/autodome/spin",
                                data=json.dumps({"direction": direction, "speed": speed}).encode('utf-8'),
                                headers={'Content-Type': 'application/json'}
                            )
                    elif action == "stop":
                        self._trigger_api(
                            "http://localhost:5000/autodome/spin",
                            data=json.dumps({"direction": "left", "speed": 0.0}).encode('utf-8'),
                            headers={'Content-Type': 'application/json'}
                        )
                    elif action == "random":
                        enabled = (row[2].lower() == "on" or row[2].lower() == "true")
                        self._trigger_api(
                            "http://localhost:5000/autodome/random",
                            data=json.dumps({"enabled": enabled}).encode('utf-8'),
                            headers={'Content-Type': 'application/json'}
                        )
                    elif action == "position":
                        angle = float(row[2])
                        self._trigger_api(
                            "http://localhost:5000/autodome/position",
                            data=json.dumps({"angle": angle}).encode('utf-8'),
                            headers={'Content-Type': 'application/json'}
                        )
                elif row[0] == "script":
                    script_name = row[1]
                    action = "run"
                    if len(row) > 2:
                        action = row[2]
                        
                    if action == "stop":
                        self._trigger_api(f"http://localhost:5000/scripts/stop/{script_name}")
                    else:
                        loop_val = "1" if action == "1" else "0"
                        self._trigger_api(f"http://localhost:5000/scripts/{script_name}/{loop_val}")
                else:
                    if __debug__:
                        print("Do not understand")
        return
