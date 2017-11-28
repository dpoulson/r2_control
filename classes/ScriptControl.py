#!/usr/bin/python
# ===============================================================================
# Copyright (C) 2013 Darren Poulson
#
# This file is part of R2_Control.
#
# R2_Control is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# R2_Control is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with R2_Control.  If not, see <http://www.gnu.org/licenses/>.
# ===============================================================================

from ScriptThread import ScriptThread
import glob
import collections


class ScriptControl:
    Scripts = collections.namedtuple('Script', 'name, script_id, thread')

    def __init__(self, script_dir):
        self.running_scripts = []
        self.script_id = 1
        self.script_dir = script_dir
        if __debug__:
            print "Starting script object with path: %s" % script_dir

    def list(self):
        files = ', '.join(glob.glob("./scripts/*.scr"))
        files = files.replace("./scripts/", "", -1)
        files = files.replace(".scr", "", -1)
        return files

    def list_running(self):
        message = ""
        for script in self.running_scripts:
            message += "%s:%s\n" % (script.script_id, script.name)
        return message

    def stop_script(self, kill_id):
        idx = 0
        if __debug__:
            print "Trying to stop script ID %s" % kill_id
        for script in self.running_scripts:
            if (int(script.script_id) == int(kill_id)) or (script.name == kill_id):
                script.thread.stop()
                self.running_scripts.pop(idx)
            idx += 1
        return "Ok"

    def stop_all(self):
        idx = 0
        if __debug__:
            print "Trying to stop all scripts"
        for script in self.running_scripts:
            self.stop_script(script.script_id)
        idx += 1
        return "Ok"

    def run_script(self, script, loop):
        idx = 0
        current_id = 0
        self.running_scripts.append(
            self.Scripts(name=script, script_id=self.script_id, thread=ScriptThread(script, loop)))
        if __debug__:
            print "ID %s" % self.script_id
        for scripts in self.running_scripts:
            if scripts.script_id == self.script_id:
                current_id = scripts.script_id
                scripts.thread.daemon = True
                scripts.thread.start()
        if __debug__:
            print "Starting script %s" % script
        if loop == "1":
            print "Looping"
        else:
            for script in self.running_scripts:
                if int(script.script_id) == int(current_id):
                    self.running_scripts.pop(idx)
                idx += 1
        self.script_id += 1
        return "Ok"
