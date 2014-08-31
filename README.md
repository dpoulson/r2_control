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


