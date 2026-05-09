""" Module to talk to battery monitor """
import serial
import time
import struct
import os
import csv
import configparser
from threading import Thread
from time import sleep
from flask import Blueprint, request
from r2utils import mainconfig
from r2utils import telegram
from builtins import range

_configfile = mainconfig.mainconfig['config_dir'] + 'monitoring.cfg'

_config = configparser.ConfigParser({'port': '/dev/ttyUSB0',
                                         'baudrate': '115200',
                                         'logfile': 'monitoring.log',
                                         'interval': 1.0})
_config.read(_configfile)

if not os.path.isfile(_configfile):
    print("Config file does not exist (Monitoring)")
    with open(_configfile, 'wt', encoding="utf-8") as configfile:
        _config.write(configfile)

_defaults = _config.defaults()

_logdir = mainconfig.mainconfig['logdir']
_logfile = _defaults['logfile']

api = Blueprint('monitoring', __name__, url_prefix='/monitoring')


@api.route('/', methods=['GET'])
@api.route('/battery', methods=['GET'])
def _battery():
    """GET gives a comma separated list of stats"""
    message = ""
    if request.method == 'GET':
        message += str(monitoring.queryBattery())
    return message


@api.route('/balance', methods=['GET'])
def _balance():
    """GET gives the current battery balance"""
    message = ""
    if request.method == 'GET':
        message += str(monitoring.queryBatteryBalance())
    return message


@api.route('/current', methods=['GET'])
def _current():
    """GET gives the current main current draw"""
    message = ""
    if request.method == 'GET':
        message += str(monitoring.queryCurrentMain())
    return message


class _Monitoring(object):
    def __init__(self, port, baudrate, interval):
        self.port = port
        self.baudrate = int(baudrate)
        self.interval = float(interval)
        self.logdir = mainconfig.mainconfig['logdir']
        self.telegram = False
        self.lowbat = False
        
        # Telemetry data
        self.data = {
            'voltage': 0.0,
            'current': 0.0,
            'cells': [0.0] * 6,
            'soc': 0,
            'temp_bms': 0.0,
            'temp_battery': 0.0
        }
        
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
        except Exception as e:
            print(f"Failed to open serial port {self.port}: {e}")
            self.ser = None

        if __debug__:
            print("Initialising Monitoring (JK BMS)")
            print(f"Port: {self.port} | Baud: {self.baudrate} | Interval: {self.interval}")

        loop = Thread(target=self.monitor_loop)
        loop.daemon = True
        loop.start()

    def _calculate_checksum(self, data):
        return sum(data) & 0xFFFFFFFF

    def _get_read_all_request(self):
        # 4E 57 00 13 00 00 00 00 06 03 00 00 00 00 00 00 68 00 00 01 29
        header = b'\x4E\x57'
        length = b'\x00\x13'
        bms_id = b'\x00\x00\x00\x00'
        cmd = b'\x06' # Read all
        source = b'\x03' # PC
        msg_type = b'\x00' # Request
        data = b'\x00' * 8 # Padding for read all
        end_flag = b'\x68'
        
        payload = bms_id + cmd + source + msg_type + data + end_flag
        # Checksum is sum of header + length + payload
        full_msg_for_sum = header + length + payload
        checksum = self._calculate_checksum(full_msg_for_sum)
        return full_msg_for_sum + struct.pack('>I', checksum)

    def _parse_frame(self, frame):
        if len(frame) < 11:
            return False
            
        header = frame[0:2]
        if header != b'\x4E\x57':
            return False
            
        length = struct.unpack('>H', frame[2:4])[0]
        # frame structure: header(2) + length(2) + payload(length) + checksum(4)
        if len(frame) < length + 8:
            return False
            
        payload = frame[4:4+length]
        received_checksum = struct.unpack('>I', frame[4+length:8+length])[0]
        calculated_checksum = self._calculate_checksum(frame[0:4+length])
        
        if received_checksum != calculated_checksum:
            if __debug__:
                print(f"Checksum mismatch: {received_checksum} != {calculated_checksum}")
            return False
            
        # DATA is Tag-Length-Value
        data_part = payload[7:-1]
        
        i = 0
        while i < len(data_part):
            tag = data_part[i]
            i += 1
            if tag == 0x79: # Cell voltages
                c_len = data_part[i]
                i += 1
                cell_count = c_len // 3
                for c in range(cell_count):
                    v = struct.unpack('>H', data_part[i+1:i+3])[0]
                    if c < 6:
                        self.data['cells'][c] = v / 1000.0
                    i += 3
            elif tag == 0x80: # Temp BMS
                self.data['temp_bms'] = struct.unpack('>h', data_part[i:i+2])[0]
                i += 2
            elif tag == 0x82: # Temp Battery
                self.data['temp_battery'] = struct.unpack('>h', data_part[i:i+2])[0]
                i += 2
            elif tag == 0x83: # Total Voltage
                self.data['voltage'] = struct.unpack('>H', data_part[i:i+2])[0] / 100.0
                i += 2
            elif tag == 0x84: # Current
                current_raw = struct.unpack('>H', data_part[i:i+2])[0]
                if current_raw & 0x8000:
                    self.data['current'] = (current_raw & 0x7FFF) / 100.0
                else:
                    self.data['current'] = -(current_raw / 100.0)
                i += 2
            elif tag == 0x85: # SOC
                self.data['soc'] = data_part[i]
                i += 1
            else:
                # Unknown tag, skip based on common lengths
                if tag in [0x86, 0x8E, 0x8F, 0x90, 0x91, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9A, 0x9B, 0x9C, 0x9D, 0x9E, 0x9F, 0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0x8B, 0x8C]:
                    i += 2
                elif tag in [0x87, 0x89, 0xA5, 0xA6, 0xA7, 0xA8]:
                    i += 4
                elif tag in [0x8A, 0xAA]:
                    i += 1
                else:
                    break
        return True

    def monitor_loop(self):
        if not self.ser:
            return
            
        f = open(self.logdir + '/power.log', 'at')
        request = self._get_read_all_request()
        
        while True:
            try:
                self.ser.write(request)
                header = self.ser.read(4)
                if len(header) == 4 and header[0:2] == b'\x4E\x57':
                    length = struct.unpack('>H', header[2:4])[0]
                    payload_and_crc = self.ser.read(length + 4)
                    if self._parse_frame(header + payload_and_crc):
                        writer = csv.writer(f)
                        row = [time.time(), self.data['voltage'], self.data['current'], self.data['soc']] + self.data['cells']
                        writer.writerow(row)
                        f.flush()
                        
                        if self.telegram and self.data['voltage'] < 21.0 and not self.lowbat:
                            telegram.send(f"Battery Low: {self.data['voltage']}V")
                            self.lowbat = True
                        elif self.data['voltage'] > 22.0:
                            self.lowbat = False
                            
            except Exception as e:
                if __debug__:
                    print(f"Error in monitor loop: {e}")
            
            sleep(self.interval)

    def queryBattery(self):
        return self.data['voltage']

    def queryBatteryBalance(self):
        if len(self.data['cells']) > 0:
            return max(self.data['cells']) - min(self.data['cells'])
        return 0

    def queryCurrentMain(self):
        return self.data['current']

    def queryCurrentLeft(self):
        return 0.0

    def queryCurrentRight(self):
        return 0.0

    def queryCurrentDome(self):
        return 0.0


monitoring = _Monitoring(_defaults['port'], _defaults['baudrate'], _defaults['interval'])

def get_telemetry():
    """Returns telemetry data for the main /status/json endpoint."""
    try:
        return {
            "main_battery": monitoring.queryBattery(),
            "battery_balance": monitoring.queryBatteryBalance(),
            "current_main": monitoring.queryCurrentMain(),
            "current_left": monitoring.queryCurrentLeft(),
            "current_right": monitoring.queryCurrentRight(),
            "current_dome": monitoring.queryCurrentDome()
        }
    except Exception:
        # Fallback if Serial hasn't populated data yet
        return {
            "main_battery": 0,
            "battery_balance": 0,
            "current_main": 0,
            "current_left": 0,
            "current_right": 0,
            "current_dome": 0
        }
