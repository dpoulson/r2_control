These are various programs to use as controllers, interfacing with r2 control.

Ideas are:

* Wiimote - Use a nunchuck as the main forward/back/dome control.
* PS3 - Controls over bluetooth rather than an xbee as the standard PS2 controller.
* WWW - Web based control from tablet or mobile (or computer). Allows all sorts of custom control, but not good for steering.
* Telegram - Instant messaging interface for getting more detailed information whilst driving with a remote


==Joystick Wrapper==
There is a joystick wrapper script and systemd service file available here. This will allow easy switch of which control
method is used on startup. There is a file called .current with a single line describing the directory of the control 
software. The script called will be r2_<joystick>.py, from the selected directory.


