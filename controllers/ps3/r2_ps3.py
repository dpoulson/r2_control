#!/usr/bin/python
import pygame
import requests
import csv
import os
import sys
import time
import datetime
from cStringIO import StringIO
from collections import defaultdict
from SabertoothPacketSerial import SabertoothPacketSerial

sys.path.append('/home/pi/r2_control/classes/')
from Adafruit_PWM_Servo_Driver import PWM

#### Open a log file
f = open('/home/pi/r2_control/logs/ps3.log', 'at')
f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : ****** ps3 started ******\n")
f.flush()

drive = SabertoothPacketSerial()
drive.driveCommand(0)
drive.turnCommand(0)



# PWM Frequency
freq = 60
# Exponential curve constant. Set this to 0 < curve < 1 to give difference response curves for axis
curve = 0.8

# Set Axis definitions
PS3_AXIS_LEFT_VERTICAL = 1
PS3_AXIS_LEFT_HORIZONTAL = 0
PS3_AXIS_RIGHT_HORIZONTAL = 2

# Channel numbers on PWM controller
SERVO_DOME = 15
SERVO_DRIVE = 14
SERVO_STEER = 13

# PWM ranges
# 245 will give full range on a Sabertooth controller (ie, 1000ms and 2000ms, with 1500ms as the centerpoint)
SERVO_FULL_CW = 300
SERVO_STOP = 380
DOME_FULL_CW = 330
DOME_STOP = 425


baseurl = "http://localhost:5000/"

os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.display.init()

while True:
    f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Waiting for joystick \n")
    f.flush()
    pygame.joystick.quit()
    pygame.joystick.init()
    num_joysticks = pygame.joystick.get_count()
    if __debug__:
        print "Waiting for joystick... (count: %s)" % num_joysticks
    if num_joysticks != 0:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Joystick found \n")
        f.flush()
        break
    time.sleep(5)

pygame.init()
size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
if __debug__:
    print "Framebuffer size: %d x %d" % (size[0], size[1])

j = pygame.joystick.Joystick(0)
j.init()
buttons = j.get_numbuttons()

# Read in key combos from csv file
keys = defaultdict(list)
with open('keys.csv', mode='r') as infile:
    reader = csv.reader(infile)
    for row in reader:
        if __debug__:
            print "Row: %s | %s | %s" % (row[0], row[1], row[2])
        keys[row[0]].append(row[1])
        keys[row[0]].append(row[2])

keys.items()


def driveDome(channel, speed):
    pulse = DOME_STOP
    speed_adj = ((curve * (speed ** 3)) + ((1 - curve) * speed))
    if speed != 0:
        # Use curve variable to decrease sensitivity at low end.
        pulse = (speed_adj * (DOME_STOP - DOME_FULL_CW)) + DOME_STOP

    period = 1 / float(freq)
    bit_duration = period / 4096
    pulse_duration = bit_duration * pulse * 1000000

    # tell servo what to do
    if __debug__:
        print "Channel %s : speed %5.5f : Adjusted speed: %5.5f : pulse %5.5f : duration %5.5f" % (
        channel, speed, speed_adj, pulse, pulse_duration)
    pwm.setPWM(channel, 0, int(pulse))


print "Initialised... entering main loop..."

pwm = PWM(0x40, debug=True)
pwm.setPWMFreq(freq)  # Set frequency to 60 Hz

url = baseurl + "audio/Happy007"
try:
    r = requests.get(url)
except:
    print "Fail...."

f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : System Initialised \n")
f.flush()

# Main loop
while True:
    global previous
    try:
        events = pygame.event.get()
    except:
        if __debug__:
            print "Something went wrong!"
        drive.driveCommand(0)
        drive.turnCommand(0)
        driveDome(SERVO_DOME, 0)
        # Send motor disable command
        url = baseurl + "servo/body/ENABLE_DRIVE/0/0"
        try:
            r = requests.get(url)
        except:
            print "Fail...."
        # Play a sound to alert about a problem
        url = baseurl + "audio/MOTIVATR"
        try:
            r = requests.get(url)
        except:
            print "Fail...."
    for event in events:
        if event.type == pygame.JOYBUTTONDOWN:
            buf = StringIO()
            for i in range(buttons):
                button = j.get_button(i)
                buf.write(str(button))
            combo = buf.getvalue()
            if __debug__:
                print "Buttons pressed: %s" % combo
            # Special key press (Select) to switch speeds of drive
            # if combo == "1000000000000000000"
            #   if __debug__:
            #      print "Switching drive speeds"
            #   # When detected, will switch between two speeds. Also, will give audio feedback
            #   print "Do shit"
            try:
                newurl = baseurl + keys[combo][0]
                f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Button Down event : " + combo + "," + keys[combo][0] +" \n")
                f.flush() 
                if __debug__:
                    print "Would run: %s" % keys[combo]
                    print "URL: %s" % newurl
                try:
                    r = requests.get(newurl)
                except:
                    print "No connection"
            except:
                if __debug__:
                    print "No combo (pressed)"
            previous = combo
        if event.type == pygame.JOYBUTTONUP:
            if __debug__:
                print "Buttons released: %s" % previous
            try:
                newurl = baseurl + keys[previous][1]
                f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Button Up event : " + previous + "," + keys[previous][1] + "\n")
                f.flush()
                if __debug__:
                    print "Would run: %s" % keys[previous][1]
                    print "URL: %s" % newurl
                try:
                    r = requests.get(newurl)
                except:
                    print "No connection"
            except:
                if __debug__:
                    print "No combo (released)"
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == PS3_AXIS_LEFT_VERTICAL:
                if __debug__:
                    print "Value (Drive): %s" % event.value
                drive.driveCommand(event.value)
            elif event.axis == PS3_AXIS_LEFT_HORIZONTAL:
                if __debug__:
                    print "Value (Steer): %s" % event.value
                drive.turnCommand(event.value)
            elif event.axis == PS3_AXIS_RIGHT_HORIZONTAL:
                if __debug__:
                    print "Value (Dome): %s" % event.value
                newvalue = ((curve * (event.value ** 3)) + ((1 - curve) * event.value))
                driveDome(SERVO_DOME, newvalue)

# If the while loop quits, make sure that the motors are reset.
drive.driveCommand(0)
drive.turnCommand(0)
driveDome(SERVO_DOME, 0)
# Turn off motors
url = baseurl + "servo/body/ENABLE_DRIVE/0/0"
try:
    r = requests.get(url)
except:
    print "Fail...."
url = baseurl + "servo/body/ENABLE_DOME/0/0"
try:
    r = requests.get(url)
except:
    print "Fail...."
f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " ****** PS3 Shutdown ******\n")

