import threading
import time
import logging
import random
import requests
import configparser
import os
from flask import Blueprint, request, jsonify
from r2utils import mainconfig
from dataclasses import dataclass, field

# Blueprint for Flask API
api = Blueprint('dome', __name__, url_prefix='/autodome')

# ---------------------------------------------------------------------------
# Configuration handling
# ---------------------------------------------------------------------------
# Main config provides the basic dome driver settings. We also support an optional
# Encoder section for the ESP32 endpoint that reports the current angle.

_configfile = mainconfig.mainconfig['config_dir'] + 'dome.cfg'
_config = configparser.ConfigParser({
    'address': '129',
    'port': '/dev/ttyUSB0',
    'type': 'Syren',
    'encoder_url': '',
    'encoder_poll_interval': '0.2',
    'auto_left_max': '45',
    'auto_right_max': '45',
    'auto_dwell_seconds': '2',
    'auto_interval_seconds': '10'
})
_config.read(_configfile)

if not os.path.isfile(_configfile):
    print("Config file does not exist (Dome)")
    with open(_configfile, 'wt', encoding="utf-8") as configfile:
        _config.write(configfile)

_defaults = _config.defaults()

_DOME_ADDR = int(_defaults['address'])
_DOME_PORT = _defaults['port']
_DOME_TYPE = _defaults['type']

_ENCODER_URL = _defaults['encoder_url'] if _defaults['encoder_url'] else None
_ENCODER_POLL = float(_defaults['encoder_poll_interval'])

# ---------------------------------------------------------------------------
# State model
# ---------------------------------------------------------------------------
@dataclass
class DomeState:
    """Thread‑safe representation of the dome's current operating state."""
    mode: str = "continuous"          # "joystick", "auto", "continuous"
    target_angle: float = 0.0        # Desired angle in degrees (joystick mode)
    current_angle: float = 0.0       # Latest angle read from encoder
    random_enabled: bool = False     # Auto‑random look‑around flag
    spin_speed: float = 0.0          # -1.0 .. 1.0 for continuous spin
    spin_direction: int = 0          # -1 for left, 1 for right, 0 for stopped
    last_manual_input: float = 0.0   # Timestamp of last manual command
    lock: threading.RLock = field(default_factory=threading.RLock, init=False)

    def as_dict(self):
        return {
            "mode": self.mode,
            "target_angle": self.target_angle,
            "current_angle": self.current_angle,
            "random_enabled": self.random_enabled,
            "spin_speed": self.spin_speed,
            "spin_direction": self.spin_direction,
            "last_manual_input": self.last_manual_input,
        }

# ---------------------------------------------------------------------------
# Dome controller thread
# ---------------------------------------------------------------------------
class DomeController(threading.Thread):
    """Background thread that drives the Syren10 based on the current state.

    The thread periodically polls an optional encoder endpoint and then issues
    commands to the motor driver using the SabertoothPacketSerial library.
    """

    def __init__(self, address=_DOME_ADDR, port=_DOME_PORT, encoder_url=_ENCODER_URL, poll_interval=_ENCODER_POLL):
        super().__init__(daemon=True)
        self.address = address
        self.port = port
        self.encoder_url = encoder_url
        self.poll_interval = poll_interval
        self.state = DomeState()
        self._running = True
        # Auto‑dome configuration
        self.auto_left_max = float(_defaults['auto_left_max'])
        self.auto_right_max = float(_defaults['auto_right_max'])
        self.auto_dwell = float(_defaults['auto_dwell_seconds'])
        self.auto_interval = float(_defaults['auto_interval_seconds'])
        # Internal timers for auto mode
        self._auto_last_move = 0
        self._auto_target = 0.0
        self._auto_phase = 'idle'  # idle, moving, dwell, returning
        # Timers and parameters for sensorless auto mode
        self._auto_move_start = 0.0
        self._auto_move_duration = 0.0
        self._auto_move_direction = 0
        self._auto_move_speed = 0.0
        # Lazily import the driver – this keeps the module importable on systems
        # without the hardware attached (useful for unit tests).
        try:
            from SabertoothPacketSerial import SabertoothPacketSerial
            self.driver = SabertoothPacketSerial(address=self.address, type=_DOME_TYPE, port=self.port)
        except Exception as e:
            logging.error(f"Failed to initialise Sabertooth driver: {e}")
            self.driver = None

    # -------------------------------------------------------------------
    # Public API – thread‑safe setters
    # -------------------------------------------------------------------
    def set_target(self, angle: float):
        with self.state.lock:
            self.state.target_angle = angle
            self.state.mode = "joystick"
            self.state.last_manual_input = time.time()
        logging.debug(f"Dome target angle set to {angle:.2f} (joystick mode)")

    def set_mode(self, mode: str):
        if mode not in {"joystick", "auto", "continuous", "stop"}:
            raise ValueError("Invalid dome mode")
        with self.state.lock:
            self.state.mode = mode
        logging.debug(f"Dome mode changed to {mode}")

    def enable_random(self, enable: bool):
        with self.state.lock:
            self.state.random_enabled = enable
            if enable:
                self.state.mode = "auto"
        logging.debug(f"Dome random mode enabled: {enable}")

    def set_continuous(self, direction: str, speed: float):
        """Set continuous spin.
        direction: "left" or "right"
        speed: magnitude between 0.0 and 1.0
        """
        dir_val = -1 if direction.lower() == "left" else 1 if direction.lower() == "right" else 0
        speed = max(0.0, min(1.0, speed))
        with self.state.lock:
            self.state.spin_direction = dir_val
            self.state.spin_speed = speed
            self.state.mode = "continuous"
            self.state.last_manual_input = time.time()
        logging.debug(f"Dome continuous spin set: direction={direction}, speed={speed:.2f}")

    def get_status(self):
        with self.state.lock:
            return self.state.as_dict()

    # -------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------
    def _poll_encoder(self):
        if not self.encoder_url:
            return
        try:
            resp = requests.get(self.encoder_url, timeout=0.5)
            resp.raise_for_status()
            data = resp.json()
            angle = float(data.get("angle", 0))
            with self.state.lock:
                self.state.current_angle = angle
        except Exception as e:
            logging.debug(f"Encoder poll failed: {e}")

    def _command_driver(self, value: float):
        """Send a normalized command (‑1.0 … 1.0) to the Syren10 driver.

        The Sabertooth driver expects a value in the range ‑0.99 … 0.99; we clamp
        accordingly before sending.
        """
        if not self.driver:
            return
        clamped = max(-0.99, min(0.99, value))
        try:
            self.driver.driveCommand(clamped)
        except Exception as e:
            logging.error(f"Failed to send command to dome driver: {e}")

    # -------------------------------------------------------------------
    # Main loop
    # -------------------------------------------------------------------
    def run(self):
        logging.info("DomeController thread started")
        while self._running:
            self._poll_encoder()
            with self.state.lock:
                mode = self.state.mode
                target = self.state.target_angle
                current = self.state.current_angle
                spin = self.state.spin_speed
                random_enabled = self.state.random_enabled
                last_manual = self.state.last_manual_input

            now = time.time()
            manual_active = False

            if mode == "joystick":
                manual_active = True
                # Simple proportional control – map angle error to driver command.
                error = target - current
                command = max(-1.0, min(1.0, error / 180.0))
                self._command_driver(command)

            elif mode == "continuous":
                if spin != 0:
                    manual_active = True
                    command = self.state.spin_direction * self.state.spin_speed
                    self._command_driver(command)
                elif now - last_manual < 2.0:
                    # Keep manual control (stopped) for 2 seconds after last input
                    manual_active = True
                    self._command_driver(0)

            if not manual_active and random_enabled:
                if self.encoder_url:
                    # Sensor-based proportional auto‑dome logic
                    if self._auto_phase == 'idle':
                        if now - self._auto_last_move >= self.auto_interval:
                            self._auto_target = random.uniform(-self.auto_left_max, self.auto_right_max)
                            self._auto_last_move = now
                            self._auto_phase = 'moving'
                    elif self._auto_phase == 'moving':
                        error = self._auto_target - current
                        command = max(-1.0, min(1.0, error / 180.0))
                        self._command_driver(command)
                        if abs(error) < 5:
                            self._auto_phase = 'dwell'
                            self._dwell_start = now
                    elif self._auto_phase == 'dwell':
                        if now - self._dwell_start >= self.auto_dwell:
                            self._auto_target = 0.0  # return to centre
                            self._auto_phase = 'returning'
                    elif self._auto_phase == 'returning':
                        error = self._auto_target - current
                        command = max(-1.0, min(1.0, error / 180.0))
                        self._command_driver(command)
                        if abs(error) < 5:
                            self._auto_phase = 'idle'
                            self._auto_last_move = now
                else:
                    # Sensorless time-based auto-dome logic
                    if self._auto_phase == 'idle':
                        if now - self._auto_last_move >= self.auto_interval:
                            # Choose a random direction, speed, and duration for the move
                            self._auto_move_direction = random.choice([-1, 1])
                            self._auto_move_speed = random.uniform(0.2, 0.4)
                            self._auto_move_duration = random.uniform(0.5, 1.5)
                            self._auto_move_start = now
                            self._auto_phase = 'moving'
                    elif self._auto_phase == 'moving':
                        self._command_driver(self._auto_move_direction * self._auto_move_speed)
                        if now - self._auto_move_start >= self._auto_move_duration:
                            self._command_driver(0)
                            self._auto_phase = 'dwell'
                            self._dwell_start = now
                    elif self._auto_phase == 'dwell':
                        if now - self._dwell_start >= self.auto_dwell:
                            # Return to "center" by inverting direction for the same duration and speed
                            self._auto_move_direction = -self._auto_move_direction
                            self._auto_move_start = now
                            self._auto_phase = 'returning'
                    elif self._auto_phase == 'returning':
                        self._command_driver(self._auto_move_direction * self._auto_move_speed)
                        if now - self._auto_move_start >= self._auto_move_duration:
                            self._command_driver(0)
                            self._auto_last_move = now
                            self._auto_phase = 'idle'
            elif not manual_active:
                if mode == "stop":
                    self._command_driver(0)
                    self._running = False
                else:
                    self._command_driver(0)

            time.sleep(self.poll_interval)
        logging.info("DomeController thread exiting")

    def stop(self):
        self.set_mode("stop")
        self.join(timeout=2)

# ---------------------------------------------------------------------------
# Global Controller Instance
# ---------------------------------------------------------------------------
_dome_controller = DomeController()
_dome_controller.start()

def get_telemetry():
    """Returns a dictionary with telemetry data for the main /status/json endpoint."""
    return _dome_controller.get_status()

# ---------------------------------------------------------------------------
# Flask routes – thin wrappers around the controller methods.
# ---------------------------------------------------------------------------
@api.route('/status', methods=['GET'])
def dome_status():
    """Return the current dome state as JSON."""
    return jsonify(_dome_controller.get_status())

@api.route('/position', methods=['POST'])
def dome_position():
    """Set a target angle (degrees) for joystick mode.

    Expected JSON payload: {"position": <float>}
    """
    data = request.get_json(force=True, silent=True) or {}
    try:
        pos = float(data.get('position', 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid position value"}), 400
    _dome_controller.set_target(pos)
    return jsonify({"status": "ok", "mode": "joystick", "target": pos})

@api.route('/mode', methods=['POST'])
def dome_mode():
    """Switch the dome operating mode.

    Expected JSON payload: {"mode": "joystick"|"auto"|"continuous"}
    """
    data = request.get_json(force=True, silent=True) or {}
    mode = data.get('mode')
    if mode not in {"joystick", "auto", "continuous"}:
        return jsonify({"error": "Invalid mode"}), 400
    _dome_controller.set_mode(mode)
    return jsonify({"status": "ok", "mode": mode})

@api.route('/random', methods=['POST'])
def dome_random():
    """Enable or disable the auto‑random look‑around behaviour.

    Expected JSON payload: {"enabled": true|false}
    """
    data = request.get_json(force=True, silent=True) or {}
    enabled = data.get('enabled')
    if not isinstance(enabled, bool):
        return jsonify({"error": "'enabled' must be a boolean"}), 400
    _dome_controller.enable_random(enabled)
    return jsonify({"status": "ok", "random_enabled": enabled})

@api.route('/toggle_random', methods=['GET', 'POST'])
def toggle_random():
    """Toggle the random_enabled flag."""
    with _dome_controller.state.lock:
        new_state = not _dome_controller.state.random_enabled
    _dome_controller.enable_random(new_state)
    return jsonify({"status": "ok", "random_enabled": new_state})

@api.route('/spin', methods=['POST'])
def dome_spin():
    """Set continuous spin direction and speed.

    Expected JSON payload: {"direction": "left"|"right", "speed": <float 0‑1>}
    """
    data = request.get_json(force=True, silent=True) or {}
    direction = data.get('direction')
    speed = data.get('speed')
    if direction not in {"left", "right"}:
        return jsonify({"error": "Invalid direction"}), 400
    try:
        speed = float(speed)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid speed value"}), 400
    _dome_controller.set_continuous(direction, speed)
    return jsonify({"status": "ok", "direction": direction, "speed": speed})

@api.route('/auto/config', methods=['GET'])
def dome_auto_config():
    """Return auto‑dome configuration values."""
    cfg = {
        "left_max": _dome_controller.auto_left_max,
        "right_max": _dome_controller.auto_right_max,
        "dwell_seconds": _dome_controller.auto_dwell,
        "interval_seconds": _dome_controller.auto_interval,
    }
    return jsonify(cfg)

# ---------------------------------------------------------------------------
# Graceful shutdown hook – the main Flask app can call this when exiting.
# ---------------------------------------------------------------------------
def shutdown_dome():
    _dome_controller.stop()

"""DomeControl module provides a Flask blueprint (`api`) and a background thread
that drives the Syren10 speed controller. The API is ready for use and can be
registered by the main application via the existing plugin loading mechanism.
"""
