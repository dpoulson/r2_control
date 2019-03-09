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

from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
from .ServoThread import ServoThread
from queue import Queue
import csv
import collections
standard_library.install_aliases()
from builtins import object


tick_duration = 100


class ServoControl(object):
    # servo_list = [] # All servos, listed here.

    Servo = collections.namedtuple('Servo', 'name, queue, thread')

    def init_config(self, address, servo_config_file):
        """Load in CSV of Servo definitions"""
        ifile = open('config/%s' % servo_config_file, "rt")
        reader = csv.reader(ifile)
        for row in reader:
            servo_channel = int(row[0])
            servo_name = row[1]
            servo_Min = int(row[2])
            servo_Max = int(row[3])
            servo_home = int(row[4])
            queue = Queue()
            self.servo_list.append(self.Servo(name=servo_name, queue=queue,
                                              thread=ServoThread(address, servo_Max, servo_Min, servo_home,
                                                                             servo_channel, queue)))
            for servo in self.servo_list:
                if servo.name == servo_name:
                    servo.thread.daemon = True
                    servo.thread.start()
            if __debug__:
                print("Added servo: %s %s %s %s %s" % (servo_channel, servo_name, servo_Min, servo_Max, servo_home))
        ifile.close()
        self.close_all_servos(0)

    def __init__(self, address, servo_config_file):
        self.servo_list = []
        self.init_config(address, servo_config_file)

    def list_servos(self):
        message = ""
        if __debug__:
            print("Listing servos for address:")
        for servo in self.servo_list:
            message += "%s\n" % servo.name
        return message

    def close_all_servos(self, duration):
        try:
            duration = int(duration)
        except:
            print("Duration is not an int")
            duration = 0
        if __debug__:
            print("Closing all servos")
        for servo in self.servo_list:
            servo.queue.put([0, duration])
        return

    def open_all_servos(self, duration):
        try:
            duration = int(duration)
        except:
            print("Duration is not an int")
            duration = 0
        if __debug__:
            print("Opening all servos")
        for servo in self.servo_list:
            servo.queue.put([1, duration])
        return

    # Send a command over i2c to turn a servo to a given position (percentage) over a set duration (seconds)
    # def servo_command(self, servo_name, position, duration):
    def servo_command(self, servo_name, position, duration):
        if __debug__:
            print("Moving %s to %s over duration %s" % (servo_name, position, duration))
        current_servo = []
        try:
            position = float(position)
        except:
            print("Position not a float")
        try:
            duration = int(duration)
        except:
            print("Duration is not an int")
        for servo in self.servo_list:
            if servo.name == servo_name:
                current_servo = servo
        current_servo.queue.put([position, duration])

