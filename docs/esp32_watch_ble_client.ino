// ESP32-S3 BLE Client Example for R2_Control using the Waveshare AMOLED Watch
// Recommends: NimBLE-Arduino Library for Bluetooth

#include <Arduino.h>
#include <NimBLEDevice.h>
#include <Wire.h>

// AXP2101 I2C Pins usually found on similar ESP32-S3 watches. 
// You'll likely need the 'XPowersLib' to interact with the AXP2101.
#define I2C_SDA 4
#define I2C_SCL 5 

// We define our target BLE configuration to match the R2 Python Server
static BLEUUID serviceUUID("A07498CA-AD5B-474E-940D-16F1FBE7E8CD");
static BLEUUID telemetryCharUUID("51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B");
static BLEUUID commandCharUUID("51FF12BB-3ED8-46E5-B4F9-D64E2FEC021C");

static boolean doConnect = false;
static boolean connected = false;
static boolean doScan = true;
static BLERemoteCharacteristic* pTeleCharacteristic;
static BLERemoteCharacteristic* pCmdCharacteristic;
static BLEAdvertisedDevice* myDevice;

// Function called whenever the R2 outputs telemetry 
static void notifyCallback(
  BLERemoteCharacteristic* pBLERemoteCharacteristic,
  uint8_t* pData,
  size_t length,
  bool isNotify) {
    
    // The data arrives from Python as a comma separated string:
    // f"{uptime_string},{battery},{batteryBalance},{remote_battery},{internet.check()},{volume}"
    String telemetry = String((char*)pData, length);
    Serial.print("R2 Telemetry Received: ");
    Serial.println(telemetry);

    // ==========================================
    // TODO: Update your AMOLED Display here!
    // Example: 
    // myTft.setCursor(0, 0); 
    // myTft.println(telemetry);
    // ==========================================
}

class MyClientCallback : public BLEClientCallbacks {
  void onConnect(BLEClient* pclient) {
    connected = true;
    Serial.println("Connected to R2_Tele");
  }

  void onDisconnect(BLEClient* pclient) {
    connected = false;
    Serial.println("Disconnected from R2_Tele - will attempt rescan.");
  }
};

class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
  void onResult(BLEAdvertisedDevice* advertisedDevice) {
    if (advertisedDevice->haveName() && advertisedDevice->getName() == "R2_Tele") {
      Serial.println("Found R2_Tele. Stopping scan...");
      BLEDevice::getScan()->stop();
      myDevice = advertisedDevice;
      doConnect = true;
      doScan = false;
    }
  }
};

bool connectToServer() {
  BLEClient*  pClient  = BLEDevice::createClient();
  pClient->setClientCallbacks(new MyClientCallback());

  // Connect to the remote BLE Server
  pClient->connect(myDevice);  
  
  // Obtain a reference to the service
  BLERemoteService* pRemoteService = pClient->getService(serviceUUID);
  if (pRemoteService == nullptr) {
    Serial.println("Failed to find our service UUID.");
    pClient->disconnect();
    return false;
  }

  // Obtain a reference to the characteristics
  pTeleCharacteristic = pRemoteService->getCharacteristic(telemetryCharUUID);
  pCmdCharacteristic = pRemoteService->getCharacteristic(commandCharUUID);
  
  if (pTeleCharacteristic == nullptr || pCmdCharacteristic == nullptr) {
    Serial.println("Failed to find our characteristic UUIDs.");
    pClient->disconnect();
    return false;
  }

  // Subscribe to telemetry notifications
  if(pTeleCharacteristic->canNotify()) {
    pTeleCharacteristic->registerForNotify(notifyCallback);
    Serial.println("Subscribed to R2_Tele Notifications!");
  }

  return true;
}

void sendCommandMessage(String commandInput) {
  if (connected && pCmdCharacteristic != nullptr && pCmdCharacteristic->canWrite()) {
    pCmdCharacteristic->writeValue(commandInput.c_str(), commandInput.length());
    Serial.println("Sent Command to R2: " + commandInput);
  } else {
    Serial.println("Cannot send command! Not connected or missing characteristic.");
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("Starting BLE Client application...");

  // Setup I2C for AXP2101 / QMI8658
  Wire.begin(I2C_SDA, I2C_SCL);
  // (Initialize XPowersLib / AXP2101 here to power on display and peripherals)
  
  // Set up BLE
  BLEDevice::init("");
  BLEScan* pBLEScan = BLEDevice::getScan();
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setInterval(1349);
  pBLEScan->setWindow(449);
  pBLEScan->setActiveScan(true);
  pBLEScan->start(5, false);
}

void loop() {
  if (doConnect == true) {
    if (connectToServer()) {
      Serial.println("We are now connected to the R2_Control BLE Server.");
    } else {
      Serial.println("We have failed to connect to the server; there is nothin more we will do.");
    }
    doConnect = false;
  }

  // If we are connected and want to send a command to R2...
  if (connected) {
    // ==============================================================
    // TOUCH SCREEN HANDLING EXAMPLE
    // Replace `getTouch()` with your actual library function (e.g. from CST816S)
    // ==============================================================
    /*
    int touchX = 0; 
    int touchY = 0;
    bool isTouched = getTouch(&touchX, &touchY); 
    
    if (isTouched) {
      // Very basic 4-quadrant button mapping
      if (touchX < 120 && touchY < 120) {
        sendCommandMessage("audio/random/happy");
        delay(500); // debounce
      } 
      else if (touchX > 120 && touchY < 120) {
        sendCommandMessage("audio/random/alarm");
        delay(500);
      }
      else if (touchX < 120 && touchY > 120) {
        sendCommandMessage("audio/random/quote");
        delay(500);
      }
      else {
        // Run script 1 as an example (must match an endpoint from /scripts/list)
        sendCommandMessage("scripts/run/1"); 
        delay(500);
      }
    }
    */
  } else if(doScan) {
    BLEDevice::getScan()->start(5, false); // Rescan
  }
  
  delay(1000); // Main loop delay
}
