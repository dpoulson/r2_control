import os
import pygame
import time
import random
import csv
import requests
from cStringIO import StringIO

baseurl = "http://localhost:5000/"
 
if not os.getenv('SDL_VIDEODRIVER'):
    os.putenv('SDL_VIDEODRIVER', 'fbcon')

pygame.display.init()
pygame.init()

size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
print "Framebuffer size: %d x %d" % (size[0], size[1])
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
screen.fill((0, 0, 0))        
pygame.display.update()
 
j = pygame.joystick.Joystick(0)
j.init()
buttons = j.get_numbuttons()

# Read in key combos from csv file
keys = {}
with open('keys.csv', mode='r') as infile:
   reader = csv.reader(infile)
   for row in reader:
      print "Row: %s | %s | %s" % (row[0], row[1], row[2])
      #keys += {row[0]:row[1]}
      keys[row[0]][0] = row[1]
      keys[row[0]][1] = row[2]

# Main loop
while True:
   events = pygame.event.get()
   for event in events:
      if event.type == pygame.JOYBUTTONDOWN:
         buf = StringIO()
         for i in range ( buttons ):
            button = j.get_button(i)
            buf.write(str(button))
         combo = buf.getvalue()
         print "Buttons: %s" % combo
         try:
            newurl = baseurl + keys[combo][0]
            print "URL: %s" % newurl
            r = requests.get(newurl)
            if keys[combo][1] != "":
               print "Running on button release option"
               newurl = baseurl + keys[combo][0]
               print "URL: %s" % newurl
               r = requests.get(newurl)
         except:
            print "No combo"



