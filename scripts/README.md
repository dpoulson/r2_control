# 🤖 R2-D2 Control Scripting Language Specification

Welcome to the R2-D2 control scripting engine. This directory contains `.scr` script files that automate physical droid behaviors (sounds, dome moves, body servo sequences, light matrices, smoke generation, and sub-sequence triggering).

Scripts are defined in a simple **Comma-Separated Values (CSV)** format. Comments can be added by starting a line with a `#` character.

---

## 📋 Table of Contents
1. [Core Keywords & Basic Movement](#1-core-keywords--basic-movement)
2. [Audio Control](#2-audio-control)
3. [Physical Body & Dome Servos](#3-physical-body--dome-servos)
4. [Autodome Drive Control](#4-autodome-drive-control)
5. [Light & Effect Systems](#5-light--effect-systems)
6. [Sub-Script Orchestration](#6-sub-script-orchestration)
7. [Premium Example Script](#7-premium-example-script)

---

## 1. Core Keywords & Basic Movement

### `sleep`
Pauses script execution. Supports both fixed and randomized interval sleep times.
* **Fixed duration**:
  ```csv
  sleep,1.5
  ```
  *(Pauses execution for 1.5 seconds)*
* **Random duration**:
  ```csv
  sleep,random,2,6
  ```
  *(Pauses execution for a random integer duration between 2 and 6 seconds)*

---

## 2. Audio Control

### `sound`
Triggers audio playback from the droid's sound libraries.
* **Specific sound file**:
  ```csv
  sound,Happy007
  ```
  *(Plays the specific audio file `Happy007.mp3`)*
* **Random sound category**:
  ```csv
  sound,random,happy
  ```
  *(Plays a random sound from the `happy` sound category folder)*
  * *Available categories include: `alarm`, `happy`, `hum`, `misc`, `quote`, `razz`, `sad`, `sent`, `ooh`, `proc`, `whistle`, `scream`*

---

## 3. Physical Body & Dome Servos

### `body`
Controls the physical body servos (e.g. charge bays, utility arms, panels).
* **Specific Servo**:
  ```csv
  body,<servo_id>,<position>,<speed>
  ```
  * Example: `body,LLD,1,10` *(Opens Left Lower Door at 10% speed)*
  * Example: `body,LLD,0,0` *(Closes Left Lower Door)*
* **All Body Servos**:
  ```csv
  body,all,<command>
  ```
  * Example: `body,all,open` *(Opens all body panels)*
  * Example: `body,all,close` *(Closes all body panels)*

---

### `dome`
Controls the individual dome panels and accessory servos.
* **Specific Servo**:
  ```csv
  dome,<servo_id>,<position>,<speed>
  ```
  * Example: `dome,HP,1,15` *(Opens Holoprojector at 15% speed)*
* **All Dome Servos**:
  ```csv
  dome,all,<command>
  ```
  * Example: `dome,all,open` *(Opens all dome panels)*
  * Example: `dome,all,close` *(Closes all dome panels)*

---

## 4. Autodome Drive Control

### `autodome`
Controls the main physical dome rotation motors.

* **Duration-based Spin**:
  ```csv
  autodome,spin,<direction>,<speed>,<duration>
  ```
  * Example: `autodome,spin,left,0.35,1.5` *(Spins left at 35% speed for 1.5 seconds, then halts)*
* **Continuous Spin / Stop**:
  * **Start Spin**: `autodome,spin,<direction>,<speed>`
  * **Stop Spin**: `autodome,stop`
* **Random Look-Around Mode (Toggle)**:
  * **Enable**: `autodome,random,on`
  * **Disable**: `autodome,random,off`
* **Absolute Angular Position**:
  ```csv
  autodome,position,<angle>
  ```
  * Example: `autodome,position,45` *(Positions dome encoder to 45 degrees)*

---

## 5. Light & Effect Systems

### `flthy`
Controls the FlthyHP (Holoprojector) lighting displays.
* **Format**:
  ```csv
  flthy,<command_string>
  ```
  * Example: `flthy,H011` *(Sets holoprojector matrix to standard sequence)*

### `rseries`
Controls R-Series logic engine lights and displays.
* **Format**:
  ```csv
  rseries,<command_string>
  ```
  * Example: `rseries,220005` *(Triggers logic light flashing pattern)*

### `psi_matrix`
Controls PSI matrix displays.
* **Format**:
  ```csv
  psi_matrix,<command_string>
  ```

### `smoke`
Controls the onboard smoke generator.
* **Format**:
  ```csv
  smoke,<duration_seconds>
  ```
  * Example: `smoke,3.0` *(Triggers smoke puff for 3 seconds)*

---

## 6. Sub-Script Orchestration

### `script`
Triggers the execution of another script from inside the current script, or forcibly stops a looping script. Excellent for nesting and reusable animations!
* **Run Once (Default)**:
  ```csv
  script,<script_name>
  ```
  * Example: `script,cantina_dance` *(Starts the cantina dance routine once in the background)*
* **Loop Run**:
  ```csv
  script,<script_name>,1
  ```
  * Example: `script,dome_spin_dance,1` *(Runs the `dome_spin_dance` script in a continuous background loop)*
* **Stop Script**:
  ```csv
  script,<script_name>,stop
  ```
  * Example: `script,dome_spin_dance,stop` *(Instantly halts a looping `dome_spin_dance` script)*

---

## 7. Premium Example Script

Here is an example `.scr` file incorporating multiple features, animations, and sound triggers:

```csv
# 1. Alert the environment
sound,ALARM003
rseries,220005
sleep,2.0

# 2. Trigger a nested dance sub-script
script,dome_spin_dance

# 3. Release smoke while opening body panel
body,LLD,1,10
smoke,1.5
sleep,2.0

# 4. Return to rest
body,LLD,0,0
autodome,stop
sound,random,happy
```
