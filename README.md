# r2_control

Python code to control an R2D2 (or other astromech) from a Raspberry Pi over I2C.

A Raspberry Pi is connected to Adafruit I2C servo controllers: http://www.adafruit.com/products/815

Rewriting to use HTTP and REST via Flask.

Check out the wiki: https://github.com/dpoulson/r2_control/wiki

## Main Process
* Read config
* Create objects
* Create REST tree
  * lights
  * lcd
  * servo
  * audio
  * script

## APIs Implemented:
 * `/servo/<body|dome>/list` - Lists all servos configured
 * `/servo/<body|dome>/<name>/<position>/<duration>` - Sets servo `<name>` to `<position>` (from 0 to 1 of full configured swing) over `<duration>` (seconds)
 * `/servo/close` - Close all servos
 * `/joystick` - Joystick selection functions
 * `/joystick/list` - List all possible joysticks
 * `/joystick/<stick>` - Select a joystick
 * `/shutdown` - Shutdown system
 * `/status` - Print current status
 * `/sendstatus` - Send status via telegram if enabled

## Install
Read the wiki. 

To see some parts of this in action, follow my instagram: https://www.instagram.com/r2djp/

## Debian Packages (Experimental)
Install the system using the pre-built Debian packages. The system is modular so you can install just what you need. 

First, add the APT repository:
```bash
echo "deb [trusted=yes] https://dpoulson.github.io/r2_control/ ./" | sudo tee /etc/apt/sources.list.d/r2-control.list
sudo apt update
```

Then, you can install the components you want:

**Core Package**:
* `sudo apt install r2-control` (This installs the core system. Note: the APT repository currently serves the lite version. For the offline bundle, download the `.deb` file directly from the GitHub releases page).

**Add-On Packages**:
* `sudo apt install r2-control-sounds` (Installs all sound libraries)
* `sudo apt install r2-control-controllers` (Installs controller logic, Joystick services, BLE, and Apache web integration)

*Note: The add-on packages will automatically depend on the main `r2-control` package.*
