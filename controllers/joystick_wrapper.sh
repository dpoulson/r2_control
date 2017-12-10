#!/bin/bash

CONT_DIR=/home/pi/r2_control/controllers

CURRENT=`cat $CONT_DIR/.current`

echo "Joystick selected: $CURRENT"

cd $CONT_DIR/$CURRENT

/usr/bin/python -O ./r2_$CURRENT.py

