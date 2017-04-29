#!/usr/bin/python

import os
import sys
import pygame
import time
import random
import csv
import requests
from collections import defaultdict
from cStringIO import StringIO
sys.path.append('/home/pi/r2_control/classes/')
from Adafruit_PWM_Servo_Driver import PWM

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

#PWM ranges
# 245 will give full range on a Sabertooth controller (ie, 1000ms and 2000ms, with 1500ms as the centerpoint)
SERVO_FULL_CW = 300
SERVO_STOP = 380
DOME_FULL_CW = 330
DOME_STOP = 425

dome_previous_speed = 0

baseurl = "http://localhost:5000/"
 
os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.display.init()

while True:
   pygame.joystick.quit()
   pygame.joystick.init()
   num_joysticks = pygame.joystick.get_count()
   if __debug__:
      print "Waiting for joystick... (count: %s)" % num_joysticks
   if num_joysticks != 0:
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

def driveServo(channel, speed):

   pulse = SERVO_STOP
   speed_adj = ((curve*(speed**3)) + ((1-curve)*speed))
   if speed != 0:
      # Use curve variable to decrease sensitivity at low end.
      pulse = (speed_adj * (SERVO_STOP - SERVO_FULL_CW)) + SERVO_STOP

   period = 1/float(freq)
   bit_duration = period/4096
   pulse_duration = bit_duration*pulse*1000000

   #tell servo what to do
   if __debug__:
      print "Channel %s : speed %5.5f : Adjusted speed: %5.5f : pulse %5.5f : duration %5.5f" % (channel,speed,speed_adj,pulse,pulse_duration)
   pwm.setPWM(channel, 0, int(pulse))

def driveDome(channel, speed):

   pulse = DOME_STOP
   speed_adj = ((curve*(speed**3)) + ((1-curve)*speed))
   if speed != 0:
      # Use curve variable to decrease sensitivity at low end.
      pulse = (speed_adj * (DOME_STOP - DOME_FULL_CW)) + DOME_STOP

   period = 1/float(freq)
   bit_duration = period/4096
   pulse_duration = bit_duration*pulse*1000000

   #tell servo what to do
   if __debug__:
      print "Channel %s : speed %5.5f : Adjusted speed: %5.5f : pulse %5.5f : duration %5.5f" % (channel,speed,speed_adj,pulse,pulse_duration)
   pwm.setPWM(channel, 0, int(pulse))


print "Initialised... entering main loop..."

pwm = PWM(0x40, debug=True)
pwm.setPWMFreq(freq) # Set frequency to 60 Hz

url = baseurl + "audio/Happy007"
try: 
  r = requests.get(url)
except:
  print "Fail...."

# Main loop
while True:
   global previous
   global dome_previous_speed
   try:
      events = pygame.event.get()
   except:
      if __debug__:
        print "Something went wrong!"
      driveServo(SERVO_DRIVE, 0)
      driveServo(SERVO_STEER, 0)
      driveDome(SERVO_DOME, 0)
      # Send motor disable command
      url = baseurl + "servo/body/ENABLE_DRIVE/0/0"
      try:
         r = requests.get(url)
      except:
         print "Fail...."
      # Play a sound to alert about a problem
      url = baseurl + "audio/Happy007"
      try:
         r = requests.get(url)
      except:
         print "Fail...."
   for event in events:
      if event.type == pygame.JOYBUTTONDOWN:
         buf = StringIO()
         for i in range ( buttons ):
            button = j.get_button(i)
            buf.write(str(button))
         combo = buf.getvalue()
         if __debug__:
            print "Buttons pressed: %s" % combo
         try:
            newurl = baseurl + keys[combo][0]
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
            driveServo(SERVO_DRIVE, event.value)
         elif event.axis == PS3_AXIS_LEFT_HORIZONTAL:
            if __debug__:
               print "Value (Steer): %s" % event.value
            driveServo(SERVO_STEER, event.value)
         elif event.axis == PS3_AXIS_RIGHT_HORIZONTAL:
            if __debug__:
               print "Value (Dome): %s" % event.value
            newvalue = ((curve*(event.value**3)) + ((1-curve)*event.value))
            if newvalue > dome_previous_speed:
               if __debug__:
                  print "Increase speed"
               dome_new_speed = dome_previous_speed + (newvalue/100)
            if newvalue < dome_previous_speed:
               if __debug__:
                  print "Decrease speed"
               dome_new_speed = dome_previous_speed - (newvalue/100)
            driveDome(SERVO_DOME, (dome_new_speed))



# If the while loop quits, make sure that the motors are reset.
driveServo(SERVO_DRIVE, 0)
driveServo(SERVO_STEER, 0)
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

