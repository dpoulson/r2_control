#include <TinyWireS.h>                  // I2C Master lib for ATTinys which use USI
#define I2C_ADDRESS 0x05

#ifndef TWI_RX_BUFFER_SIZE
#define TWI_RX_BUFFER_SIZE ( 16 )
#endif

#define PIN_RELAY 1
#define PIN_BUTTON 4

#define DURATION 5

int smokeState = LOW;
int buttonState;             // the current reading from the input pin
int lastButtonState = LOW;   // the previous reading from the input pin
char command = (char) 0;
int duration = 5;

unsigned long lastDebounceTime = 0;  // the last time the output pin was toggled
unsigned long debounceDelay = 50;    // the debounce time; increase if the output flickers

void generateSmoke(int duration) {
  digitalWrite(PIN_RELAY, HIGH);
  delay(duration*1000);
  digitalWrite(PIN_RELAY, LOW);
}

void receiveEvent(uint8_t howMany)
{
    if (howMany < 1) {
        // Sanity-check
        return;
    }
    
    if (howMany > TWI_RX_BUFFER_SIZE) {
        // Also insane number
        return;
    }

    command = TinyWireS.receive();
    if (howMany > 1) {
        // Assume any following characters are the duration
        duration = TinyWireS.receive();
    }
}


void setup() {
  // put your setup code here, to run once
  delay(2000);
  pinMode(PIN_RELAY, OUTPUT);
  pinMode(PIN_BUTTON, INPUT);
  digitalWrite(PIN_RELAY, LOW);
  
  TinyWireS.begin(I2C_ADDRESS);
  TinyWireS.onReceive(receiveEvent);

  delay(2000);

}

void loop() {
  if (command == 'S') {
     generateSmoke(duration);
     command = (char) 0;
     duration = DURATION;
  }
  
  // read the state of the switch into a local variable:
  int reading = digitalRead(PIN_BUTTON);

  // check to see if you just pressed the button
  // (i.e. the input went from LOW to HIGH),  and you've waited
  // long enough since the last press to ignore any noise:

  // If the switch changed, due to noise or pressing:
  if (reading != lastButtonState) {
    // reset the debouncing timer
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    // whatever the reading is at, it's been there for longer
    // than the debounce delay, so take it as the actual current state:

    // if the button state has changed:
    if (reading != buttonState) {
      buttonState = reading;

      // only toggle the LED if the new button state is HIGH
      if (buttonState == HIGH) {
        smokeState = !smokeState;
      }
    }
  }

  // set the LED:
  if (smokeState == HIGH) {
    // Activate the smoke  
    generateSmoke(DURATION);
    smokeState=LOW;
  }
  // save the reading.  Next time through the loop,
  // it'll be the lastButtonState:
  lastButtonState = reading;
  //TinyWireS_stop_check();
}


