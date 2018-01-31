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

drive = SabertoothPacketSerial(legacy=True)
drive.drive(0)
drive.turn(0)

keepalive = 0.25

# Speed factor. This multiplier will define the max value to be sent to the drive system. 
# eg. 0.5 means that the value of the joystick position will be halved
# Should never be greater than 1
speed_fac = 0.35

# Invert. Does the drive need to be inverted. 1 = no, -1 = yes
invert = -1

drive_mod = speed_fac * invert

# Deadband: the amount of deadband on the sticks
deadband = 3

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

# PWM ranges
# 245 will give full range on a Sabertooth controller (ie, 1000ms and 2000ms, with 1500ms as the centerpoint)
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

last_command = time.time()

# Main loop
while True:
    global previous
    global last_command
    global speed_fac
    if time.time() - last_command > keepalive: 
        if __debug__:
            print "Last command sent greater than %s ago, doing keepAlive" % keepalive
        drive.keepAlive()
        last_command = time.time()
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
            # Special key press (All 4 plus triangle) to increase speed of drive
            if combo == "0000010011110000000":
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
            if combo == "0000000111110000000":
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
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == PS3_AXIS_LEFT_VERTICAL:
                if __debug__:
                    print "Value (Drive): %s : Speed Factor : %s" % (event.value, speed_fac)
                f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Forward/Back : " + str(event.value*speed_fac) + "\n")
                f.flush
                drive.drive(event.value*drive_mod)
                last_command = time.time()
            elif event.axis == PS3_AXIS_LEFT_HORIZONTAL:
                if __debug__:
                    print "Value (Steer): %s" % event.value
                f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Left/Right : " + str(event.value*speed_fac) + "\n")
                f.flush
                drive.turn(event.value*drive_mod)
                last_command = time.time()
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

