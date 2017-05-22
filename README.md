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
 * /audio/list - lists all audio files available
 * /audio/\<name\> - Plays audio file \<name\>
 * /audio/random/\<type\> - Plays random audio file of \<type\>. If \<type\> is omitted, any random sound is played
 * /audio/volume - Returns current volume
 * /audio/volume/\<up|down|value\> - Turns volume up/down or sets to level 0-1
 * /lights/\<effect\> - Triggers pre programmed Teecee \<effect\>
 * /lcd - TBD


Install
=======

Read the wiki. 

