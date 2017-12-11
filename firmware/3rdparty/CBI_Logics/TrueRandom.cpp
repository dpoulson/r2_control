/**
 * TrueRandom - A true random number generator for Arduino.
 *
 * Copyright (c) 2010 Peter Knight, Tinker.it! All rights reserved.
 */

#include <avr/io.h>
#include "TrueRandom.h"

int TrueRandomClass::randomBitRaw(void) {
  uint8_t copyAdmux, copyAdcsra, copyAdcsrb, copyPortc, copyDdrc;
  uint16_t i;
  uint8_t bit;
  volatile uint8_t dummy;
  
  // Store all the registers we'll be playing with
  copyAdmux = ADMUX;
  copyAdcsra = ADCSRA;
  copyAdcsrb = ADCSRB;
  copyPortc = PORTC;
  copyDdrc = DDRC;
  
  // Perform a conversion on Analog0, using the Vcc reference
  ADMUX = _BV(REFS0);
  
#if F_CPU > 16000000
  // ADC is enabled, divide by 32 prescaler
  ADCSRA = _BV(ADEN) | _BV(ADPS2) | _BV(ADPS0);
#elif F_CPU > 8000000
  // ADC is enabled, divide by 16 prescaler
  ADCSRA = _BV(ADEN) | _BV(ADPS2);
#else
  // ADC is enabled, divide by 8 prescaler
  ADCSRA = _BV(ADEN) | _BV(ADPS1) | _BV(ADPS0);
#endif

  // Autotriggering disabled
  ADCSRB = 0;

  // Pull Analog0 to ground
  PORTC &=~_BV(0);
  DDRC |= _BV(0);
  // Release Analog0, apply internal pullup
  DDRC &= ~_BV(0);
  PORTC |= _BV(1);
  // Immediately start a sample conversion on Analog0
  ADCSRA |= _BV(ADSC);
  // Wait for conversion to complete
  while (ADCSRA & _BV(ADSC)) PORTC ^= _BV(0);
  // Xor least significant bits together
  bit = ADCL;
  // We're ignoring the high bits, but we have to read them before the next conversion
  dummy = ADCH;

  // Restore register states
  ADMUX = copyAdmux;
  ADCSRA = copyAdcsra;
  ADCSRB = copyAdcsrb;
  PORTC = copyPortc;
  DDRC = copyDdrc;

  return bit & 1;
}

int TrueRandomClass::randomBitRaw2(void) {
  // Software whiten bits using Von Neumann algorithm
  //
  // von Neumann, John (1951). "Various techniques used in connection
  // with random digits". National Bureau of Standards Applied Math Series
  // 12:36.
  //
  for(;;) {
    int a = randomBitRaw() | (randomBitRaw()<<1);
    if (a==1) return 0; // 1 to 0 transition: log a zero bit
    if (a==2) return 1; // 0 to 1 transition: log a one bit
    // For other cases, try again.
  }
}

int TrueRandomClass::randomBit(void) {
  // Software whiten bits using Von Neumann algorithm
  //
  // von Neumann, John (1951). "Various techniques used in connection
  // with random digits". National Bureau of Standards Applied Math Series
  // 12:36.
  //
  for(;;) {
    int a = randomBitRaw2() | (randomBitRaw2()<<1);
    if (a==1) return 0; // 1 to 0 transition: log a zero bit
    if (a==2) return 1; // 0 to 1 transition: log a one bit
    // For other cases, try again.
  }
}

char TrueRandomClass::randomByte(void) {
  char result;
  uint8_t i;
  result = 0;
  for (i=8; i--;) result += result + randomBit();
  return result;
}

int TrueRandomClass::rand() {
  int result;
  uint8_t i;
  result = 0;
  for (i=15; i--;) result += result + randomBit();
  return result;
}

long TrueRandomClass::random() {
  long result;
  uint8_t i;
  result = 0;
  for (i=31; i--;) result += result + randomBit();
  return result;
}

long TrueRandomClass::random(long howBig) {
  long randomValue;
  long maxRandomValue;
  long topBit;
  long bitPosition;
  
  if (!howBig) return 0;
  randomValue = 0;
  if (howBig & (howBig-1)) {
    // Range is not a power of 2 - use slow method
    topBit = howBig-1;
    topBit |= topBit>>1;
    topBit |= topBit>>2;
    topBit |= topBit>>4;
    topBit |= topBit>>8;
    topBit |= topBit>>16;
    topBit = (topBit+1) >> 1;

    bitPosition = topBit;
    do {
      // Generate the next bit of the result
      if (randomBit()) randomValue |= bitPosition;

      // Check if bit 
      if (randomValue >= howBig) {
        // Number is over the top limit - start again.
        randomValue = 0;
        bitPosition = topBit;
      } else {
        // Repeat for next bit
        bitPosition >>= 1;
      }
    } while (bitPosition);
  } else {
    // Special case, howBig is a power of 2
    bitPosition = howBig >> 1;
    while (bitPosition) {
      if (randomBit()) randomValue |= bitPosition;
      bitPosition >>= 1;
    }
  }
  return randomValue;
}

long TrueRandomClass::random(long howSmall, long howBig) {
  if (howSmall >= howBig) return howSmall;
  long diff = howBig - howSmall;
  return TrueRandomClass::random(diff) + howSmall;
}

void TrueRandomClass::memfill(char* location, int size) {
  for (;size--;) *location++ = randomByte();
}

void TrueRandomClass::mac(uint8_t* macLocation) {
  memfill((char*)macLocation,6);
}

void TrueRandomClass::uuid(uint8_t* uuidLocation) {
  // Generate a Version 4 UUID according to RFC4122
  memfill((char*)uuidLocation,16);
  // Although the UUID contains 128 bits, only 122 of those are random.
  // The other 6 bits are fixed, to indicate a version number.
  uuidLocation[6] = 0x40 | (0x0F & uuidLocation[6]); 
  uuidLocation[8] = 0x80 | (0x3F & uuidLocation[8]);
}

TrueRandomClass TrueRandom;
