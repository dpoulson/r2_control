These are various programs to use as controllers, interfacing with r2 control.

Current controllers are:

* PS3 - Controls over bluetooth rather than an xbee as the standard PS2 controller.
* PSMove - A stealthier option to control R2.
* WWW - Web based control from tablet or mobile (or computer). Allows all sorts of custom control, but not good for steering.
* Telegram - Instant messaging interface for getting more detailed information whilst driving with a remote.
* XBox360Controller - Alternative to PS3.
* sBusPythonDrive - Suitable for R/C Transmitter.


## Joystick Wrapper

There is a joystick wrapper script and systemd service file available here. This will allow easy switch of which control
method is used on startup. There is a file called .current with a single line describing the directory of the control 
software. The script called will be r2\_\<joystick\>.py, from the selected directory.

To mark a directory as a potential joystick (rather than another form of control) then make sure it has a .isjoystick file in it.
This is used by r2\_control when calling the joystick list API.


