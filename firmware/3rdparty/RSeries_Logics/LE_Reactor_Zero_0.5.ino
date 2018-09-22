/*
    Logic Reactor Zero
    Basic Logic Display Sketch by Paul Murphy 2018-09-03
	This sketch is a work in progress and currently only supports the Reactor Zero board.
	Teensy Reactor support is in the works.
*/

#define LEDLIB 1 //0 for FastLED, 1 for Adafruit_NeoPixel, 2 for NeoPixelBus
//the sketch will run at about 120 loops per second with NeoPixel, 109 with NeoPixelBus, but ironically only 80 with FastLED
//for this reason, FastLED is not recommended

#define DEBUG 0  //change to 1 to print some useful stuff to the serial monitor, 2 will also check loops-per-second

#define TEECESPSI 1  //enable support for two Teeces PSI's (oh, the humanity!). 0=disabled, 1=enabled

#define ENABLE_JEDI_SERIAL 0
#define BAUDRATE 19200

//default "factory" settings...
#define DFLT_FRONT_FADE 3
#define DFLT_FRONT_DELAY 60
#define DFLT_REAR_FADE 10
#define DFLT_REAR_DELAY 400
#define MAX_BRIGHTNESS 180
#define DFLT_FRONT_HUE 0
#define DFLT_REAR_HUE 0
#define DFLT_FRONT_PAL 0
#define DFLT_REAR_PAL 1
#define DFLT_FRONT_BRI 100
#define DFLT_REAR_BRI 70
#define DFLT_FRONT_DESAT 0
#define DFLT_REAR_DESAT 0

#define MAX_FADE 15
#define MAX_DELAY 500
#define MIN_DELAY 10
#define MIN_BRI 10

//we store the color pallets here as an array of colors in HSV (Hue,Saturation,Value) format
#define NUM_PALS 4
const byte keyColors[NUM_PALS][4][3] = {
  { {170, 255, 0} , {170, 255, 85} , {170, 255, 170} , {170, 0,170}  } , //front colors
  { {90, 235, 0}  , {75, 255, 250} , {30, 255, 184}  , {0, 255, 250}  } , //rear colors (hues: 87=bright green, 79=yellow green, 45=orangey yellow, 0=red)
  { {0, 255, 0}   , {0, 255, 0}   , {0, 255, 100}   , {0, 255, 250}  } , //monotone (black to solid red)
  { {0, 255, 0}   , {0, 255, 250}   , {40, 255, 0}   , {40, 255, 250}}  //dual color red and yellow
};

#define FrontLEDCount 80
#define RearLEDCount 96
#define TWEENS 20

#define SWAPADJ 1 //on some early Reactor Zero boards the Front/Rear switch was labelled incorrectly, this will fix that
                  //1 for red PCB , 0 for green

//a struct that holds the current color number and pause value of each LED (when pause value hits 0, the color number gets changed)
//to save SRAM, we don't store the "direction" anymore, instead we pretend that instead of having 16 colors, we've got 31 (16 that cross-fade up, and 15 "bizarro" colors that cross-fade back in reverse)
struct LEDstat {
  byte colorNum;
  int colorPause;
};
LEDstat frontLEDstatus[FrontLEDCount];
LEDstat rearLEDstatus[RearLEDCount];
#define TOTALCOLORS (4+(TWEENS*(3)))
#define TOTALCOLORSWBIZ ((TOTALCOLORS*2)-2)
byte allColors[2][TOTALCOLORS][3]; //the allColor array will comprise of two color palettes

#define DEBUG_SERIAL SerialUSB
#define JEDI_SERIAL Serial1
#define numChars 8
#define CMD_MAX_LENGTH 64 // maximum number of characters in a command (63 chars since we need the null termination)
char cmdString[CMD_MAX_LENGTH]; 
char ch;
bool command_available; 
bool doingSerialStuff;
unsigned long serialMillis = millis();
#define serialMillisWait 10 //this is how many milliseconds we hold off from sending data to LEDs if serial data has started coming in

unsigned long loopcount;

#define TIMECHECKMS 10000

#define FRONT_PIN 5
#define REAR_PIN 3
#define STATUSLED_PIN 8

#include <Adafruit_NeoPixel.h>
Adafruit_NeoPixel frontLEDs = Adafruit_NeoPixel(FrontLEDCount, FRONT_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel rearLEDs = Adafruit_NeoPixel(RearLEDCount, REAR_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel statusLED = Adafruit_NeoPixel(1, STATUSLED_PIN, NEO_GRB + NEO_KHZ800);

bool frontRear;

bool flipFlop=0;
bool prevFlipFlop=1;
#define slowBlink 300
#define fastBlink 50
int flipFlopLoops = slowBlink;

#define delayPin A0
#define fadePin A1
#define briPin A2
#define huePin A3
#if (SWAPADJ==0)
  #define FADJ_PIN 4
  #define RADJ_PIN 2
#else  
  #define FADJ_PIN 2
  #define RADJ_PIN 4
#endif
#define PAL_PIN 9
//unsigned long palPinMillis = millis();
unsigned int palPinLoops;
bool palPinStatus = 1;
bool prevPalPinStatus = 1;
byte adjMode, prevAdjMode, startAdjMode;
//unsigned long adjMillis = millis();
unsigned int adjLoops;
#define adjLoopMax 90000
#define adjLoopMin 500
int startTrimpots[4]; //will hold trimpot values when adjustments start being made
bool trimEnabled[4]; //during adjustment, if trimpot has moved beyond specified threshold it will be enabled here
int loopTrimpots[4]; //will hold trimpot values when adjustments start being made
bool adjEnabled[4]; //tells us if a trimpot has been adjusted beyond adj_threshold
byte adjThreshold = 5;
byte onOff[4]={0,1,1,1}; //turns on/off each logic display

#if (DEBUG>0)
  #include <RTCZero.h>
  RTCZero rtc;
  byte rtcSeconds, prevRtcSeconds;
#endif

typedef struct {
  unsigned int writes; //keeps a count of how many times we've written settings to flash
  byte maxBri;
  int frontDelay; byte frontFade; byte frontBri; byte frontHue; byte frontPalNum; byte frontDesat;
  int rearDelay;  byte rearFade;  byte rearBri;  byte rearHue;  byte rearPalNum; byte rearDesat;
} Settings;
#include <FlashStorage.h> //see StoreNameAndSurname example
FlashStorage(my_flash_store, Settings);
Settings mySettings;
Settings tempSettings;

//FastLED has built in HSV conversions, for other libraries we need this helper function...
byte rgbColor[3];
void hsv2rgb(uint8_t hue, uint8_t sat, uint8_t val) {
  uint16_t h = hue * 3;
  uint8_t r, g, b;
  //uint8_t value = dim_curve[ val ]; //dim_curve can be found in WS2812.h if necessary
  //uint8_t invsat = dim_curve[ 255 - sat ];
  uint8_t value = val;
  uint8_t invsat = 255 - sat;
  uint8_t brightness_floor = (value * invsat) / 256;
  uint8_t color_amplitude = value - brightness_floor;
  uint8_t section = h >> 8; // / HSV_SECTION_3; // 0..2
  uint8_t offset = h & 0xFF ; // % HSV_SECTION_3;  // 0..255
  uint8_t rampup = offset; // 0..255
  uint8_t rampdown = 255 - offset; // 255..0
  uint8_t rampup_amp_adj   = (rampup   * color_amplitude) / (256);
  uint8_t rampdown_amp_adj = (rampdown * color_amplitude) / (256);
  uint8_t rampup_adj_with_floor   = rampup_amp_adj   + brightness_floor;
  uint8_t rampdown_adj_with_floor = rampdown_amp_adj + brightness_floor;
  if ( section ) {
    if ( section == 1) {
      // section 1: 0x40..0x7F
      r = brightness_floor;
      g = rampdown_adj_with_floor;
      b = rampup_adj_with_floor;
    }
    else {
      // section 2; 0x80..0xBF
      r = rampup_adj_with_floor;
      g = brightness_floor;
      b = rampdown_adj_with_floor;
    }
  }
  else {
    // section 0: 0x00..0x3F
    r = rampdown_adj_with_floor;
    g = rampup_adj_with_floor;
    b = brightness_floor;
  }
  rgbColor[0] = r;
  rgbColor[1] = g;
  rgbColor[2] = b;
}

byte hsvColor[3];
void calcColor(byte palNum, int colorNum) {
  if (colorNum % (TWEENS + 1) == 0) {
    //colorNum is a key, life is easy
    for (byte x = 0; x < 3; x++) {
      hsvColor[x] = keyColors[palNum][(colorNum / TWEENS)][x];
    }
  }
  else {
    //this color is a tween between two keys, calculate its H, S and V values. Oh the humanity!
    byte upperKey = ceil(colorNum / (TWEENS + 1) + 1);
    byte tweenNumDiff = colorNum - ((upperKey - 1) * (TWEENS + 1));
    for (byte x = 0; x < 3; x++) {
      hsvColor[x] = ( keyColors[palNum][upperKey - 1][x] + (tweenNumDiff *  (keyColors[palNum][upperKey][x] - keyColors[palNum][upperKey - 1][x]) / (TWEENS + 1)  ));
    }
  }
}

void calcColors(byte palNum, byte logicNum) {
  #if (DEBUG>0)
    if (logicNum == 0) {
      DEBUG_SERIAL.print(F("Front"));
      DEBUG_SERIAL.print(F(" Colors : hue+"));
      DEBUG_SERIAL.print(mySettings.frontHue);
      DEBUG_SERIAL.print(F("  desat"));
      DEBUG_SERIAL.print(mySettings.frontDesat);
      DEBUG_SERIAL.print(F("  bri"));
      DEBUG_SERIAL.println(byte(float(mySettings.maxBri) / 255 * mySettings.frontBri));
    }
    else {
      DEBUG_SERIAL.print(F("Rear"));
      DEBUG_SERIAL.print(F(" Colors : hue+"));
      DEBUG_SERIAL.print(mySettings.rearHue);
      DEBUG_SERIAL.print(F("  desat"));
      DEBUG_SERIAL.print(mySettings.rearDesat);
      DEBUG_SERIAL.print(F("  bri"));
      DEBUG_SERIAL.println(byte(float(mySettings.maxBri) / 255 * mySettings.rearBri));
    }
         
  #endif
  for (byte col = 0; col < TOTALCOLORS; col++) {
    calcColor(palNum, col);
    //now hsvColor contains our color
    //scale down the Val based on our brightness settings
    //say maxBri setting is 200/255 and frontBri setting is 50/255 , our value will be scaled to 200/255*50
    if (logicNum == 0) {      
      hsvColor[0] = hsvColor[0] + mySettings.frontHue;
      if (mySettings.frontDesat>0) hsvColor[1] = map(hsvColor[1],0,255,0,mySettings.frontDesat); //adjust for our stored desaturation value
      hsvColor[2] = map(hsvColor[2], 0, 255, 0, byte(float(mySettings.maxBri) / 255 * mySettings.frontBri) );
    }
    else {
      hsvColor[0] = hsvColor[0] + mySettings.rearHue;
      //if (mySettings.rearDesat>0) hsvColor[1] = map(hsvColor[1],0,255,0,mySettings.rearDesat); //adjust for our stored desaturation value
      //if (mySettings.rearDesat>0 && hsvColor[1]-mySettings.rearDesat>0) hsvColor[1] = hsvColor[1]-mySettings.rearDesat;
      if (mySettings.rearDesat>0) {
        #if (DEBUG>0)
        DEBUG_SERIAL.print(F("S was "));
        DEBUG_SERIAL.print(hsvColor[1]);
        DEBUG_SERIAL.print(F(" now "));
        #endif
        hsvColor[1] = map(hsvColor[1],0,255,0,mySettings.rearDesat); // 3K500x0D
        #if (DEBUG>0)
        DEBUG_SERIAL.println(hsvColor[1]);
        #endif
      }
      hsvColor[2] = map(hsvColor[2], 0, 255, 0, byte(float(mySettings.maxBri) / 255 * mySettings.rearBri) );
    }
    //now lets throw it into the allColors array in RGB format
    hsv2rgb(hsvColor[0], hsvColor[1], hsvColor[2]);
    for (byte x = 0; x < 3; x++) {
      allColors[logicNum][col][x] = rgbColor[x];
    }
  }
}

void setStatusLED() {
    if (flipFlop == 0) {
    if (adjMode == 0) statusLED.setPixelColor(0, 0, 0, 2); //blue
    else if (adjMode == 1) statusLED.setPixelColor(0, 0, 0, 2); //blue
    else if (adjMode == 3) statusLED.setPixelColor(0, 0, 2, 0); //green
    //flipFlop = 1;
    }
    else {
    if (adjMode == 0) statusLED.setPixelColor(0, 2, 0, 0); //red
    else if (adjMode == 1) statusLED.setPixelColor(0, 2, 2, 2); //white
    else if (adjMode == 3) statusLED.setPixelColor(0, 2, 2, 0); //orangey
    //flipFlop = 0;
    }
}

void checkTrimpots(bool startTrim = 0) {
  //check the current trimpot values and put them into startTrimpots[] or loopTrimpots[]
  if (startTrim == 0) {
    loopTrimpots[0] = map(analogRead(delayPin), 0, 1023, MIN_DELAY, MAX_DELAY);
    loopTrimpots[1] = map(analogRead(fadePin), 0, 1023, 0, MAX_FADE);
    loopTrimpots[2] = map(analogRead(briPin), 0, 1023, MIN_BRI, mySettings.maxBri);
    loopTrimpots[3] = map(analogRead(huePin), 0, 1023, 0, 255);
  }
  else {
    startTrimpots[0] = map(analogRead(delayPin), 0, 1023, MIN_DELAY, MAX_DELAY);
    startTrimpots[1] = map(analogRead(fadePin), 0, 1023, 0, MAX_FADE);
    startTrimpots[2] = map(analogRead(briPin), 0, 1023, MIN_BRI, mySettings.maxBri);
    startTrimpots[3] = map(analogRead(huePin), 0, 1023, 0, 255);
  }
}

void compareTrimpots(byte adjMode = 0) {
  checkTrimpots();
  for (byte x = 0; x < 4; x++) {
    if ( x > 1 && adjEnabled[x] == 0 && ( startTrimpots[x] - loopTrimpots[x] > adjThreshold || loopTrimpots[x] - startTrimpots[x] > adjThreshold )  ) { //compare Brightness and Hue using adjThreshold, as changes there can be a lot of work
      adjEnabled[x] = 1;
    }
    else if ( adjEnabled[x] == 0 && startTrimpots[x] != loopTrimpots[x] ) {
      adjEnabled[x] = 1;
      #if (DEBUG>0)
        DEBUG_SERIAL.print(x);
        DEBUG_SERIAL.println(F("ENABLED"));
      #endif
    }
    else if ( adjEnabled[x] == 1) {
      //if (loopTrimpots[x] != startTrimpots[x]) {
      if ((x==1 && loopTrimpots[x] != startTrimpots[x]) || (loopTrimpots[x]-startTrimpots[x]>=2 || startTrimpots[x]-loopTrimpots[x]>=2)) {
        #if (DEBUG>0)
          DEBUG_SERIAL.print(x);
          DEBUG_SERIAL.print("=");
          DEBUG_SERIAL.println(loopTrimpots[x]);
        #endif
        //adjustment is enabled for this pot, if settings have changed see if we need to recalc colors and all that jazz
        if (adjMode == 1) {
            //FRONT ADJUSTMENTS...
            if (x == 0) mySettings.frontDelay = loopTrimpots[x];
            else if (x == 1) mySettings.frontFade = loopTrimpots[x];
            else if (x == 2) {
              //map(hsvColor[2],0,255,0,byte(float(mySettings.maxBri)/255*mySettings.frontBri) )
              //mySettings.frontBri = map(loopTrimpots[x], 0, 1023, 0, 255); //if loopTrimpots were int's
              mySettings.frontBri = loopTrimpots[x];
              calcColors(mySettings.frontPalNum, 0);
            }
            else if (x == 3) {
              //mySettings.frontHue = map(loopTrimpots[x], 0, 1023, 0, 255); //if loopTrimpots were int's
              mySettings.frontHue = loopTrimpots[x];
              calcColors(mySettings.frontPalNum, 0);
            }
        }
        if (adjMode == 3) {
            if (x == 0) mySettings.rearDelay = loopTrimpots[x];
            else if (x == 1) mySettings.rearFade = loopTrimpots[x];
            else if (x == 2) {
              //map(hsvColor[2],0,255,0,byte(float(mySettings.maxBri)/255*mySettings.frontBri) )
              //mySettings.frontBri = map(loopTrimpots[x], 0, 1023, 0, 255); //if loopTrimpots were int's
              mySettings.rearBri = loopTrimpots[x];
              calcColors(mySettings.rearPalNum, 1);
            }
            else if (x == 3) {
              //mySettings.frontHue = map(loopTrimpots[x], 0, 1023, 0, 255); //if loopTrimpots were int's
              mySettings.rearHue = loopTrimpots[x];
              calcColors(mySettings.rearPalNum, 1);
            }
        }
      }
      //save the values for the next loop
      startTrimpots[x] = loopTrimpots[x];
    }
  }
}

void checkAdjSwitch() {
  if (digitalRead(FADJ_PIN) == 0 && prevAdjMode != 1 && startAdjMode == 0) {
    adjMode = 1;
    checkTrimpots(1); //put initial trimpot values into startTrimpots[]
#if (DEBUG>0)
    DEBUG_SERIAL.println(F("adj Front"));
#endif
    //adjMillis = millis();
    adjLoops=0;
    flipFlopLoops = fastBlink;
  }
  else if (digitalRead(RADJ_PIN) == 0 && prevAdjMode != 3 && startAdjMode == 0) {
    adjMode = 3;
    checkTrimpots(1); //put initial trimpot values into startTrimpots[]
#if (DEBUG>0)
    DEBUG_SERIAL.println(F("adj Rear"));
#endif
    //adjMillis = millis();
    adjLoops=0;
    flipFlopLoops = fastBlink;
  }
  else if ( (prevAdjMode != 0 && digitalRead(RADJ_PIN) == 1 && digitalRead(FADJ_PIN) == 1 && startAdjMode == 0) || (adjLoops>adjLoopMax) ) {
      #if (DEBUG>0)
        if (adjLoops>adjLoopMax) DEBUG_SERIAL.println(F("MAXED OUT")); 
      #endif
      //if we were in previous adjMode for way too long, save settings here  SAVE STUFF HERE and go back to regular mode!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      if (adjLoops > adjLoopMin)  {
        #if (DEBUG>0)
          DEBUG_SERIAL.println(F("save"));
          DEBUG_SERIAL.print(F("FDelay "));
          DEBUG_SERIAL.println(mySettings.frontDelay);
          DEBUG_SERIAL.print(F("FFade "));
          DEBUG_SERIAL.println(mySettings.frontFade);
          DEBUG_SERIAL.print(F("FHue "));
          DEBUG_SERIAL.println(mySettings.frontHue);
          DEBUG_SERIAL.print(F("FBri "));
          DEBUG_SERIAL.println(mySettings.frontBri);
          DEBUG_SERIAL.print(F("FPal "));
          DEBUG_SERIAL.println(mySettings.frontPalNum);        
        #endif
        mySettings.writes++;
        my_flash_store.write(mySettings);
        if (adjLoops>adjLoopMax) {
          startAdjMode=adjMode;
          adjLoops=0;
        }
        adjMode = 0;
        for (byte x = 0; x < 4; x++) adjEnabled[x] = 0; //
        flipFlopLoops = slowBlink;  
        //flipFlop=0; prevFlipFlop=1;           
      }
  }
  else if (digitalRead(RADJ_PIN) == 1 && digitalRead(FADJ_PIN) == 1 && startAdjMode != 0) {
    //adjMode didn't start off centered, which could have messed us up.
    //now it is centered though, so let's get back to our normal state.
    startAdjMode = 0;
  }
  if (adjMode != prevAdjMode) {
    statusBlink(2, 250, 1, 0, 2); //blink purple 2 times
  }
  prevAdjMode = adjMode;
}

int checkPalButton() {
  if (digitalRead(PAL_PIN) == 0) {
    //button is held
    palPinLoops++;
    if (palPinStatus == 1 && prevPalPinStatus == 1) {
      //we just started holding the button
      palPinStatus = 0;
      palPinLoops=0;
    }
    return (0);
  }  
  else if (digitalRead(PAL_PIN) == 1 && palPinStatus == 0 && prevPalPinStatus == 0) {
  //else if (digitalRead(PAL_PIN) == 1 && prevPalPinStatus == 0) {
    //button has just been released
    palPinLoops++;
    palPinStatus = 1;
    return (palPinLoops);
  }
  prevPalPinStatus = palPinStatus;
}

//function takes a color number (that may be bizarro) and returns an actual color number
byte actualColorNum(byte x) {
  if (x >= TOTALCOLORS) x = (TOTALCOLORS - 2) - (x - TOTALCOLORS);
  return (x);
}

void statusBlink(byte blinks, byte delayTime, byte redVal, byte greenVal, byte blueVal) {
  for ( byte x = 0; x <= blinks; x++) {
      statusLED.setPixelColor(0, redVal, greenVal, blueVal);
      statusLED.show();      
      delay(delayTime);
      statusLED.setPixelColor(0, 0, 0, 0); 
      statusLED.show();  
      delay(delayTime);
  }    
}

//Teeces PSI related settings...
#if (TEECESPSI==1)
  #define TEECES_D_PIN 12
  #define TEECES_C_PIN 10
  #define TEECES_L_PIN 6
  #define RPSIbright 15 //rear PSI
  #define FPSIbright 15 //front PSI
  #define PSIstuck 15 //odds (in 100) that a PSI will get partially stuck between 2 colors
  const int PSIpause[2] = { 3000, 6000 };
  const byte PSIdelay[2]PROGMEM = { 25, 35 };
  #include <LedControl.h>
  #undef round
  LedControl lcChain = LedControl(TEECES_D_PIN, TEECES_C_PIN, TEECES_L_PIN, 2); //use Teensy Reactor pins 2,4 & 5, 2 devices
  /*
     Each PSI has 7 states. For example on the front...
      0 = 0 columns Red, 6 columns Blue
      1 = 1 columns Red, 5 columns Blue (11)
      2 = 2 columns Red, 4 columns Blue (10)
      3 = 3 columns Red, 3 columns Blue  (9)
      4 = 4 columns Red, 2 columns Blue  (8)
      5 = 5 columns Red, 1 columns Blue  (7)
      6 = 6 columns Red, 0 columns Blue
  */
  void setPSIstate(bool frontRear, byte PSIstate) {
    //set PSI (0 or 1) to a state between 0 (full red) and 6 (full blue)
    // states 7-11 are moving backwards
    if (PSIstate > 6) PSIstate = 12 - PSIstate;
    for (byte col = 0; col < 6; col++) {
      if (col < PSIstate) {
        if (col % 2) lcChain.setColumn(frontRear, col, B10101010);
        else lcChain.setColumn(frontRear, col,      B01010101);
      }
      else {
        if (col % 2) lcChain.setColumn(frontRear, col, B01010101);
        else lcChain.setColumn(frontRear, col,      B10101010);
      }
    }
  }
  byte PSIstates[2] = { 0, 0 };
  unsigned long PSItimes[2] = { millis(), millis() };
  unsigned int PSIpauses[2] = { 0, 0 };
#endif

void loadSettings(byte deviceNum = 0) {
  //load stored settings for specified logic display(s) (0 for all, 1 for front, 3 for rear)
  if (deviceNum==0) mySettings = my_flash_store.read();
  else tempSettings = my_flash_store.read();
  if (deviceNum==1) {
    //just read front specific settings from stored values
    mySettings.frontDelay=tempSettings.frontDelay;
    mySettings.frontFade=tempSettings.frontFade;
    mySettings.frontBri=tempSettings.frontBri;
    mySettings.frontHue=tempSettings.frontHue;
    mySettings.frontPalNum=tempSettings.frontPalNum;
    mySettings.frontDesat=tempSettings.frontDesat;
  }
  else if (deviceNum==3) {
    //just read rear specific settings from stored values
    mySettings.rearDelay=tempSettings.rearDelay;
    mySettings.rearFade=tempSettings.rearFade;
    mySettings.rearBri=tempSettings.rearBri;
    mySettings.rearHue=tempSettings.rearHue;
    mySettings.rearPalNum=tempSettings.rearPalNum;
    mySettings.rearDesat=tempSettings.rearDesat;
  }
  if (deviceNum==0||deviceNum==1) calcColors(mySettings.frontPalNum, 0);
  if (deviceNum==0||deviceNum==3) calcColors(mySettings.rearPalNum, 1);  
}

void saveSettings() {
  my_flash_store.write(mySettings);
}

////////////////////////////////
// command line builder, makes a valid command line from the input
byte buildCommand(char ch, char* output_str) {
  static uint8_t pos=0;
  if (ch=='\r') {  // end character recognized
      output_str[pos]='\0';   // append the end of string character
      pos=0;        // reset buffer pointer
      //doingSerialStuff=0;
      return true;      // return and signal command ready      
  }
  else {  // regular character
      output_str[pos]=ch;   // append the  character to the command string
      if(pos<=CMD_MAX_LENGTH-1)pos++; // too many characters, discard them.
  }
  return false;
}

void checkJediSerial() {
  if (JEDI_SERIAL.available() > 0) {
    doingSerialStuff=1; 
    serialMillis = millis();        
    ch=JEDI_SERIAL.read();  // get input
    //JEDI_SERIAL.print(ch);  // echo back
    #if (DEBUG>0)
      //DEBUG_SERIAL.println(ch);
      //DEBUG_SERIAL.println(ch,HEX);
    #endif
    command_available=buildCommand(ch, cmdString);  // build command line
    if (command_available) {
      parseCommand(cmdString);  // interpret the command
      //JEDI_SERIAL.print(F("\n> "));  // prompt again
      //DEBUG_SERIAL.print(F("\n> ")); // prompt again
    } 
  }
}

void parseCommand(char* inputStr) {
        #if (DEBUG>0)
          DEBUG_SERIAL.print(F("parse "));
          DEBUG_SERIAL.println(inputStr);
        #endif
        byte hasArgument=false;
        int argument=0;
        byte deviceNum;
        byte pos=0;
        byte length=strlen(inputStr);
        if(length<2) goto beep;   // not enough characters

        // get the Device Number (aka address), one or two digits
        char addrStr[3];
        if(!isdigit(inputStr[pos])) goto beep;  // invalid, first char not a digit
        addrStr[pos]=inputStr[pos];
        pos++;                              // pos=1
        if(isdigit(inputStr[pos])) {        // add second digit address if it's there 
          addrStr[pos]=inputStr[pos];
          pos++;                            // pos=2
        }
        addrStr[pos]='\0';                  // add null terminator
        deviceNum= atoi(addrStr);        // extract the address

        // check for more
        if(!length>pos) goto beep;            // invalid, no command after address
       
        //check for a valid command letter. F (fade),J (delay),H (hue),J (bri) or P (parameter)
        if (inputStr[1]=='P') {
          // valid P options are 70 (Reset), 71 (Load) , 72 (Save), 73 (Palette)
          if (inputStr[2]=='7') {
            if (inputStr[3]=='3') {
              // ** command P73 , cycle palette(s)
              if (deviceNum==1||deviceNum==0) changePalNum(1);
              if (deviceNum==3||deviceNum==0) changePalNum(3);
            }
            else if (inputStr[3]=='0') {
              // ** command P70 , load factory settings
              factorySettings();
            }
            else if (inputStr[3]=='1') {
              // ** command P71 , load stored settings
              if (deviceNum==0)loadSettings();
              else if (deviceNum==1)loadSettings(1);
              else if (deviceNum==3)loadSettings(3);
            }
          }            
        }
        else if (inputStr[1]=='T') {
          if (inputStr[2]=='r') {
              // ** Tr, same as command P71 , load stored settings but also enables all logics
              if (deviceNum==0){
                loadSettings();
                onOff[1]=1;
                onOff[2]=1;
                onOff[3]=1;
              }
              else if (deviceNum==1){
                loadSettings(1);
                onOff[1]=1;
                onOff[2]=1;
              }
              else if (deviceNum==3){
                loadSettings(3);
                onOff[3]=1;
              }
          }
        }
        else if (inputStr[1]=='O') {
          // ** command O changes a device's on/off state
          if (inputStr[2]=='0') {
            if (deviceNum==0||deviceNum==1) {
              onOff[1]=0;
              for ( byte LEDnum = 0; LEDnum < 40; LEDnum++) {
                  frontLEDs.setPixelColor(LEDnum, 0 , 0 , 0);  //neoPixel
              }
            }
            if (deviceNum==0||inputStr[0]=='2') { 
              onOff[2]=0;
              for ( byte LEDnum = 40; LEDnum < 80; LEDnum++) {
                  frontLEDs.setPixelColor(LEDnum, 0 , 0 , 0);  //neoPixel
              }
            }
            if (deviceNum==0||deviceNum==3) {
              onOff[3]=0;
              for ( byte LEDnum = 0; LEDnum < RearLEDCount; LEDnum++) {
                  rearLEDs.setPixelColor(LEDnum, 0 , 0 , 0); //neoPixel
              }                
            }
          }
          else if (inputStr[2]=='1') {
            if (deviceNum==0||deviceNum==1) onOff[1]=1;
            if (deviceNum==0||inputStr[0]=='2') onOff[2]=1;
            if (deviceNum==0||deviceNum==3) onOff[3]=1;
          }
        }
        else {
          //F (fade),G (delay),H (hue),J (bri)
          //these other commands will have a value from 0-255 after the command letter
          //so let's get those numbers into a workable value
          char argument[3];
          argument[0]=inputStr[2];
          argument[1]=inputStr[3];
          argument[2]=inputStr[4];
          byte argumentValue = atoi(argument);
          #if (DEBUG>0)              
            /*DEBUG_SERIAL.println(inputStr[2]);
            DEBUG_SERIAL.println(inputStr[3]);
            DEBUG_SERIAL.println(inputStr[4]); */             
            DEBUG_SERIAL.println(argumentValue);
          #endif
          if (inputStr[1]=='F') {
            if (deviceNum==0) {
              mySettings.frontFade=argumentValue;
              mySettings.rearFade=argumentValue; 
            }
            else if (deviceNum==1) mySettings.frontFade=argumentValue;
            else if (deviceNum==3) mySettings.rearFade=argumentValue;             
          }
          else if (inputStr[1]=='G') {
            if (deviceNum==0) {
              mySettings.frontDelay=argumentValue;
              mySettings.rearDelay=argumentValue; 
            }
            else if (deviceNum==1) mySettings.frontDelay=argumentValue;
            else if (deviceNum==3) mySettings.rearDelay=argumentValue;             
          }   
          else if (inputStr[1]=='H') {
            if (deviceNum==0) {
              mySettings.frontHue=argumentValue;
              calcColors(mySettings.frontPalNum, 0);
              mySettings.rearHue=argumentValue; 
              calcColors(mySettings.rearPalNum, 1); 
            }
            else if (deviceNum==1) {
              mySettings.frontHue=argumentValue;
              calcColors(mySettings.frontPalNum, 0);
            }
            else if (deviceNum==3) {
              mySettings.rearHue=argumentValue; 
              calcColors(mySettings.rearPalNum, 1);            
            }
          } 
          else if (inputStr[1]=='K') {
            //adjust Desaturation setting
            if (deviceNum==1 || deviceNum==0) {
              mySettings.frontDesat=argumentValue;
              calcColors(mySettings.frontPalNum, 0);
            }
            if (deviceNum==3 || deviceNum==0) {
              mySettings.rearDesat=argumentValue; 
              calcColors(mySettings.rearPalNum, 1);            
            }
          }
          else if (inputStr[1]=='J') {
            if (deviceNum==0) {
              mySettings.frontBri=argumentValue;
              calcColors(mySettings.frontPalNum, 0);
              mySettings.rearBri=argumentValue; 
              calcColors(mySettings.rearPalNum, 1); 
            }
            else if (deviceNum==1) {
              mySettings.frontBri=argumentValue;
              calcColors(mySettings.frontPalNum, 0);
            }
            else if (deviceNum==3) {
              mySettings.rearBri=argumentValue; 
              calcColors(mySettings.rearPalNum, 1);            
            }
          } 
        }

        return;                               // normal exit
  
        beep:                                 // error exit
        //JEDI_SERIAL.write(0x7);               // beep the terminal, if connected
        return;
}

void changePalNum(byte logicAddress) {
    if (logicAddress == 1)   {
      mySettings.frontPalNum++;
      if (mySettings.frontPalNum == NUM_PALS) mySettings.frontPalNum = 0;
      //generate new front palette here!!!
      calcColors(mySettings.frontPalNum, 0);
      #if (DEBUG>0)
          DEBUG_SERIAL.print(F("pal"));
          DEBUG_SERIAL.println(mySettings.frontPalNum);
      #endif
    }
    else if (logicAddress == 3) {
      mySettings.rearPalNum++;
      if (mySettings.rearPalNum == NUM_PALS) mySettings.rearPalNum = 0;
      //generate new rear palette here!!!
      calcColors(mySettings.rearPalNum, 1);
      #if (DEBUG>0)
          DEBUG_SERIAL.print(F("pal"));
          DEBUG_SERIAL.println(mySettings.rearPalNum);
      #endif
    }
}

void factorySettings() {
  mySettings = { (mySettings.writes+1), MAX_BRIGHTNESS,
                   DFLT_FRONT_DELAY, DFLT_FRONT_FADE, DFLT_FRONT_BRI, DFLT_FRONT_HUE, DFLT_FRONT_PAL, DFLT_FRONT_DESAT,
                   DFLT_REAR_DELAY,  DFLT_REAR_FADE,  DFLT_REAR_BRI,  DFLT_REAR_HUE,  DFLT_REAR_PAL, DFLT_REAR_DESAT
                 };
  calcColors(mySettings.frontPalNum, 0);
  calcColors(mySettings.rearPalNum, 1);                     
}

void setup() {
#if (DEBUG>0)
  delay(2000);
  DEBUG_SERIAL.begin(BAUDRATE);
  DEBUG_SERIAL.println(F("yo"));
  rtc.begin();
  rtc.setTime(0, 0, 0);
  //rtc.setDate(1, 1, 2018);
#endif
JEDI_SERIAL.begin(BAUDRATE);

statusLED.begin();
statusLED.setPixelColor(0, 0, 2, 0); //green
statusLED.show();
frontLEDs.begin();
frontLEDs.show();
rearLEDs.begin();
rearLEDs.show();

  mySettings = my_flash_store.read();
  if (mySettings.writes == false) {
#if (DEBUG>0)
    DEBUG_SERIAL.println(F("no settings"));
#endif
    mySettings = { 1, MAX_BRIGHTNESS,
                   DFLT_FRONT_DELAY, DFLT_FRONT_FADE, DFLT_FRONT_BRI, DFLT_FRONT_HUE, DFLT_FRONT_PAL, DFLT_FRONT_DESAT,
                   DFLT_REAR_DELAY,  DFLT_REAR_FADE,  DFLT_REAR_BRI,  DFLT_REAR_HUE,  DFLT_REAR_PAL, DFLT_REAR_DESAT
                 };
    my_flash_store.write(mySettings);
    mySettings = my_flash_store.read();
    if (mySettings.writes >= 1) {
#if (DEBUG>0)
      DEBUG_SERIAL.println(F("dflts wrote"));
#endif
    }
  }
  else {
#if (DEBUG>0)
    DEBUG_SERIAL.println(F("settings ok"));
    DEBUG_SERIAL.print(mySettings.writes);
    DEBUG_SERIAL.println(F(" writes"));
#endif
  }

  //generate all the colors!
  calcColors(mySettings.frontPalNum, 0);
  calcColors(mySettings.rearPalNum, 1);

  //assign each logic LED a random color and pause value
  for ( byte LEDnum = 0; LEDnum < FrontLEDCount; LEDnum++) {
    frontLEDstatus[LEDnum].colorNum = random(TOTALCOLORSWBIZ);
    frontLEDstatus[LEDnum].colorPause = random(mySettings.frontDelay);
  }
  for ( byte LEDnum = 0; LEDnum < RearLEDCount; LEDnum++) {
    rearLEDstatus[LEDnum].colorNum = random(TOTALCOLORSWBIZ);
    rearLEDstatus[LEDnum].colorPause = random(mySettings.rearDelay);
  }

  pinMode(FADJ_PIN, INPUT_PULLUP); //use internal pullup resistors of Teensy
  pinMode(RADJ_PIN, INPUT_PULLUP);
  if (digitalRead(RADJ_PIN) == 0 or digitalRead(FADJ_PIN) == 0) startAdjMode = 1; //adj switch isn't centered!
  pinMode(PAL_PIN, INPUT_PULLUP);

    #if (TEECESPSI==1)
      lcChain.shutdown(0, false); //take the device out of shutdown (power save) mode
      lcChain.clearDisplay(0);
      lcChain.shutdown(1, false); //take the device out of shutdown (power save) mode
      lcChain.clearDisplay(1);
      lcChain.setIntensity(0, FPSIbright); //Front PSI
      lcChain.setIntensity(1, RPSIbright); //Rear PSI
    #endif

  
  //delay(2000);
}


void loop() {
  //currentMillis = millis();
  #if (DEBUG>0)
    rtcSeconds = rtc.getSeconds();
  #endif

  #if (ENABLE_JEDI_SERIAL==1)
  checkJediSerial();
  #endif

  loopcount++;
  if (loopcount>flipFlopLoops) {
    if (flipFlop==0) {
      prevFlipFlop=0;
      flipFlop=1;
    }
    else {
      prevFlipFlop=1;
      flipFlop=0;
    }
    loopcount=0;
  }
  
  if (frontRear==0) frontRear=1;
  else frontRear=0;

  checkAdjSwitch(); //checks the switch and sets adjMode and flipFlopMillis
  setStatusLED(); //blinks the status LED back and forth
  if (adjMode != 0) {
    adjLoops++;
    compareTrimpots(adjMode);
  }

  int palBut = checkPalButton();
  if (palBut >= 400) {
    #if (DEBUG>0)
      DEBUG_SERIAL.println(F("2 sec rule"));
    #endif
    factorySettings();
    calcColors(mySettings.frontPalNum, 0);
    calcColors(mySettings.rearPalNum, 1);
    my_flash_store.write(mySettings);
    statusBlink(6, 100, 1, 0, 2); //blink purple 6 times fast
  }
  else if (adjMode != 0 && palBut >= 3) {
    //change up the color palette used for this logic display
    changePalNum(adjMode);
  }

  if (doingSerialStuff==1 && (millis()-serialMillis>serialMillisWait) ) doingSerialStuff=0; //enough time has passed since we saw some serial data, send data to the LEDs again
  if (doingSerialStuff==0) {

      //UPDATE FIRST FRONT LOGIC...
      if (onOff[1]==1) {
        for ( byte LEDnum = 0; LEDnum < 40; LEDnum++) {
          if (frontLEDstatus[LEDnum].colorPause != 0)  frontLEDstatus[LEDnum].colorPause--;
          else {
            frontLEDstatus[LEDnum].colorNum++;
            if (frontLEDstatus[LEDnum].colorNum >= TOTALCOLORSWBIZ) frontLEDstatus[LEDnum].colorNum = 0; //bring it back to color zero
            if (frontLEDstatus[LEDnum].colorNum % (TWEENS + 1) == 0) frontLEDstatus[LEDnum].colorPause = random(mySettings.frontDelay); //color is a key, assign random pause
            else frontLEDstatus[LEDnum].colorPause = mySettings.frontFade; //color is a tween, assign a quick pause
            //now set the actual color of this LED, you big dummy
            frontLEDs.setPixelColor(LEDnum, allColors[0][actualColorNum(frontLEDstatus[LEDnum].colorNum)][0] , allColors[0][actualColorNum(frontLEDstatus[LEDnum].colorNum)][1] , allColors[0][actualColorNum(frontLEDstatus[LEDnum].colorNum)][2]); 
          }
        }
      }
      //UPDATE SECOND FRONT LOGIC...
      if (onOff[2]==1) {
        for ( byte LEDnum = 40; LEDnum < 80; LEDnum++) {
          if (frontLEDstatus[LEDnum].colorPause != 0)  frontLEDstatus[LEDnum].colorPause--;
          else {
            frontLEDstatus[LEDnum].colorNum++;
            if (frontLEDstatus[LEDnum].colorNum >= TOTALCOLORSWBIZ) frontLEDstatus[LEDnum].colorNum = 0; //bring it back to color zero
            if (frontLEDstatus[LEDnum].colorNum % (TWEENS + 1) == 0) frontLEDstatus[LEDnum].colorPause = random(mySettings.frontDelay); //color is a key, assign random pause
            else frontLEDstatus[LEDnum].colorPause = mySettings.frontFade; //color is a tween, assign a quick pause
            //now set the actual color of this LED, you big dummy
            frontLEDs.setPixelColor(LEDnum, allColors[0][actualColorNum(frontLEDstatus[LEDnum].colorNum)][0] , allColors[0][actualColorNum(frontLEDstatus[LEDnum].colorNum)][1] , allColors[0][actualColorNum(frontLEDstatus[LEDnum].colorNum)][2]); 
          }
        }
      }
      //UPDATE REAR LOGIC...
      if (onOff[3]==1) {
        for ( byte LEDnum = 0; LEDnum < RearLEDCount; LEDnum++) {
          if (rearLEDstatus[LEDnum].colorPause != 0)  rearLEDstatus[LEDnum].colorPause--;
          else {
            rearLEDstatus[LEDnum].colorNum++;
            if (rearLEDstatus[LEDnum].colorNum >= TOTALCOLORSWBIZ) rearLEDstatus[LEDnum].colorNum = 0; //bring it back to color zero
            if (rearLEDstatus[LEDnum].colorNum % (TWEENS + 1) == 0) rearLEDstatus[LEDnum].colorPause = random(mySettings.rearDelay); //color is a key, assign random pause
            else rearLEDstatus[LEDnum].colorPause = mySettings.rearFade; //color is a tween, assign a quick pause
            //now set the actual color of this LED, you big dummy
            rearLEDs.setPixelColor(LEDnum, allColors[1][actualColorNum(rearLEDstatus[LEDnum].colorNum)][0] , allColors[1][actualColorNum(rearLEDstatus[LEDnum].colorNum)][1] , allColors[1][actualColorNum(rearLEDstatus[LEDnum].colorNum)][2]); 
          }
        }
      } 

        statusLED.show();
        //updating every LED on every loop can cause interrupt issues, so we alternate between front and rear on each loop...
        if (frontRear == 0) frontLEDs.show();
        else rearLEDs.show();
    
  }
  
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////// TEECES PSI STUFF
    #if (TEECESPSI==1)
      for (byte PSInum = 0; PSInum < 2; PSInum++) {
        if (millis() - PSItimes[PSInum] >= PSIpauses[PSInum]) {
          //time's up, do something...
          PSIstates[PSInum]++;
          if (PSIstates[PSInum] == 12) PSIstates[PSInum] = 0;
          if (PSIstates[PSInum] != 0 && PSIstates[PSInum] != 6) {
            //we're swiping...
            PSIpauses[PSInum] = pgm_read_byte(&PSIdelay[PSInum]);
          }
          else {
            //we're pausing
            PSIpauses[PSInum] = random(PSIpause[PSInum]);
            //decide if we're going to get 'stuck'
            if (random(100) <= PSIstuck) {
              if (PSIstates[PSInum] == 0) PSIstates[PSInum] = random(1, 3);
              else PSIstates[PSInum] = random(3, 5);
            }
          }
          setPSIstate(PSInum, PSIstates[PSInum]);
          PSItimes[PSInum] = millis();
        }
      }
    #endif

#if (DEBUG>1)  
  if (rtcSeconds != prevRtcSeconds) {
    //a second has passed. how many loops did we do?
    DEBUG_SERIAL.println( loopcount );
    //DEBUG_SERIAL.println(analogRead(fadePin));
    loopcount = 0;
  }
  //if (rtcSeconds!=prevRtcSeconds) DEBUG_SERIAL.println(rtcSeconds);
  prevRtcSeconds = rtcSeconds;
#endif

  
  
}
