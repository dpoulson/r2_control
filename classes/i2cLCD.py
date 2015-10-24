#!/usr/bin/python
# 
#    Copyright Paul Knox-Kennedy, 2012
#    This file is part of RpiLcdBackpack.

#    RpiLcdBackpack is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    RpiLcdBackpack is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.#

import smbus,time
from subprocess import * 
from time import sleep, strftime
from datetime import datetime
from Adafruit_I2C import Adafruit_I2C



class i2cLCD:
  # commands
  __CLEARDISPLAY=0x01
  __RETURNHOME=0x02
  __ENTRYMODESET=0x04
  __DISPLAYCONTROL=0x08
  __CURSORSHIFT=0x10
  __FUNCTIONSET=0x20
  __SETCGRAMADDR=0x40
  __SETDDRAMADDR=0x80

  # flags for display entry mode
  __ENTRYRIGHT=0x00
  __ENTRYLEFT=0x02
  __ENTRYSHIFTINCREMENT=0x01
  __ENTRYSHIFTDECREMENT=0x00

  # flags for display on/off control
  __DISPLAYON=0x04
  __DISPLAYOFF=0x00
  __CURSORON=0x02
  __CURSOROFF=0x00
  __BLINKON=0x01
  __BLINKOFF=0x00

  # flags for display/cursor shift
  __DISPLAYMOVE=0x08
  __CURSORMOVE=0x00
  __MOVERIGHT=0x04
  __MOVELEFT=0x00

  # flags for function set
  __8BITMODE=0x10
  __4BITMODE=0x00
  __2LINE=0x08
  __1LINE=0x00
  __5x10DOTS=0x04
  __5x8DOTS=0x00


  _rs=0x02
  _e=0x4
  _dataMask=0x78
  _dataShift=3
  _light=0x80



  def writeFourBits(self,value):
    self.__data &= ~self._dataMask
    self.__data |= value << self._dataShift
    self.__data &= ~self._e 
    self.__bus.write_byte_data(0x20,0x09,self.__data)
    time.sleep(0.000001)
    self.__data |= self._e 
    self.__bus.write_byte_data(0x20,0x09,self.__data)
    time.sleep(0.000001)
    self.__data &= ~self._e 
    self.__bus.write_byte_data(0x20,0x09,self.__data)
    time.sleep(0.000101)

  def writeCommand(self,value):
    self.__data &= ~self._rs
    self.writeFourBits(value>>4)
    self.writeFourBits(value&0xf)

  def writeData(self,value):
    self.__data |= self._rs
    self.writeFourBits(value>>4)
    self.writeFourBits(value&0xf)

  def __init__(self, address=0x20, debug=False):
    self.i2c = Adafruit_I2C(address, 1)
    self.address = address
    self.debug = debug
    self.__displayfunction = self.__8BITMODE | self.__2LINE | self.__5x8DOTS
    self.__displaycontrol = self.__DISPLAYCONTROL | self.__DISPLAYON | self.__CURSORON | self.__BLINKON
    self.__data = 0
    if __debug__:
      print "Clearing Screen"
    #self.i2c.write8(self.__CLEARDISPLAY, 0x00)
    self.clear()


  def backlight(self,on):
    if on:
      self.__data |= 0x80
    else:
      self.__data &= 0x7f
    self.__bus.write_byte_data(0x20,0x09,self.__data)


  def clear(self):
    self.writeCommand(self.__CLEARDISPLAY)
    time.sleep(0.002)


  def blink(self, on):
    if on:
      self.__displaycontrol |= self.__BLINKON
    else:
      self.__displaycontrol &= ~self.__BLINKON
    self.writeCommand(self.__displaycontrol)

  def noCursor(self):
    self.writeCommand(self.__displaycontrol)

  def cursor(self, on):
    if on:
      self.__displaycontrol |= self.__CURSORON
    else:
      self.__displaycontrol &= ~self.__CURSORON
    self.writeCommand(self.__displaycontrol)

  def message(self, text):
    for char in text:
      if char == '\n':
        self.writeCommand(0xC0)
      else:
        self.writeData(ord(char))


