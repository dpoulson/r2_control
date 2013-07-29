r2_control
==========

Python code to control an R2D2 (or other astromech) from a Raspberry Pi over i2c

A Raspberry Pi is connected to Adafruit i2c servo controllers (http://www.adafruit.com/products/815)

A single process will run to accept commands via a named pipe. 

Other programs will be available to do things such as remote commands, run scripts, etc.


R2_Servo_Control.py

   * Creates a named pipe called /tmp/r2_commands.pipe
   * Loads a config file (servo.conf) with name, channel, min and max values for servos
   * Waits for commands to be piped in

   Accepts:
     * RELOAD - Reloads config file
     * QUIT - Quits program
     * <servo name>,<value> - Name is specified in the config file, and value is between 0 and 1 signifying what position to put the servo in


