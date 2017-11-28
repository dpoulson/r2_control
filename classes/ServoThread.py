#!/usr/bin/python
import threading
import Queue
import time
from Adafruit_PWM_Servo_Driver import PWM

tick_duration = 100

q = Queue

Address = 0x40
Max = 0
Min = 0
Current = 0
Home = 0
Channel = 0


class ServoThread(threading.Thread):
    def __init__(self, Address, Max, Min, Home, Channel, q):
        if __debug__:
            print "Initialising thread"
        self.q = q
        self.Address = Address
        self.Max = Max
        self.Min = Min
        self.Home = Home
        self.Current = Min
        self.Channel = Channel
        threading.Thread.__init__(self)
        self.i2c = PWM(Address, debug=False)
        self.i2c.setPWMFreq(60)
        return

    def run(self):
        if __debug__:
            print "Starting Thread"
        while True:
            command = self.q.get()
            position = command[0]
            duration = command[1]
            if position > 1 or position < 0:
                print "Invalid position (%s)" % (position)
            else:
                actual_position = int(((self.Max - self.Min) * position) + self.Min)
            if __debug__:
                print "Duration: %s " % duration
            if duration > 0:
                ticks = (duration * 1000) / tick_duration
                tick_position_shift = (actual_position - self.Current) / float(ticks)
                tick_actual_position = self.Current + tick_position_shift
                if __debug__:
                    print "Ticks:%s  Current Position: %s Position shift: %s Starting Position: %s End Position %s" % (
                    ticks, self.Current, tick_position_shift, tick_actual_position, actual_position)
                for x in range(0, ticks):
                    if __debug__:
                        print "Tick: %s Position: %s" % (x, tick_actual_position)
                    self.i2c.setPWM(self.Channel, 0, int(tick_actual_position))
                    tick_actual_position += tick_position_shift
                if __debug__:
                    print "Finished move: Position: %s" % tick_actual_position
            else:
                if __debug__:
                    print "Setting servo %s(%s) to position = %s(%s)" % (
                    "test", self.Channel, actual_position, position)
                self.i2c.setPWM(self.Channel, 0, actual_position)
            # Save current position of servo
            if __debug__:
                print "Servo move finished. Servo.name: %s ServoCurrent %s Tick %s" % (
                "Test", self.Current, actual_position)
            self.Current = actual_position
            if __debug__:
                print "New current: %s" % self.Current
            time.sleep(0.3)
            self.i2c.setPWM(self.Channel, 4096, 0)
        return
