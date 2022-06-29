#!/bin/bash

CONT_DIR=/home/pi/.r2config

CURRENT=`cat $CONT_DIR/current_joy`
rm $CONT_DIR/.shutdown

echo "Joystick selected: $CURRENT"

cd /home/pi/r2_control/$CURRENT

/usr/bin/python -O ./r2_$CURRENT.py

