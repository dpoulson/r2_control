// R-Series Charging Bay Indicators Demo
// with Optional Voltage Monitor & Display
// CCv3 SA BY - 2012 Michael Erwin
// An Extension to Teeces Logics
//
// Release History
// v009 - Removed all MP3 code, not needed for my implementation - Darren Poulson <darren.poulson@gmail.com>
// v008 - Added Single Test all LEDs, and if monitorVCC == false, it simulates battery condition OK
// v007 - Changed status indicator operation to reflect ESBmode
// v006 - Added ESBmode to charging SEQ
// v005 - Added Voltage Monitor
// v004 - Demo Sketch
//
//We always have to include the library
#include "LedControl.h"

/*
 Now we need a LedControl to work with.
 ***** These pin numbers will probably not work with your hardware *****
 pin 13 is connected to the DataIn 
 pin 12 is connected to the CLK 
 pin 11 is connected to LOAD 
 We have only a single MAX72XX.
 */
LedControl lc=LedControl(13,12,11,1);

// you will need to adjust these variables for your configuration
boolean ESBmode = true;   // operates like charging scene on Dagobah otherwise operates line mode
boolean monitorVCC = true;// Set this to true to monitor voltage
boolean testLEDs = false; // Set to true to test every LED on initial startup

int analoginput = 0;       // Set this to which Analog Pin you use for the voltage in.

float greenVCC = 12.5;    // Green LED l21 on if above this voltage
float yellowVCC = 12.0;    // Yellow LED l22 on if above this voltage & below greenVCC... below turn on only RED l23



// For 15volts: R1=47k, R2=24k
// For 30volts: R1=47k, R2=9.4k

float R1 = 47000.0;     // >> resistance of R1 in ohms << the more accurate these values are
float R2 = 24000.0;     // >> resistance of R2 in ohms << the more accurate the measurement will be


float vout = 0.0;       // for voltage out measured analog input
int value = 0;          // used to hold the analog value coming out of the voltage divider
float vin = 0.0;        // voltage calulcated... since the divider allows for 15 volts



/* we always wait a bit between updates of the display */
unsigned long delaytime=300;




void setup(){

   // Random Code
  
randomSeed(analogRead(5));
  
  // End Random Code


  
  
  Serial.begin(9600);                    // DEBUG CODE
  if (monitorVCC == true) { pinMode(analoginput, INPUT);}
  
  /*
   The MAX72XX is in power-saving mode on startup,
   we have to do a wakeup call
   */
  lc.shutdown(0,false);
  /* Set the brightness to a medium values */
  lc.setIntensity(0,8);
  /* and clear the display */
  lc.clearDisplay(0);
  if (testLEDs == true) {
    singleTest(); 
  
  }
  if (monitorVCC == false){
    l23on();
  }
}

/* 
 This function will light up every Led on the matrix.
 The led will blink along with the row-number.
 row number 4 (index==3) will blink 4 times etc.
 */
void singleTest() {
  for(int row=0;row<4;row++) {
    for(int col=0;col<5;col++) {
      delay(delaytime);
      lc.setLed(0,row,col,true);
      delay(delaytime);
      for(int i=0;i<col;i++) {
        lc.setLed(0,row,col,false);
        delay(delaytime);
        lc.setLed(0,row,col,true);
        delay(delaytime);
      }
    }
  }
  l21on();
  delay(delaytime);
  l22on();
  delay(delaytime);
  l23on();
  delay(delaytime);
  l21off();
  l22off();
  l23off();
}

void l21on() // Voltage GREEN
{
lc.setLed(0,4,5,true);
}

void l22on()// Voltage Yellow
{
lc.setLed(0,5,5,true);
}

void l23on()// Voltage RED
{
lc.setLed(0,6,5,true);
}


void l21off() // Voltage Green 
{
lc.setLed(0,4,5,false);
}

void l22off() // Voltage Yellow
{
lc.setLed(0,5,5,false);
}

void l23off() // Voltage Red
{
lc.setLed(0,6,5,false);
}


void heartSEQ() {
 // Step 0
  lc.setRow(0,0,B01110000);
  lc.setRow(0,1,B00100000);
  lc.setRow(0,2,B00100000);
  lc.setRow(0,3,B01110000);
  delay(1000);
  // Step 1
  lc.setRow(0,0,B01010001);
  lc.setRow(0,1,B11111000);
  lc.setRow(0,2,B01110000);
  lc.setRow(0,3,B00100000);
  delay(1000);
  // Step 1
  lc.setRow(0,0,B01010001);
  lc.setRow(0,1,B01010001);
  lc.setRow(0,2,B01010001);
  lc.setRow(0,3,B01110000);
  delay(1000);


}


/* 
 This function in a fashon like ESB scene
i */
void chargingSEQ() {  // used when monitorVCC == false
 // Step 0
  lc.setRow(0,0,B11111000);
  lc.setRow(0,1,B11111000);
  lc.setRow(0,2,B11111000);
  lc.setRow(0,3,B00000110);
  l21on();
  delay(delaytime);
 // Step 1 
  lc.setRow(0,1,B00000110);
  delay(delaytime);
 // Step 2
  lc.setRow(0,1,B11111000);
  lc.setRow(0,2,B00000110);
  lc.setRow(0,3,B11111000);
  l22on();
  delay(delaytime);
 // Step 3
  lc.setRow(0,0,B00000110);
  lc.setRow(0,1,B11111000);
  lc.setRow(0,2,B11111000); 
  lc.setRow(0,3,B00000110);
  l23on();
  delay(delaytime);
// Step 4
  lc.setRow(0,0,B11111000);
  lc.setRow(0,1,B11111000); 
  lc.setRow(0,2,B11111000);
  lc.setRow(0,3,B11111000); 
  delay(300);
// Step 5
  lc.setRow(0,0,B11111000);
  lc.setRow(0,1,B00000110);
  lc.setRow(0,1,B00000110);
  lc.setRow(0,3,B00000110);
  delay(delaytime);
// Step 6
  lc.setRow(0,0,B00000110);
  lc.setRow(0,1,B11111000); 
  lc.setRow(0,2,B00000110);
  lc.setRow(0,3,B00000110);
  l23off();
  delay(delaytime);
// Step 7
  lc.setRow(0,0,B11111000);
  lc.setRow(0,1,B11111000);
  lc.setRow(0,2,B00000110);
  lc.setRow(0,3,B00000110);
  l22off();
  delay(delaytime);
  // Step 8
  lc.setRow(0,0,B00000110);
  lc.setRow(0,1,B11111000);
  lc.setRow(0,2,B00000110);
  lc.setRow(0,3,B11111000);
  l21off();
  delay(delaytime);
  // Step 9
  lc.setRow(0,0,B00000110);
  lc.setRow(0,1,B11111000);
  lc.setRow(0,2,B11111000);
  lc.setRow(0,3,B11111000);
  delay(delaytime);
}


void operatingSEQ() {          // used when monitorVCC == true
 // Step 0
  lc.setRow(0,0,B11111000);
  lc.setRow(0,1,B11111000);
  lc.setRow(0,2,B11111000);
  lc.setRow(0,3,B00000110);
  delay(delaytime);
 // Step 1 
  lc.setRow(0,1,B00000110);
  delay(delaytime);
 // Step 2
  lc.setRow(0,1,B11111000);
  lc.setRow(0,2,B00000110);
  lc.setRow(0,3,B11111000);
  delay(delaytime);
 // Step 3
  lc.setRow(0,0,B00000110);
  lc.setRow(0,1,B11111000);
  lc.setRow(0,2,B11111000); 
  lc.setRow(0,3,B00000110);
  delay(delaytime);
// Step 4
  lc.setRow(0,0,B11111000);
  lc.setRow(0,1,B11111000); 
  lc.setRow(0,2,B11111000);
  lc.setRow(0,3,B11111000); 
  delay(300);
// Step 5
  lc.setRow(0,0,B11111000);
  lc.setRow(0,1,B00000110);
  lc.setRow(0,1,B00000110);
  lc.setRow(0,3,B00000110);
  delay(delaytime);
// Step 6
  lc.setRow(0,0,B00000110);
  lc.setRow(0,1,B11111000); 
  lc.setRow(0,2,B00000110);
  lc.setRow(0,3,B00000110);
  delay(delaytime);
// Step 7
  lc.setRow(0,0,B11111000);
  lc.setRow(0,1,B11111000);
  lc.setRow(0,2,B00000110);
  lc.setRow(0,3,B00000110);
  delay(delaytime);
  // Step 8
  lc.setRow(0,0,B00000110);
  lc.setRow(0,1,B11111000);
  lc.setRow(0,2,B00000110);
  lc.setRow(0,3,B11111000);
  delay(delaytime);
  // Step 9
  lc.setRow(0,0,B00000110);
  lc.setRow(0,1,B11111000);
  lc.setRow(0,2,B11111000);
  lc.setRow(0,3,B11111000);
  delay(delaytime);
}

void blankCBI() {          // used when monitorVCC == true
 // Step 0
  lc.setRow(0,0,B00000000);
  lc.setRow(0,1,B00000000);
  lc.setRow(0,2,B00000000);
  lc.setRow(0,3,B00000000);
  lc.setRow(0,4,B00000000);
  lc.setRow(0,5,B00000000);
  lc.setRow(0,6,B00000000);
}



void ESBoperatingSEQ() {          // used when ESBmode == true
 // Step 0
  lc.setRow(0,0,B01101101);
  lc.setRow(0,1,B00000110);
  lc.setRow(0,2,B11011011);
  lc.setRow(0,3,B00010011);
  lc.setRow(0,4,B11000011);
  lc.setRow(0,5,B01000011);
  lc.setRow(0,6,B00110011);
  getVCC();
  delay(delaytime);

 // Step 1
  lc.setRow(0,0,B01100101);
  lc.setRow(0,1,B00000110);
  lc.setRow(0,2,B10010111);
  lc.setRow(0,3,B00001011);
  lc.setRow(0,4,B00100001);
  lc.setRow(0,5,B11000001);
  lc.setRow(0,6,B10101011);
 getVCC();
  delay(delaytime);

 // Step 2 
  lc.setRow(0,0,B00000110);
  lc.setRow(0,1,B00010011);
  lc.setRow(0,2,B10110001);
  lc.setRow(0,3,B00001011);
  lc.setRow(0,4,B11101001);
  lc.setRow(0,5,B10100000);
  lc.setRow(0,6,B11101001);
  getVCC();
  delay(delaytime);
 
  // Step 3
  lc.setRow(0,0,B10000111);
  lc.setRow(0,1,B00010011);
  lc.setRow(0,2,B10110111); 
  lc.setRow(0,3,B11000010);
  lc.setRow(0,4,B00000011);
  lc.setRow(0,5,B10010000);
  lc.setRow(0,6,B10001000);
  getVCC();
 // l21off();
  delay(delaytime);

 // Step 4
  lc.setRow(0,0,B01010001);
  lc.setRow(0,1,B00010011);
  lc.setRow(0,2,B10010111); 
  lc.setRow(0,3,B11001000);
  lc.setRow(0,4,B11001000);
  lc.setRow(0,5,B10101001);
  lc.setRow(0,6,B00000001);
  getVCC();
  delay(delaytime);

 // Step 5
  lc.setRow(0,0,B01010101);
  lc.setRow(0,1,B01010011);
  lc.setRow(0,2,B00010011); 
  lc.setRow(0,3,B01001100);
  lc.setRow(0,4,B00000001);
  lc.setRow(0,5,B00010000);
  lc.setRow(0,6,B11000001);
  getVCC();
 // l21on();
  delay(delaytime);

  // Step 6
  lc.setRow(0,0,B00010011);
  lc.setRow(0,1,B00010011);
  lc.setRow(0,2,B00010011);
  lc.setRow(0,3,B10100110);
  lc.setRow(0,4,B10000001);
  lc.setRow(0,5,B00010000);
  lc.setRow(0,6,B11000001);
  getVCC();
  delay(delaytime);

 // Step 7
  lc.setRow(0,0,B00010011);
  lc.setRow(0,1,B00000110);
  lc.setRow(0,2,B10011011);
  lc.setRow(0,3,B00010011);
  lc.setRow(0,4,B11001010);
  lc.setRow(0,5,B11001000);
  lc.setRow(0,6,B10100000);
  getVCC();
 // l21off();
  delay(delaytime);

 // Step 8
  lc.setRow(0,0,B00010011);
  lc.setRow(0,1,B10100101);
  lc.setRow(0,2,B10000010);
  lc.setRow(0,3,B00110101);
  lc.setRow(0,4,B10110000);
  lc.setRow(0,5,B00000011);
  lc.setRow(0,6,B11001000);
  getVCC();
  delay(delaytime);

 // Step 9
  lc.setRow(0,0,B00001110);
  lc.setRow(0,1,B00010011);
  lc.setRow(0,2,B01000010); 
  lc.setRow(0,3,B00000110);
  lc.setRow(0,4,B10101011);
  lc.setRow(0,5,B00000001);
  lc.setRow(0,6,B10101011);
  getVCC();
  delay(delaytime);

 // Step 10
  lc.setRow(0,0,B01000011);
  lc.setRow(0,1,B00000110);
  lc.setRow(0,2,B00010011); 
  lc.setRow(0,3,B00000110);
  lc.setRow(0,4,B10101011);
  lc.setRow(0,5,B11101001);
  lc.setRow(0,6,B00000011);
  getVCC();
 // l22on();
 // l21on();
  delay(delaytime);

 // Step 11
  lc.setRow(0,0,B01100101);
  lc.setRow(0,1,B00110011);
  lc.setRow(0,2,B00010111); 
  lc.setRow(0,3,B00000110);
  lc.setRow(0,4,B10100000);
  lc.setRow(0,5,B11101001);
  lc.setRow(0,6,B10101011);
  getVCC();
  delay(delaytime);

 // Step 12
  lc.setRow(0,0,B00100000);
  lc.setRow(0,1,B00010011);
  lc.setRow(0,2,B10001000); 
  lc.setRow(0,3,B00011000);
  lc.setRow(0,4,B00000001);
  lc.setRow(0,5,B00000011);
  lc.setRow(0,6,B11001000);
  getVCC();
//  l22off();
//  l21off();
  delay(delaytime);

 // Step 13
  lc.setRow(0,0,B10000000);
  lc.setRow(0,1,B00010011);
  lc.setRow(0,2,B10110101); 
  lc.setRow(0,3,B10010110);
  lc.setRow(0,4,B00000001);
  lc.setRow(0,5,B11101001);
  lc.setRow(0,6,B11101001);
  getVCC();
  delay(delaytime);

 // Step 14
  lc.setRow(0,0,B10100110);
  lc.setRow(0,1,B01010001);
  lc.setRow(0,2,B01010011); 
  lc.setRow(0,3,B10100000);
  lc.setRow(0,4,B11001000);
  lc.setRow(0,5,B10110000);
  lc.setRow(0,6,B00000011);
  getVCC();
 // l21on();
  delay(delaytime);

 // Step 15
  lc.setRow(0,0,B10101000);
  lc.setRow(0,1,B01010001);
  lc.setRow(0,2,B00010001); 
  lc.setRow(0,3,B10000000);
  lc.setRow(0,4,B11101001);
  lc.setRow(0,5,B11101001);
  lc.setRow(0,6,B10101011);
  getVCC();
  delay(delaytime);

 // Step 16
  lc.setRow(0,0,B10000011);
  lc.setRow(0,1,B00100000);
  lc.setRow(0,2,B10010011); 
  lc.setRow(0,3,B11000010);
  lc.setRow(0,4,B10101011);
  lc.setRow(0,5,B00000001);
  lc.setRow(0,6,B00000011);
  getVCC();
//  l21off();
  delay(delaytime);

 // Step 17
  lc.setRow(0,0,B10000010);
  lc.setRow(0,1,B00010011);
  lc.setRow(0,2,B00010010); 
  lc.setRow(0,3,B11000010);
  lc.setRow(0,4,B00110000);
  lc.setRow(0,5,B11101001);
  lc.setRow(0,6,B00110000);
  getVCC();
  delay(delaytime);

 // Step 18
  lc.setRow(0,0,B01100101);
  lc.setRow(0,1,B00010011);
  lc.setRow(0,2,B00100000); 
  lc.setRow(0,3,B00000110);
  lc.setRow(0,4,B11001000);
  lc.setRow(0,5,B00011001);
  lc.setRow(0,6,B01000001);
  getVCC();
//  l21on();
  delay(delaytime);

 // Step 19
  lc.setRow(0,0,B10100011);
  lc.setRow(0,1,B00010011);
  lc.setRow(0,2,B01010101); 
  lc.setRow(0,3,B01100101);
  lc.setRow(0,4,B00110000);
  lc.setRow(0,5,B01010000);
  lc.setRow(0,6,B01100001);
  getVCC();
  delay(delaytime);

 // Step 20
  lc.setRow(0,0,B10000000);
  lc.setRow(0,1,B10000000);
  lc.setRow(0,2,B01010001); 
  lc.setRow(0,3,B00001011);
  lc.setRow(0,4,B11101001);
  lc.setRow(0,5,B11001000);
  lc.setRow(0,6,B11001000);
  getVCC();
 // l21off();
  delay(delaytime);

 // Step 21
  lc.setRow(0,0,B00000110);
  lc.setRow(0,1,B00100000);
  lc.setRow(0,2,B11011000); 
  lc.setRow(0,3,B01001100);
  lc.setRow(0,4,B10101011);
  lc.setRow(0,5,B01010000);
  lc.setRow(0,6,B00000010);
  getVCC();
  delay(delaytime);

 // Step 22
  lc.setRow(0,0,B01000011);
  lc.setRow(0,1,B00011000);
  lc.setRow(0,2,B10011000); 
  lc.setRow(0,3,B01000011);
  lc.setRow(0,5,B00000010);
  lc.setRow(0,6,B11001010);
  getVCC();
//  l21on();
  delay(delaytime);

 // Step 25
  lc.setRow(0,0,B00101100);
  lc.setRow(0,1,B00010011);
  lc.setRow(0,2,B01011010); 
  lc.setRow(0,3,B01000011);
  lc.setRow(0,4,B01010000);
  lc.setRow(0,5,B10101011);
  lc.setRow(0,6,B11001010);
  getVCC();
  delay(delaytime);

 // Step 26
  lc.setRow(0,0,B10101010);
  lc.setRow(0,1,B00100000);
  lc.setRow(0,2,B01001100); 
  lc.setRow(0,3,B01000010);
  lc.setRow(0,4,B00000011);
  lc.setRow(0,5,B11001010);
  lc.setRow(0,6,B01010000);
  getVCC();
 // l21off();
  delay(delaytime);

 // Step 27
  lc.setRow(0,0,B00000110);
  lc.setRow(0,1,B00000110);
  lc.setRow(0,2,B10001100); 
  lc.setRow(0,3,B00000110);
  lc.setRow(0,4,B01001000);
  lc.setRow(0,5,B01010000);
  lc.setRow(0,6,B00000010);
  getVCC();
  delay(delaytime);

 // Step 28
  lc.setRow(0,0,B00000110);
  lc.setRow(0,1,B00010011);
  lc.setRow(0,2,B00111000); 
  lc.setRow(0,3,B01001100);
  lc.setRow(0,4,B11001010);
  lc.setRow(0,5,B00000001);
  lc.setRow(0,6,B10101011);
  getVCC();
//  l21on();
  delay(delaytime);

 // Step 29
  lc.setRow(0,0,B00000110);
  lc.setRow(0,1,B00010011);
  lc.setRow(0,2,B01001100); 
  lc.setRow(0,3,B01000011);
  lc.setRow(0,4,B00000011);
  lc.setRow(0,5,B11001000);
  lc.setRow(0,6,B11001000);
  getVCC();
  delay(delaytime);

}

void allON(){
// Step 4
  lc.setRow(0,0,B11111111);
  lc.setRow(0,1,B11111111); 
  lc.setRow(0,2,B11111111);
  lc.setRow(0,3,B11111111);
  lc.setRow(0,0,B11111111);
  lc.setRow(0,1,B11111111); 
  lc.setRow(0,2,B11111111);
  lc.setRow(0,3,B11111111); 
  delay(300);

}



void getVCC(){
 value = analogRead(analoginput);// this must be between 0.0 and 5.0 - otherwise you'll let the blue smoke out of your ar
 vout= (value * 5.0)/1024.0;  //voltage coming out of the voltage divider
 vin = vout / (R2/(R1+R2));  //voltage to display
 
 // Serial.print("Volt Out = ");                                  // DEBUG CODE
 // Serial.print(vout, 1);   //Print float "vin" with 1 decimal   // DEBUG CODE

   
//  Serial.print("\tVolts Calc = ");                             // DEBUG CODE
// Serial.print(vin, 1);   //Print float "vin" with 1 decimal   // DEBUG CODE
 
 if (vin >= greenVCC) {
   l21on();
   l22on();
   l23on();
 //  Serial.println("\tTurn on Led l23 - GREEN");              // DEBUG CODE
 } else if (vin >= yellowVCC) {
     l21on();
     l22on();
     l23off();
  //   Serial.println("\tTurn on Led l22 - YELLOW");           // DEBUG CODE
 } else {              // voltage is below yellowVCC value, so turn on l23.
     l21on();
     l22off();
     l23off();
  //   Serial.println("\tTurn on Led l21 - RED");              // DEBUG CODE

 }
}



void loop() { 
  
 if (monitorVCC == true){
   getVCC();          // Get Battery Status via the voltage divider circuit & display status
 }
 if (ESBmode==false) {operatingSEQ(); lc.clearDisplay(0);}
   else {ESBoperatingSEQ();} // use ESBoperatingSEQ() if you want the charge lights flickering.
   // blankCBI();
   
  

   
 }
  




