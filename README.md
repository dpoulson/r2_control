r2_control
==========

Python code to control an R2D2 (or other astromech) from a Raspberry Pi over i2c

A Raspberry Pi is connected to Adafruit i2c servo controllers (http://www.adafruit.com/products/815)

Rewriting to use HTTP and REST.

Flask

Main process
	Read config
	Create REST tree
		teecee
		lcd
		servo
		audio
	Populate modules (eg. /teecee/0/ or /server/dome)


APIs Implemented:

/servo/list - lists all servos configured
/servo/<name>/<position>/<duration> - sets servo <name> to <position> (from 0 to 1 of full configured swing) over <duration> (seconds)
/audio/list - lists all audio files available
/audio/<name> - Plays audio file <name>
/teecee/<effect> - Triggers pre programmed Teecee <effect>
/lcd - TBD

