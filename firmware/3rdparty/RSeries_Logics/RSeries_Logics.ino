/*
LE_bare_bones
=============
by Paul Murphy (joymonkey@gmail.com)
This sketch is a intended to be a minimal implimentation. It includes code for standard
logic display animations only (no communication or PSI code). Intended for using as groundwork
for a more complicated sketch.
Requires the FastLED library : https://github.com/FastLED/FastLED/releases/
*/

#define LOGIC 2       // 1 for Front Logic, 2 for Rear Logic

#define PCBVERSION 2  // 2 for Sept 2014 logics (Kenny & 3PO PCBs) or newer
                      // 1 for older logics (Naboo logo on PCB backs)

#define maxBrightness 128  // how bright the LEDs can get with the Bright trimpot turned up all the way
                           // limit this to something under 192 to conserve eyeballs and batteries
                           
#define keyColors 5
#define Tweens 10   

#define DEBUG 0

#include "FastSPI_LED2.h"
#define DATA_PIN 6
#include <avr/pgmspace.h>

byte hueVal;
#define keyPin A0   //pin used to adjust Key Color pause time
#define twnPin A1   //pin used to adjust Tween Color pause time
#define briPin A2   //pin used to adjust global brightness
#define huePin A3   //pin used to shift color hues
#define SPEEDPIN 3  //pin that can be jumped to enable the Delay & Fade trimpots

#if (LOGIC==1)
  // Front Logic specifics...
  const byte colorPal[5][3]PROGMEM = { {170,0,0} , {170,255,87} , {166,255,200} , {154,84,150} , {174,0,200} }; //black, blues & whites
  byte tweenPause=5;
  byte keyPause=30;
  #define MatrixWidth  8
  #define MatrixHeight 10  
  #if (PCBVERSION==2)
    //mapping for newer FLD PCBs (40 LEDs per PCB, lower FLD upside-down)...
    const byte ledMap[]PROGMEM = { 
     0, 1, 2, 3, 4, 5, 6, 7,
    15,14,13,12,11,10, 9, 8,
    16,17,18,19,20,21,22,23,
    31,30,29,28,27,26,25,24,
    32,33,34,35,36,37,38,39,    
    79,78,77,76,75,74,73,72,
    64,65,66,67,68,69,70,71,
    63,62,61,60,59,58,57,56,
    48,49,50,51,52,53,54,55,
    47,46,45,44,43,42,41,40};
  #else
    //mapping for FLD boards from first run (with 48 LEDs per PCB)
    const byte ledMap[]PROGMEM = {
    15,14,13,12,11,10, 9, 8,
    16,17,18,19,20,21,22,23,
    31,30,29,28,27,26,25,24,
    32,33,34,35,36,37,38,39,
    47,46,45,44,43,42,41,40, //
    88,89,90,91,92,93,94,95, //
    87,86,85,84,83,82,81,80,
    72,73,74,75,76,77,78,79,
    71,70,69,68,67,66,65,64,
    56,57,58,59,60,61,62,63};  
  #endif
#else
  //Rear Logic Specifics...
  const byte colorPal[5][3]PROGMEM = { {87,0,0} , {87,206,105} , {79,255,184} , {18,255,250} , {0,255,214} }; //black, greens, yellows & reds
  byte tweenPause=8;
  byte keyPause=60;
  #define MatrixWidth  24
  #define MatrixHeight 4
  #if (PCBVERSION==2)
    //mapping for single RLD PCB (second parts run on)...
    const byte ledMap[]PROGMEM = {
     0, 1, 2,28, 3,27, 4,26, 5,25, 6, 7, 8, 9,22,10,21,11,20,12,19,13,14,15,
    31,30,29,32,33,34,35,36,37,38,39,24,23,40,41,42,43,44,45,46,47,18,17,16,
    64,65,66,63,62,61,60,59,58,57,56,71,72,55,54,53,52,51,50,49,48,77,78,79,
    95,94,93,67,92,68,91,69,90,70,89,88,87,86,73,85,74,84,75,83,76,82,81,80};
  #else
    //mapping for first RLD (two PCBs soldered together)
    const byte ledMap[]PROGMEM = {
     0, 1, 2, 3, 4, 5, 6, 7,48,49,50,51,52,53,54,55,
    15,14,13,12,11,10, 9, 8,63,62,61,60,59,58,57,56,
    16,17,18,19,20,21,22,23,64,65,66,67,68,69,70,71,
    31,30,29,28,27,26,25,24,79,78,77,76,75,74,73,72,
    32,33,34,35,36,37,38,39,80,81,82,83,84,85,86,87,
    47,46,45,44,43,42,41,40,95,94,93,92,91,90,89,88};
  #endif
#endif

#define NUM_LEDS (MatrixWidth*MatrixHeight)

//typically we have 5 key colors and 10 tween colors
// http://rseries.net/logic2/color/?keys=5&tweens=10 was used to wrap my little head around some of this
//    Key Colors : 00 __ __ __ __ __ __ __ __ __ __ 11 __ __ __ __ __ __ __ __ __ __ 22 __ __ __ __ __ __ __ __ __ __ 33 __ __ __ __ __ __ __ __ __ __ 44 
// Actual Colors : 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 
//Bizarro Colors :    87 86 85 84 83 82 81 80 79 78 77 76 75 74 73 72 71 70 69 68 67 66 65 64 63 62 61 60 59 58 57 56 55 54 53 52 51 50 49 48 47 46 45 
//so we've got 45 actual colors, but we pretend we've got 88.
//color numbers between 45 and 88 are 'bizarro' colors; just a color from the original 45, but referenced in reverse

//byte totalColors=(keyColors+(Tweens*(keyColors-1))); //typically 45
#define totalColors (keyColors+(Tweens*(keyColors-1)))
#define totalColorsWBiz ((totalColors*2)-2)
CRGB leds[NUM_LEDS]; // This is an array of leds.  One item for each led in your strip.
byte LEDstatus[NUM_LEDS][2]; //an array that will hold color number and pause value for each LED

//function takes a color number (that may be bizarro) and returns an actual color number
byte actualColorNum(byte x) {
      if (x<totalColors) return(x);
      else return((totalColors-2)-(x-totalColors)) ;
}

byte workColor[3]; //a temporary color
void setWorkColor(byte findcolor) {
    findcolor=actualColorNum(findcolor); //switches the color number to a "real" one if it's a bizarro number
    //if x is a key color (a multiple of Tweens+1), just set that and we're done...
    if (findcolor%(Tweens+1)==0)
      for (byte x=0; x<3; x++) workColor[x]=pgm_read_byte(&colorPal[findcolor/(Tweens+1)][x]);
    else {
       //the color is somewhere between upperKey and lowerKey (which is just upperKey-1)
       byte upperKey=ceil(findcolor/(Tweens+1)+1);
       //now which tween are we dealing with? how higher than the lower key is it?
       byte tweenNumDiff=findcolor-((upperKey-1)*(Tweens+1));
       //now we'll figure out the amount each tween needs to change as it steps towards the upper
       //we do this 3 times (Hue, Saturation, Value)
       for (byte x=0; x<3; x++) {
         byte hsvdiff=(pgm_read_byte(&colorPal[upperKey][x]) - pgm_read_byte(&colorPal[upperKey-1][x])) / (Tweens+1);
         workColor[x]=(pgm_read_byte(&colorPal[upperKey-1][x])+(hsvdiff*tweenNumDiff));
       }
       //now workColor *should* hold the HSV values of our color, without us having to define a big array of colors
       //right?
    }  
}

//a function that updates the color number and pause time for a given LED
void updateLED(byte LEDnum, byte hueVal) {
    if (LEDstatus[LEDnum][1]!=0) { //LED is paused
      LEDstatus[LEDnum][1]=LEDstatus[LEDnum][1]-1; //reduce the LEDs pause number and check back next loop
    }
    else{
      //increase the color number in LEDstatus...
      LEDstatus[LEDnum][0]=LEDstatus[LEDnum][0]+1;
      //if we've gone beyond the possible color numbers, bring it back to 0...
      if (LEDstatus[LEDnum][0]>=totalColorsWBiz) LEDstatus[LEDnum][0]=0;
      //now lets set a pause value for this LED...
      if (LEDstatus[LEDnum][0]%(keyColors+1)==0) {
        //color is a key color, lets give it a new pause value between 0 and keyPause
        LEDstatus[LEDnum][1]=random(keyPause);
      }
      else LEDstatus[LEDnum][1]=tweenPause; //it was a tween so its pause value is set accordingly
      //now lets set the actual color of this LED...
      setWorkColor(LEDstatus[LEDnum][0]);
      leds[LEDnum].setHSV((workColor[0]+hueVal), workColor[1], workColor[2]);
    }  
}  


void setup() {
  delay(50);
  #if (DEBUG>0)
  Serial.begin(9600);         
  #endif 
  randomSeed(analogRead(0)); //helps keep random numbers more randomy 
  hueVal = analogRead(huePin)/4; //read the value of the hue trimpot, colors will have their Hue shifted by this amount
  FastLED.setBrightness(map(analogRead(briPin),0,1024,0,maxBrightness)); //read the value of the hue trimpot and map it down to an allowed brightness
  if (digitalRead(SPEEDPIN)==HIGH) {
    //jumper is on S3, use pause values based on the Delay and Fade trimpots
    keyPause=analogRead(keyPin)/4;
    tweenPause=analogRead(twnPin)/10;
  }  
  FastLED.addLeds<WS2812, 6, GRB>(leds, NUM_LEDS);
  //lets hand out some random color numbers to our LEDs and turn them on...
  for(byte x = 0; x < NUM_LEDS; x++) {
      //x=ledMap[x];
      LEDstatus[x][0]=random(totalColorsWBiz);
      if (LEDstatus[x][0]%(Tweens+1)==0) LEDstatus[x][1]=random(keyPause);
      else LEDstatus[x][1]=random(tweenPause);
      setWorkColor(LEDstatus[x][0]);
      leds[x].setHSV((workColor[0]+hueVal), workColor[1], workColor[2]);
      FastLED.show(); 
      delay(5);
  }    
}


#if (DEBUG==1)
long lastMillis = 0;
int loopcount;
#endif


void loop() {
  #if (DEBUG==1)
    long currentMillis = millis();
    loopcount++;
  #endif
  
  //update each LED...
  for(byte x = 0; x < NUM_LEDS; x++) {
    updateLED(x, hueVal);
  } 
  FastLED.show();  
  
  //read the trimpots...
  hueVal = analogRead(huePin)/4;
  FastLED.setBrightness(map(analogRead(briPin),0,1024,0,maxBrightness)); 
  if (digitalRead(SPEEDPIN)==HIGH) {
    keyPause = analogRead(keyPin)/4;  
    tweenPause = analogRead(twnPin)/10;
  }
  //
  
  #if (DEBUG==1)
  if(currentMillis - lastMillis > 1000){
    Serial.println(loopcount);
    lastMillis = currentMillis;
    loopcount = 0;
  }
  #endif
}
