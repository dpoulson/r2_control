#!/usr/bin/python
from __future__ import print_function
from future import standard_library
from builtins import str
from builtins import range
import pygame
import requests
import csv
import configparser
import os
import sys
import time
import datetime
import argparse
from io import StringIO
from collections import defaultdict
from SabertoothPacketSerial import SabertoothPacketSerial
import signal

standard_library.install_aliases()


def sig_handler(signal, frame):
    print('Cleaning Up')
    sys.exit(0)


signal.signal(signal.SIGINT, sig_handler)

##########################################################
# Load config
_configfile = 'psmove.cfg'
_config = configparser.SafeConfigParser({'log_file': '/home/pi/r2_control/logs/psmove.log',
                                         'baseurl': 'http://localhost:5000/',
                                         'keepalive': 0.25,
                                         'speed_fac': 0.35,
                                         'invert': -1,
                                         'accel_rate': 0.025,
                                         'curve': 0.6,
                                         'deadband': 0.2
                                         })

_config.add_section('Dome')
_config.set('Dome', 'address', '129')
_config.set('Dome', 'type', 'Syren')
_config.set('Dome', 'port', '/dev/ttyUSB0')
_config.add_section('Drive')
_config.set('Drive', 'address', '128')
_config.set('Drive', 'type', 'Sabertooth')
_config.set('Drive', 'port', '/dev/ttyACM0')
_config.add_section('Axis')
_config.set('Axis', 'drive', '1')
_config.set('Axis', 'turn', '0')
_config.set('Axis', 'dome', '3')
_config.read(_configfile)

if not os.path.isfile(_configfile):
    print("Config file does not exist")
    with open(_configfile, 'wb') as configfile:
        _config.write(configfile)

mainconfig = _config.defaults()

##########################################################
# Set variables
# Log file location
log_file = mainconfig['log_file']

# How often should the script send a keepalive (s)
keepalive = float(mainconfig['keepalive'])

# Speed factor. This multiplier will define the max value to be sent to the drive system.
# eg. 0.5 means that the value of the joystick position will be halved
# Should never be greater than 1
speed_fac = float(mainconfig['speed_fac'])

# Invert. Does the drive need to be inverted. 1 = no, -1 = yes
invert = int(mainconfig['invert'])

drive_mod = speed_fac * invert

# Deadband: the amount of deadband on the sticks
deadband = float(mainconfig['deadband'])

# Exponential curve constant. Set this to 0 < curve < 1 to give difference response curves for axis
curve = float(mainconfig['curve'])

dome_speed = 0
accel_rate = float(mainconfig['accel_rate'])
dome_stick = 0

# Set Axis definitions
PSMOVE_AXIS_LEFT_VERTICAL = int(_config.get('Axis', 'drive'))
PSMOVE_AXIS_LEFT_HORIZONTAL = int(_config.get('Axis', 'turn'))
PSMOVE_AXIS_SHOULDER = int(_config.get('Axis', 'dome'))

baseurl = mainconfig['baseurl']

os.environ["SDL_VIDEODRIVER"] = "dummy"


################################################################################
################################################################################
# Custom Functions


def locate(user_string="PSMove Controller", x=0, y=0):
    ''' locate - Print a string at a certain location '''
    # Don't allow any user errors. Python's own error detection will check for
    # syntax and concatination, etc, etc, errors.
    x = int(x)
    y = int(y)
    if x >= 80:
        x = 80
    if y >= 40:
        y = 40
    if x <= 0:
        x = 0
    if y <= 0:
        y = 0
    HORIZ = str(x)
    VERT = str(y)
    # Plot the user_string at the starting at position HORIZ, VERT...
    print("\033["+VERT+";"+HORIZ+"f"+user_string)


def clamp(n, minn, maxn):
    ''' clamp - clamp a value between a min and max '''
    if n < minn:
        print("Clamping min")
        return minn
    elif n > maxn:
        print("Clamping max " + str(n))
        return maxn
    else:
        return n


def shutdownR2():
    ''' shutdownR2 - Put R2 into a safe state '''

    if __debug__:
        print("Running shutdown procedure")
    if __debug__:
        print("Stopping all motion...")
        print("...Setting drive to 0")
    drive.driveCommand(0)
    if __debug__:
        print("...Setting turn to 0")
    drive.turnCommand(0)
    if __debug__:
        print("...Setting dome to 0")
    dome.driveCommand(0)

    if __debug__:
        print("Disable drives")
    url = baseurl + "servo/body/ENABLE_DRIVE/0/0"
    try:
        requests.get(url)
    except Exception:
        print("Fail....")

    if __debug__:
        print("Disable dome")
    url = baseurl + "servo/body/ENABLE_DOME/0/0"
    try:
        requests.get(url)
    except Exception:
        print("Fail....")

    if __debug__:
        print("Bad motivator")
    # Play a sound to alert about a problem
        url = baseurl + "audio/MOTIVATR"
    try:
        requests.get(url)
    except Exception:
        print("Fail....")

    f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " ****** PSMove Shutdown ******\n")


#######################################################

parser = argparse.ArgumentParser(description='PSMove controller for r2_control.')
parser.add_argument('--curses', '-c', action="store_true", dest="curses", required=False, default=False,
                    help='Output in a nice readable format')
parser.add_argument('--dryrun', '-d', action="store_true", dest="dryrun", required=False, default=False,
                    help='Output in a nice readable format')
args = parser.parse_args()

# Open a log file
f = open(log_file, 'at')
f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : ****** PSMove started ******\n")
f.flush()

if not args.dryrun:
    if __debug__:
        print("Not a drytest")
    drive = SabertoothPacketSerial(address=int(_config.get('Drive', 'address')),
                                   type=_config.get('Drive', 'type'), port=_config.get('Drive', 'port'))
    dome = SabertoothPacketSerial(address=int(_config.get('Dome', 'address')),
                                  type=_config.get('Dome', 'type'), port=_config.get('Dome', 'port'))
    drive.driveCommand(0)
    drive.turnCommand(0)

pygame.display.init()

if args.curses:
    print('\033c')
    locate("-=[ PSMove Controller ]=-", 10, 0)
    locate("Left", 3, 2)
    locate("Right", 30, 2)
    locate("Joystick Input", 18, 3)
    locate("Drive Value (    )", 16, 7)
    locate('%4s' % speed_fac, 29, 7)
    locate("Last button", 3, 11)


num_joysticks = 0
j = list()
buttons = list()

# Start up
####################################################
# Wait for the first joystick
while True:
    pygame.joystick.quit()
    pygame.joystick.init()
    num_joysticks = pygame.joystick.get_count()
    if __debug__:
        print("Waiting for joystick... (count: %s)" % num_joysticks)
    if num_joysticks != 0:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Joystick found \n")
        f.flush()
        break
    time.sleep(5)

# Acknowledge first joystick
url = baseurl + "audio/Happy007"
try:
    r = requests.get(url)
except Exception:
    if __debug__:
        print("Fail....")

# Wait for second joystick, or button press.
count = 0
while True:
    if __debug__:
        print("Waiting for another joystick... (count: %s)" % num_joysticks)
    pygame.joystick.quit()
    pygame.joystick.init()
    num_joysticks = pygame.joystick.get_count()
    if num_joysticks == 2 or count > 3:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Joystick found \n")
        f.flush()
        break
    time.sleep(5)
    count += 1

pygame.init()
size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
if __debug__:
    print("Framebuffer size: %d x %d" % (size[0], size[1]))

joy = 0
while joy < num_joysticks:
    if __debug__:
        print("Initialising joystick " + str(joy))
    j.append(pygame.joystick.Joystick(joy))
    j[joy].init()
    buttons.append(j[joy].get_numbuttons())
    joy += 1


if num_joysticks == 1:
    PSMOVE_AXIS_LEFT_VERTICAL = int(_config.get('Axis', 'drive'))
    PSMOVE_AXIS_LEFT_HORIZONTAL = int(_config.get('Axis', 'turn'))
    PSMOVE_AXIS_SHOULDER = int(_config.get('Axis', 'dome'))


# Read in key combos from csv file
keys = defaultdict(list)
keys_file = 'keys' + str(num_joysticks) + '.csv'
with open(keys_file, mode='r') as infile:
    reader = csv.reader(infile)
    for row in reader:
        if __debug__:
            print("Row: %s | %s | %s" % (row[0], row[1], row[2]))
        keys[row[0]].append(row[1])
        keys[row[0]].append(row[2])

list(keys.items())

print("Initialised... entering main loop...")

f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : System Initialised \n")
f.flush()

last_command = time.time()
joystick = True

# Main loop
while (joystick):
    global previous
    if time.time() - last_command > keepalive:
        if __debug__:
            print("Last command sent greater than %s ago, doing keepAlive" % keepalive)
        drive.keepAlive()
        # Check js0 still there
        if (os.path.exists('/dev/input/js0')):
            if __debug__:
                print("Joystick still there....")
        else:
            print("No joystick")
            joystick = False
        # Check for no shutdown file
        if (os.path.exists('/home/pi/r2_control/controllers/.shutdown')):
            print("Shutdown file is there")
            joystick = False
        last_command = time.time()
    try:
        events = pygame.event.get()
    except Exception:
        if __debug__:
            print("Something went wrong!")
        shutdownR2()
        sys.exit(0)
    for event in events:
        if event.type == pygame.JOYBUTTONDOWN:
            buf = StringIO()
            x = 0
            while x < len(buttons):
                for i in range(buttons[x]):
                    button = j[x].get_button(i)
                    buf.write(str(button))
                x += 1
            combo = buf.getvalue()
            if __debug__:
                print("Buttons pressed: %s" % combo)
            if args.curses:
                locate("                   ", 1, 12)
                locate(combo, 3, 12)
            # Special key press (Both shoulder plus right) to increase speed of drive
            if combo == "00001010000000001":
                if __debug__:
                    print("Incrementing drive speed")
                # When detected, will increment the speed_fac by 0.5 and give some audio feedback.
                speed_fac += 0.05
                if speed_fac > 1:
                    speed_fac = 1
                if __debug__:
                    print("*** NEW SPEED %s" % speed_fac)
                if args.curses:
                    locate('%4f' % speed_fac, 28, 7)
                drive_mod = speed_fac * invert
                f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                        " : Speed Increase : " + str(speed_fac) + " \n")
                url = baseurl + "audio/Happy006"
                try:
                    r = requests.get(url)
                except Exception:
                    if __debug__:
                        print("Fail....")
            # Special key press (Both shoulder plus left) to decrease speed of drive
            if combo == "00001010000000010":
                if __debug__:
                    print("Decrementing drive speed")
                # When detected, will increment the speed_fac by 0.5 and give some audio feedback.
                speed_fac -= 0.05
                if speed_fac < 0.2:
                    speed_fac = 0.2
                drive_mod = speed_fac * invert
                f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                        " : Speed Decrease : " + str(speed_fac) + " \n")
                url = baseurl + "audio/Sad__019"
                try:
                    r = requests.get(url)
                except Exception:
                    if __debug__:
                        print("Fail....")
            try:
                newurl = baseurl + keys[combo][0]
                f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                        " : Button Down event : " + combo + "," + keys[combo][0] + " \n")
                f.flush()
                if __debug__:
                    print("Would run: %s" % keys[combo])
                    print("URL: %s" % newurl)
                try:
                    r = requests.get(newurl)
                except Exception:
                    if __debug__:
                        print("No connection")
            except Exception:
                if __debug__:
                    print("No combo (pressed)")
            previous = combo
        if event.type == pygame.JOYBUTTONUP:
            if __debug__:
                print("Buttons released: %s" % previous)
            try:
                newurl = baseurl + keys[previous][1]
                f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                        " : Button Up event : " + previous + "," + keys[previous][1] + "\n")
                f.flush()
                if __debug__:
                    print("Would run: %s" % keys[previous][1])
                    print("URL: %s" % newurl)
                try:
                    r = requests.get(newurl)
                except Exception:
                    if __debug__:
                        print("No connection")
            except Exception:
                if __debug__:
                    print("No combo (released)")
            previous = ""
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == PSMOVE_AXIS_LEFT_VERTICAL:
                if __debug__:
                    print("Value (Drive): %s : Speed Factor : %s" % (event.value, speed_fac))
                if args.curses:
                    locate("                   ", 10, 4)
                    locate('%10f' % (event.value), 10, 4)
                f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                        " : Forward/Back : " + str(event.value*drive_mod) + "\n")
                f.flush
                if not args.dryrun:
                    if __debug__:
                        print("Not a drytest")
                    drive.driveCommand(event.value*drive_mod)
                if args.curses:
                    locate("                   ", 10, 8)
                    locate('%10f' % (event.value*drive_mod), 10, 8)
                last_command = time.time()
            elif event.axis == PSMOVE_AXIS_LEFT_HORIZONTAL:
                if __debug__:
                    print("Value (Steer): %s" % event.value)
                if args.curses:
                    locate("                   ", 10, 5)
                    locate('%10f' % (event.value), 10, 5)
                f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                        " : Left/Right : " + str(event.value*drive_mod) + "\n")
                f.flush
                if not args.dryrun:
                    if __debug__:
                        print("Not a drytest")
                    drive.turnCommand(event.value*drive_mod)
                if args.curses:
                    locate("                   ", 10, 9)
                    locate('%10f' % (event.value*drive_mod), 10, 9)
                last_command = time.time()

# If the while loop quits, make sure that the motors are reset.
if __debug__:
    print("Exited main loop")
shutdownR2()
