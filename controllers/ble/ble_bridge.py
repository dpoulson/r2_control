#!/usr/bin/env python3
import asyncio
import logging
import requests
from bless import (
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("R2-BLE-Bridge")

# Define our BLE profile
SERVER_NAME = "R2_Tele"
SERVICE_UUID = "A07498CA-AD5B-474E-940D-16F1FBE7E8CD"
TELEMETRY_CHAR_UUID = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B" # Read-only telemetry (csv format string)
COMMAND_CHAR_UUID = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021C" # Write-only commands (string to interpret as rest calls)

# Flask endpoints
STATUS_URL = "http://127.0.0.1:5000/status/csv"
BASE_URL = "http://127.0.0.1:5000"

def get_telemetry():
    """
    Fetches the CSV telemetry from the main R2_Control Flask API.
    Returns the string or 'error' on fail.
    """
    try:
        response = requests.get(STATUS_URL, timeout=1)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        logger.debug(f"Failed to get telemetry: {e}")
    return "error"


def trigger_command(command_str):
    """
    ESP32 sends simple strings like "joystick/ps4" or "shutdown/now".
    We map it to an HTTP GET on the localhost REST API.
    """
    logger.info(f"Received BLE Command: {command_str}")
    endpoint = command_str.strip()
    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint
    url = BASE_URL + endpoint
    
    try:
        res = requests.get(url, timeout=2)
        logger.info(f"Command execution HTTP result: {res.status_code}")
    except Exception as e:
        logger.error(f"Failed to execute command '{url}': {e}")


def read_request(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
    # standard read is requested via BLE
    return characteristic.value


def write_request(characteristic: BlessGATTCharacteristic, value: bytearray, **kwargs):
    logger.debug(f"Write request to {characteristic.uuid}: {value}")
    if characteristic.uuid.lower() == COMMAND_CHAR_UUID.lower():
        try:
            command_str = value.decode('utf-8')
            trigger_command(command_str)
        except Exception as e:
            logger.error(f"Error handling write command: {e}")
            
    characteristic.value = value


async def run_ble_server(loop):
    logger.info("Initializing BLE Server...")
    server = BlessServer(name=SERVER_NAME, loop=loop)
    
    # Read & Write callbacks
    server.read_request_func = read_request
    server.write_request_func = write_request

    try:
        # Add Service
        await server.add_new_service(SERVICE_UUID)
        
        # Add Telemetry Characteristic
        char_flags = GATTCharacteristicProperties.read | GATTCharacteristicProperties.notify
        permissions = GATTAttributePermissions.readable
        await server.add_new_characteristic(SERVICE_UUID, TELEMETRY_CHAR_UUID, char_flags, None, permissions)
        
        # Add Command Characteristic
        cmd_flags = GATTCharacteristicProperties.write | GATTCharacteristicProperties.write_without_response
        cmd_permissions = GATTAttributePermissions.writeable
        await server.add_new_characteristic(SERVICE_UUID, COMMAND_CHAR_UUID, cmd_flags, None, cmd_permissions)
        
        logger.info("Starting BLE server...")
        await server.start()
        logger.info(f"BLE server started successfully. {SERVER_NAME} is advertising.")
        
        # Polling loop to update telemetry characteristic
        while True:
            await asyncio.sleep(2.0)
            telemetry_data = get_telemetry()
            val = telemetry_data.encode('utf-8')
            
            # The bless library requires checking if the characteristic object was indeed created safely
            char = server.get_characteristic(TELEMETRY_CHAR_UUID)
            if char:
                char.value = val
                # notify subscribers
                server.update_value(SERVICE_UUID, TELEMETRY_CHAR_UUID)
            
    except BaseException as e:
        logger.error(f"Error in BLE Server: {e}")
        try:
            await server.stop()
        except AttributeError:
            pass # bless library bug on failed initialization

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_ble_server(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down bridging service")
