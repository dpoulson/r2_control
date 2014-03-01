#!/usr/bin/python

import time
import math
from Adafruit_I2C import Adafruit_I2C

# ============================================================================
# Adafruit PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class TeeCeeI2C :
  i2c = None

  # Registers/etc.
  __SUBADR1            = 0x02
  __SUBADR2            = 0x03
  __SUBADR3            = 0x04
  __MODE1              = 0x00
  __PRESCALE           = 0xFE
  __LED0_ON_L          = 0x06
  __LED0_ON_H          = 0x07
  __LED0_OFF_L         = 0x08
  __LED0_OFF_H         = 0x09
  __ALLLED_ON_L        = 0xFA
  __ALLLED_ON_H        = 0xFB
  __ALLLED_OFF_L       = 0xFC
  __ALLLED_OFF_H       = 0xFD

  def __init__(self, address=0x04, debug=1):
    self.i2c = Adafruit_I2C(0x04, 1)
    self.address = address
    self.debug = debug

  def TriggerEffect(self, effect):
    "Triggers effect"
    self.i2c.write4(effect)




