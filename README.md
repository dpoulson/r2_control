r2_control
==========

Python code to control an R2D2 (or other astromech) from a Raspberry Pi over i2c

A Raspberry Pi is connected to Adafruit i2c servo controllers (http://www.adafruit.com/products/815)

Rewriting to use HTTP and REST.

Flask

Check out the wiki: https://github.com/dpoulson/r2_control/wiki

Main process
* Read config
* Create objects
* Create REST tree
*  lights
*  lcd
*  servo
*  audio
*  script


APIs Implemented:

 * /servo/\<body|dome\>/list - lists all servos configured
 * /servo/\<body|dome\>/\<name\>/\<position\>/\<duration\> - sets servo \<name\> to \<position\> (from 0 to 1 of full configured swing) over \<duration\> (seconds)
 * /servo/close - Close all servos
 * /joystick - Joystick selection functions
 * /joystick/list - List all possible joysticks
 * /joystick/\<stick\> - Select a joystick
 * /shutdown - Shutdown system
 * /status - Print current status
 * /sendstatus - Send status via telegram if enabled

Install
=======

Read the wiki. 


To see some parts of this in action, follow my instagram: https://www.instagram.com/r2djp/

