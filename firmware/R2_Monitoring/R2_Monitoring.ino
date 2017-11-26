
#include <MCP3008.h>
#include <Wire.h>

#define SLAVE_ADDRESS 0x04
#define NUM_CELLS 6
 
// define pin connections
#define CLOCK_PIN 10
#define MISO_PIN 11
#define MOSI_PIN 12
#define CS_PIN 13

#define MOTOR_LEFT 3
#define MOTOR_RIGHT 2
#define MAIN_DRAW 1

// put pins inside MCP3008 constructor
MCP3008 adc(CLOCK_PIN, MOSI_PIN, MISO_PIN, CS_PIN);

int number=0;
int state=0;

int mVperAmp = 66;
int RawValue = 0;
int ACSoffset = 2495;
float i2c_data[12];
float Amps[4];
float cell[8] = {0,0,0,0,0,0,0,0};
float cell_refine[8] = { 1.0024, 1.0045, 1.0001, 0.9952, 0.9810, 1.0193, 1, 1 };
float cell_total = 0;
float cell_min = 0;
float cell_max = 0;

 
void setup() {
  Serial.begin(9600); // open serial port
  Wire.begin(SLAVE_ADDRESS);
  Wire.onRequest(sendData);
}
 
void loop() {  
  // Get current readings and place into i2c_data
  for (int i=0; i<4; i++) {
    Amps[i] =  ((((analogRead(i)/1024.0) * 5000) - ACSoffset) / mVperAmp);
    i2c_data[i] = Amps[i];
  } 
  cell_total = 0;
  cell_min = 100;
  cell_max = 0;
  for (int i=0; i<NUM_CELLS; i++) {
    cell[i] = (((4.83/1023)*adc.readADC(i))*cell_refine[i]);
    cell_total += cell[i];
    if (cell[i] < cell_min) {
      cell_min = cell[i];
    }
    if (cell[i] > cell_max) {
      cell_max = cell[i];
    }
    //i2c_data[i+4] = cell[i];
  }
  i2c_data[4]=cell_total;
  i2c_data[5]=cell_min;
  i2c_data[6]=cell_max;
  
  Serial.print("Current: ");
  for (int i=0; i<4; i++) {
     Serial.print(Amps[i]);
     Serial.print("|");
  }
  Serial.print("A\t Voltage Cells ");
  for (int i=0; i<8; i++) {
     Serial.print(cell[i]);
     Serial.print("|");
  }
  Serial.print(" Battery Total: ");
  Serial.print(cell_total);
  Serial.println("V");
}


// callback for sending data
void sendData(){
  // Buffer to hold temp data, 6 bytes for each device
  byte buffer[32];
  // Populate buffer with temp. data
  for(int a = 0; a < 8; a++) {
    byte* b = (byte*) &i2c_data[a];
    // 4 bytes for each float
    for(int i = 0; i < 4; i++) {
      buffer[a*4+i] = b[i];
    }
  }
  // Send data over i2c connection
  Wire.write(buffer, 32);
}
  

