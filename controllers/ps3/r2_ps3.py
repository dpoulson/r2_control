#!/usr/bin/python
import pygame
import requests
import csv
import os
import sys
import time
import datetime
import argparse
from cStringIO import StringIO
from collections import defaultdict
from SabertoothPacketSerial import SabertoothPacketSerial

import signal

def sig_handler(signal, frame):
    print('Cleaning Up')
    sys.exit(0)

signal.signal(signal.SIGINT, sig_handler)

##########################################################
# Set variables

# How often should the script send a keepalive (s)
keepalive = 0.25

# Speed factor. This multiplier will define the max value to be sent to the drive system. 
# eg. 0.5 means that the value of the joystick position will be halved
# Should never be greater than 1
speed_fac = 0.35

# Invert. Does the drive need to be inverted. 1 = no, -1 = yes
invert = -1

drive_mod = speed_fac * invert

# Deadband: the amount of deadband on the sticks
deadband = 0.2

# PWM Frequency
freq = 60
# Exponential curve constant. Set this to 0 < curve < 1 to give difference response curves for axis
curve = 0.6

dome_speed = 0
accel_rate = 0.025
dome_stick = 0

# Set Axis definitions
PS3_AXIS_LEFT_VERTICAL = 1
PS3_AXIS_LEFT_HORIZONTAL = 0
PS3_AXIS_RIGHT_HORIZONTAL = 3

baseurl = "http://localhost:5000/"

os.environ["SDL_VIDEODRIVER"] = "dummy"

################################################################################
################################################################################
# Custom Functions

########################################
# Clamp a value between a min and max
def clamp(n, minn, maxn):
    if n < minn:
        print "Clamping min"
        return minn
    elif n > maxn:
        print "Clamping max " + str(n)
        return maxn
    else:
        return n

########################################
# Send command to the dome
def driveDome(speed_wanted):
    global dome_speed
    speed_actual = 0
    #speed_wanted = clamp(speed_wanted, -1, 1)
    if speed_wanted < deadband and speed_wanted > -deadband:
        speed_wanted = 0
    if speed_wanted > dome_speed:
        speed_actual = dome_speed + accel_rate
    elif speed_wanted < dome_speed:
        speed_actual = dome_speed - accel_rate
#    speed_actual = clamp(speed_actual, -1, 1)
    dome_speed = speed_actual

    # tell servo what to do
    if __debug__:
        print "speed %5.5f : Actual speed: %5.5f" % (
        speed_wanted, speed_actual)
    dome.driveCommand(speed_actual)

######################################
# Shutdown R2's drive - kill all motion
def shutdownR2():
   if __debug__:
      print "Running shutdown procedure"
   if __debug__:
      print "Stopping all motion..."
      print "...Setting drive to 0"
   drive.driveCommand(0)
   if __debug__:
      print "...Setting turn to 0"
   drive.turnCommand(0)
   if __debug__:
      print "...Setting dome to 0"
   dome.driveCommand(0)

   if __debug__:
      print "Disable drives"
   url = baseurl + "servo/body/ENABLE_DRIVE/0/0"
   try:
      r = requests.get(url)
   except:
      print "Fail...."
 
   if __debug__:
      print "Disable dome"
   url = baseurl + "servo/body/ENABLE_DOME/0/0"
   try:
      r = requests.get(url)
   except:
      print "Fail...."

   if __debug__:
      print "Bad motivator"
   # Play a sound to alert about a problem
      url = baseurl + "audio/MOTIVATR"
   try:
      r = requests.get(url)
   except:
      print "Fail...."

   f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " ****** PS3 Shutdown ******\n")

#######################################################

parser = argparse.ArgumentParser(description='PS3 controller for r2_control.');
parser.add_argument('--curses', '-c', action="store_true", dest="curses", required=False, default=False,
        help='Output in a nice readable format')
args = parser.parse_args()
print(args)

#### Open a log file
#f = open('/home/pi/r2_control/logs/ps3.log', 'at')
f = open('test.log', 'at')
f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : ****** ps3 started ******\n")
f.flush()

drive = SabertoothPacketSerial()
dome = SabertoothPacketSerial(address=129, type='Syren', port='/dev/ttyUSB0')
drive.driveCommand(0)
drive.turnCommand(0)

pygame.display.init()

while True:
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

url = baseurl + "audio/Happy007"
try:
    r = requests.get(url)
except:
    print "Fail...."

f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : System Initialised \n")
f.flush()

last_command = time.time()
joystick = True

# Main loop
while (joystick):
    global previous
    global last_command
    global speed_fac
    global dome_stick
    driveDome(dome_stick)
    if time.time() - last_command > keepalive: 
        if __debug__:
            print "Last command sent greater than %s ago, doing keepAlive" % keepalive
        drive.keepAlive()
        #dome.keepAlive()
        # Check js0 still there
        if (os.path.exists('/dev/input/js0')): 
           if __debug__:
              print "Joystick still there...."
        else:
           print "No joystick"
           joystick = False
        # Check for no shutdown file
        if (os.path.exists('/home/pi/r2_control/controllers/.shutdown')):
            print "Shutdown file is there"
            joystick = False
        last_command = time.time()
    try:
        events = pygame.event.get()
    except:
        if __debug__:
            print "Something went wrong!"
        shutdownR2()
	sys.exit(0)
    for event in events:
        if event.type == pygame.JOYBUTTONDOWN:
            buf = StringIO()
            for i in range(buttons):
                button = j.get_button(i)
                buf.write(str(button))
            combo = buf.getvalue()
            if __debug__:
                print "Buttons pressed: %s" % combo
            # Special key press (All 4 plus triangle) to increase speed of drive
            if combo == "00001111000000001":
              if __debug__:
                 print "Incrementing drive speed"
              # When detected, will increment the speed_fac by 0.5 and give some audio feedback.
              speed_fac += 0.05
              if speed_fac > 1:
                 speed_fac = 1
              if __debug__:
                 print "*** NEW SPEED %s" % speed_fac
              drive_mod = speed_fac * invert
              f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Speed Increase : " + str(speed_fac) + " \n")
              url = baseurl + "audio/Happy006"
              try:
                 r = requests.get(url)
              except:
                 print "Fail...."
            # Special key press (All 4 plus X) to decrease speed of drive
            if combo == "00001111000000010":
              if __debug__:
                 print "Decrementing drive speed"
              # When detected, will increment the speed_fac by 0.5 and give some audio feedback.
              speed_fac -= 0.05
              if speed_fac < 0.2:
                 speed_fac = 0.2
              drive_mod = speed_fac * invert
              f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Speed Decrease : " + str(speed_fac) + " \n")
              url = baseurl + "audio/Sad__019"
              try:
                 r = requests.get(url)
              except:
                 print "Fail...."
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
            previous = ""
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == PS3_AXIS_LEFT_VERTICAL:
                if __debug__:
                    print "Value (Drive): %s : Speed Factor : %s" % (event.value, speed_fac)
                f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Forward/Back : " + str(event.value*speed_fac) + "\n")
                f.flush
                drive.driveCommand(event.value*drive_mod)
                last_command = time.time()
            elif event.axis == PS3_AXIS_LEFT_HORIZONTAL:
                if __debug__:
                    print "Value (Steer): %s" % event.value
                f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Left/Right : " + str(event.value*speed_fac) + "\n")
                f.flush
                drive.turnCommand(event.value*drive_mod)
                last_command = time.time()
            elif event.axis == PS3_AXIS_RIGHT_HORIZONTAL:
                if __debug__:
                    print "Value (Dome): %s" % event.value
                #dome_stick = ((curve * (event.value ** 3)) + ((1 - curve) * event.value))
                #dome.driveCommand(event.value)
                dome_stick = event.value

# If the while loop quits, make sure that the motors are reset.
if __debug__:
    print "Exited main loop"
shutdownR2()


