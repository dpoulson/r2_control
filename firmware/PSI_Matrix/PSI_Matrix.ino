/*
 * PSI_Matrix.ino
 * Displays swiping of R2's PSI displays on the front and back of his dome. 
 * Software i2c connects to two Seeed RGB Matrix displays, and hardware i2c is used
 * to communicate with the r2_control software to trigger effects
 * 
 * Parts of the code are taken from the Seeed driver library for the displays.
 *  
 *
 * The MIT License (MIT)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */
#include <SoftwareWire.h>
#include <Wire.h>

#define SWIPE_SPEED 50              // Speed of swipe
#define SWIPE_FRONT_ONE 0xb1        // First colour of front PSI
#define SWIPE_FRONT_TWO 0           // Second colour of front PSI
#define SWIPE_REAR_ONE 0x5e         // First colour of rear PSI
#define SWIPE_REAR_TWO 0x24         // Second colour of rear PSI
#define SWIPE_DELAY 500             // Base delay between swipes

#define SOFT_SDA A0                 // Software i2c SDA pin (for communicating with displays)
#define SOFT_SCL A1                 // Software i2c SCL pin (for communicating with displays)

#define DISPLAY_ADDRESS 0x65

#define FRONT_ADDRESS 0x06;
#define REAR_ADDRESS 0x07

char command = (char) 0;
char which = (char) 0;
int cycles = 5;

int swipe_direction = 0;
int swipe_position = 0;
int count = 0;
int psi = 2; // Defaults to front PSI
uint8_t i2c_address = 0x07; 

SoftwareWire sw(SOFT_SDA, SOFT_SCL);

// Heart animation
uint64_t heart[] = {

  0xff0000ffff0000ff,
  0x0000000000000000,
  0x0000000000000000,
  0x0000000000000000,
  0xff000000000000ff,
  0xffff00000000ffff,
  0xffffff0000ffffff,
  0xffffffffffffffff,
 
  0xffffffffffffffff,
  0xffff00ffff00ffff,
  0xff000000000000ff,
  0xff000000000000ff,
  0xffff00000000ffff,
  0xffffff0000ffffff,
  0xffffffffffffffff,
  0xffffffffffffffff,
 
  0xffffffffffffffff,
  0xffffffffffffffff,
  0xffff00ffff00ffff,
  0xffff00000000ffff,
  0xffffff0000ffffff,
  0xffffffffffffffff,
  0xffffffffffffffff,
  0xffffffffffffffff,
 
  0xffffffffffffffff,
  0xffff00ffff00ffff,
  0xff000000000000ff,
  0xff000000000000ff,
  0xffff00000000ffff,
  0xffffff0000ffffff,
  0xffffffffffffffff,
  0xffffffffffffffff
};

//////////////////////////////////////
// i2c stuff

int i2cSendBytes(uint8_t *data, uint8_t len)
{
  int ret = 0;
  sw.beginTransmission(DISPLAY_ADDRESS);
  ret = sw.write(data, len);
  sw.endTransmission();
  return ret;
}


void displayFrames(uint64_t *buffer, uint16_t duration_time, bool forever_flag, uint8_t frames_number)
{
  int ret = 0;
  uint8_t data[72] = {0, };
  // max 5 frames in storage
  if (frames_number > 5) frames_number = 5;
  else if (frames_number == 0) return;

  data[0] = 0x05;
  data[1] = 0x0;
  data[2] = 0x0;
  data[3] = 0x0;
  data[4] = frames_number;

  for (int i=frames_number-1;i>=0;i--)
  {
    data[5] = i;
    // different from uint8_t buffer
    for (int j = 0; j< 8; j++)
    {
      for (int k = 7; k >= 0; k--)
      {
        data[8+j*8+(7-k)] = ((uint8_t *)buffer)[j*8+k+i*64];
      }
    }

    if (i == 0)
    {
      // display when everything is finished.
      data[1] = (uint8_t)(duration_time & 0xff);
      data[2] = (uint8_t)((duration_time >> 8) & 0xff);
      data[3] = forever_flag;
    }

    i2cSendBytes(data, 72);
  }
}

void displayFrames(uint8_t *buffer, uint16_t duration_time, bool forever_flag, uint8_t frames_number)
{
  uint8_t data[72] = {0, };
  // max 5 frames in storage
  if (frames_number > 5) frames_number = 5;
  else if (frames_number == 0) return;

  data[0] = 0x05;
  data[1] = 0x0;
  data[2] = 0x0;
  data[3] = 0x0;
  data[4] = frames_number;

  for (int i=frames_number-1;i>=0;i--)
  {
    data[5] = i;
    for (int j=0;j<64;j++) data[8+j] = buffer[j+i*64];
    if (i == 0)
    {
      // display when everything is finished.
      data[1] = (uint8_t)(duration_time & 0xff);
      data[2] = (uint8_t)((duration_time >> 8) & 0xff);
      data[3] = forever_flag;
    }
    i2cSendBytes(data, 72);
  }
}

void swipe_main(uint8_t pos, uint16_t duration_time, bool forever_flag, uint8_t frames_number)
{
  int ret = 0;
  int colour = 0;
  uint8_t data[72] = {0, };

  data[0] = 0x05;
  data[1] = 0x0;
  data[2] = 0x0;
  data[3] = 0x0;
  data[4] = frames_number;
  data[5] = 0;
    // different from uint8_t buffer
    for (int j = 0; j< 8; j++)
    {
      for (int k = 7; k >= 0; k--)
      {
        if (pos > k) {
          if (psi == 1) {
            colour = SWIPE_FRONT_ONE;
          } else {
            colour = SWIPE_REAR_ONE;
          }
        } else {
          if (psi == 1) {
            colour = SWIPE_FRONT_TWO;
          } else {
            colour = SWIPE_REAR_TWO;
          }
        }
        //data[8+j*8+(7-k)] = ((uint8_t *)buffer)[j*8+k+i*64];
        data[8+j*8+(7-k)] = colour;
      }
    }
    data[1] = (uint8_t)(duration_time & 0xff);
    data[2] = (uint8_t)((duration_time >> 8) & 0xff);
    data[3] = forever_flag;

    i2cSendBytes(data, 72);

}

void receiveEvent(uint8_t howMany)
{
    if (howMany < 1) {
        // Sanity-check
        return;
    }
    Serial.print("HowMany: ");
    Serial.println(howMany);
    command = Wire.read();
    Serial.print("Command: ");
    Serial.println(command);
    if (howMany > 1) {
        // Assume any following characters are the duration
        cycles = int(Wire.read());
        Serial.print("Cycles: ");
        Serial.println(cycles);
    }
}

// Routine to display a pulsing heart
void do_heart(uint8_t cycles, uint8_t pulse_speed) {
       for(int i=0;i<cycles;i++) {
           for (int i=0;i<4;i++) {
              displayFrames(heart+i*8, 100, true, 1);
              delay(pulse_speed);
           }
       } 
}

// Routine to do <cycles> of random pixels. As it loops through <cycles>
// the frequency of pixels reduces
void do_random(uint8_t cycles, uint8_t pulse_speed) {
  uint8_t data[64] = {0, };
  int pixel;
  int colour;
  Serial.println("Malfuction");
  Serial.print("Number of cycles: ");
  Serial.println(cycles);
  Serial.print("Pulse Speed: ");
  Serial.println(pulse_speed);
  for(int i=0;i<=cycles;i++) {
    for (int j = 0; j< 8; j++) {
      for (int k = 7; k >= 0; k--) {
        pixel = random(0,cycles);
        if (pixel < cycles-i) {
          // Pixel on
          colour = random(0,250);
        } else {
          colour = 0xff;
        }
        data[j*8+(7-k)] = colour;
      }
    }
    displayFrames(data, 100, true, 1);
    delay(pulse_speed);
  }
  uint8_t blank[64] = {0xff, };
  for( int i = 0; i < sizeof(blank);  ++i )
    blank[i] = (char)255;
  displayFrames(blank, 100, true, 1);
  delay(2000);
}

////////////////////////////////////////
// Setup
void setup()
{
    // Do some checking to see which PSI this is
    
    Wire.begin(i2c_address);
    sw.begin();
    Wire.onReceive(receiveEvent);
    Serial.begin(115200);
    delay(1000);  
}


void loop()
{
    if (command == 'H') { // Heart
      do_heart(cycles, 100);
      command = (char) 0;
    }
    if (command == 'M') { // Malfunction
      do_random(cycles, 100);
      command = (char) 0;
    }
   
    int x;
    swipe_main(swipe_position,100, true, 1);
    if (swipe_direction == 0) {
      if (swipe_position > 7) {
        swipe_direction = 1;
        x = random(0, 1500);
        delay(SWIPE_DELAY + x);
        swipe_position--;
      } else {
        swipe_position++;
      }
    } else {
      if (swipe_position <= 0) {
        swipe_direction = 0;
        x = random(0, 1500);
        delay(SWIPE_DELAY + x);
        swipe_position++;
      } else {
        swipe_position--;
      }
    }
    delay(SWIPE_SPEED);
    count++;

    
}
