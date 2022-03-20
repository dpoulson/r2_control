#!/bin/bash

CONT_DIR=/home/pi/r2_control/controllers

CURRENT=$(cat $CONT_DIR/.current)
rm $CONT_DIR/.shutdown

echo "Joystick selected: $CURRENT"

cd $CONT_DIR/"$CURRENT" || exit

/usr/bin/python -O ./r2_"$CURRENT".py

