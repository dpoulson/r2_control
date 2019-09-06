/*
* ===============================================================================
* Copyright (C) 2018 Darren Poulson
*
* This file is part of R2_Control.
*
* R2_Control is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 2 of the License, or
* (at your option) any later version.
*
* R2_Control is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with R2_Control.  If not, see <http://www.gnu.org/licenses/>.
* ===============================================================================
*
* This is code to read in a rotary encoder value to determine the position of the 
* dome on an astromech. It is designed to use a simple IR sensor arrangement to 
* count the number of teeth that have gone past the sensor.
*
* Base code taken from http://playground.arduino.cc/Main/RotaryEncoders#Example3
* 
*/

#define encoder0PinA  2
#define encoder0PinB  3
#define numberTeeth 87

#define DEBUG 1

volatile unsigned int encoder0Pos = 0;

void setup() {
  pinMode(encoder0PinA, INPUT);
  pinMode(encoder0PinB, INPUT);

  // encoder pin on interrupt 0 (pin 2)
  attachInterrupt(0, doEncoderA, CHANGE);

  // encoder pin on interrupt 1 (pin 3)
  attachInterrupt(1, doEncoderB, CHANGE);

  Serial.begin (115200);
  Serial.println("Starting...");
}

void loop() {
  //Do stuff here
}

void changePos(int x) {
  encoder0Pos = encoder0Pos + x;
  // it takes 4 increments of encoder0Pos to transit from one tooth to the next
  if (encoder0Pos == (numberTeeth*4))
         encoder0Pos = 0;
  if (encoder0Pos == -1)
         encoder0Pos = (numberTeeth*4) - 1;
  #if (DEBUG>0) 
    Serial.print(encoder0Pos);
    Serial.print(",");
    Serial.print(digitalRead(encoder0PinA));
    Serial.print(",");
    Serial.print(digitalRead(encoder0PinB));
    Serial.print(",");
    Serial.println(calcDegrees());
  #endif
}

float calcDegrees() {
  return (encoder0Pos/4) * (360/numberTeeth);
}

void doEncoderA() {
  // look for a low-to-high on channel A
  if (digitalRead(encoder0PinA) == HIGH) {
    // check channel B to see which way encoder is turning
    if (digitalRead(encoder0PinB) == LOW) 
      changePos(1);          // CW
    else 
      changePos(-1);         // CCW
  } else {
    // must be a high-to-low edge on channel A
    // check channel B to see which way encoder is turning
    if (digitalRead(encoder0PinB) == HIGH) 
      changePos(1);          // CW
    else 
      changePos(-1);         // CCW
  }
}

void doEncoderB() {
  // look for a low-to-high on channel B
  if (digitalRead(encoder0PinB) == HIGH) {
    // check channel A to see which way encoder is turning
    if (digitalRead(encoder0PinA) == HIGH) 
      changePos(1);          // CW
    else 
      changePos(-1);         // CCW
  } else {
    // Look for a high-to-low on channel B
    // check channel B to see which way encoder is turning
    if (digitalRead(encoder0PinA) == LOW) 
      changePos(1);          // CW
    else 
      changePos(-1);         // CCW
  }
}
