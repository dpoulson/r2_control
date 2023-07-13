#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
derivated from
    Sokrates80/sbus_driver_micropython git hub
    https://os.mbed.com/users/Digixx/code/SBUS-Library_16channel/file/83e415034198/FutabaSBUS/FutabaSBUS.cpp/
    https://os.mbed.com/users/Digixx/notebook/futaba-s-bus-controlled-by-mbed/
    https://www.ordinoscope.net/index.php/Electronique/Protocoles/SBUS
"""

# dsimonet

import array
import serial
import codecs
import time


class SBUSReceiver():
    def __init__(self, _uart_port='/dev/ttyS0'):

        # init serial of raspberry pi
        self.ser = serial.Serial(
            port=_uart_port,
            baudrate=100000,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.EIGHTBITS,
            timeout=0,
        )

        # constants
        self.START_BYTE = b'\x0f'
        self.END_BYTE = b'\x00'
        self.SBUS_FRAME_LEN = 25
        self.SBUS_NUM_CHAN = 18
        self.OUT_OF_SYNC_THD = 10
        self.SBUS_NUM_CHANNELS = 18
        self.SBUS_SIGNAL_OK = 0
        self.SBUS_SIGNAL_LOST = 1
        self.SBUS_SIGNAL_FAILSAFE = 2

        # Stack Variables initialization
        self.isReady = True
        self.lastFrameTime = 0
        self.sbusBuff = bytearray(1)  # single byte used for sync
        self.sbusFrame = bytearray(25)  # single SBUS Frame
        self.sbusChannels = array.array('H', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])  # RC Channels
        self.failSafeStatus = self.SBUS_SIGNAL_FAILSAFE

    def get_rx_channels(self):
        """
        Used to retrieve the last SBUS channels values reading
        :return:  an array of 18 unsigned short elements containing 16 standard channel values + 2 digitals (ch 17 and 18)
        """

        return self.sbusChannels

    def get_rx_channel(self, num_ch):
        """
        Used to retrieve the last SBUS channel value reading for a specific channel
        :param: num_ch: the channel which to retrieve the value for
        :return:  a short value containing
        """

        return self.sbusChannels[num_ch]

    def get_failsafe_status(self):
        """
        Used to retrieve the last FAILSAFE status
        :return:  a short value containing
        """

        return self.failSafeStatus

    def decode_frame(self):

        # each values are in beetween two or tree differentes bytes . so look the mess to catch it !
        # Thanks futaba to make this.

        def toInt(_from):
            return int(codecs.encode(_from, 'hex'), 16)

        self.sbusChannels[0] = ((toInt(self.sbusFrame[1]) | toInt(self.sbusFrame[2]) << 8) & 0x07FF)
        self.sbusChannels[1] = ((toInt(self.sbusFrame[2]) >> 3 | toInt(self.sbusFrame[3]) << 5) & 0x07FF)
        self.sbusChannels[2] = ((toInt(self.sbusFrame[3]) >> 6 |
                                toInt(self.sbusFrame[4]) << 2 | toInt(self.sbusFrame[5]) << 10) & 0x07FF)
        self.sbusChannels[3] = ((toInt(self.sbusFrame[5]) >> 1 | toInt(self.sbusFrame[6]) << 7) & 0x07FF)
        self.sbusChannels[4] = ((toInt(self.sbusFrame[6]) >> 4 | toInt(self.sbusFrame[7]) << 4) & 0x07FF)
        self.sbusChannels[5] = ((toInt(self.sbusFrame[7]) >> 7 | toInt(self.sbusFrame[8]) << 1 |
                                toInt(self.sbusFrame[9]) << 9) & 0x07FF)
        self.sbusChannels[6] = ((toInt(self.sbusFrame[9]) >> 2 | toInt(self.sbusFrame[10]) << 6) & 0x07FF)
        self.sbusChannels[7] = ((toInt(self.sbusFrame[10]) >> 5 | toInt(self.sbusFrame[11]) << 3) & 0x07FF)
        self.sbusChannels[8] = ((toInt(self.sbusFrame[12]) | toInt(self.sbusFrame[13]) << 8) & 0x07FF)
        self.sbusChannels[9] = ((toInt(self.sbusFrame[13]) >> 3 | toInt(self.sbusFrame[14]) << 5) & 0x07FF)
        self.sbusChannels[10] = ((toInt(self.sbusFrame[14]) >> 6 | toInt(self.sbusFrame[15]) << 2 |
                                 toInt(self.sbusFrame[16]) << 10) & 0x07FF)
        self.sbusChannels[11] = ((toInt(self.sbusFrame[16]) >> 1 | toInt(self.sbusFrame[17]) << 7) & 0x07FF)
        self.sbusChannels[12] = ((toInt(self.sbusFrame[17]) >> 4 | toInt(self.sbusFrame[18]) << 4) & 0x07FF)
        self.sbusChannels[13] = ((toInt(self.sbusFrame[18]) >> 7 | toInt(self.sbusFrame[19]) << 1 |
                                 toInt(self.sbusFrame[20]) << 9) & 0x07FF)
        self.sbusChannels[14] = ((toInt(self.sbusFrame[20]) >> 2 | toInt(self.sbusFrame[21]) << 6) & 0x07FF)
        self.sbusChannels[15] = ((toInt(self.sbusFrame[21]) >> 5 | toInt(self.sbusFrame[22]) << 3) & 0x07FF)

        # to be tested, No 17 & 18 channel on taranis X8R
        if toInt(self.sbusFrame[23]) & 0x0001:
            self.sbusChannels[16] = 2047
        else:
            self.sbusChannels[16] = 0
        # to be tested, No 17 & 18 channel on taranis X8R
        if (toInt(self.sbusFrame[23]) >> 1) & 0x0001:
            self.sbusChannels[17] = 2047
        else:
            self.sbusChannels[17] = 0

        # Failsafe
        self.failSafeStatus = self.SBUS_SIGNAL_OK
        if toInt(self.sbusFrame[self.SBUS_FRAME_LEN - 2]) & (1 << 2):
            self.failSafeStatus = self.SBUS_SIGNAL_LOST
        if toInt(self.sbusFrame[self.SBUS_FRAME_LEN - 2]) & (1 << 3):
            self.failSafeStatus = self.SBUS_SIGNAL_FAILSAFE

    def update(self):
        """
        we need a least 2 frame size to be sure to find one full frame
        so we take all the fuffer (and empty it) and read it by the end to
        catch the last news
        First find ENDBYTE and looking FRAMELEN backward to see if it's STARTBYTE
        """

        # does we have enougth data in the buffer and no thread is currently trying in background?
        if self.ser.inWaiting() >= self.SBUS_FRAME_LEN*2 and self.isReady:
            self.isReady = False
            # so taking all of them
            tempFrame = self.ser.read(self.ser.inWaiting())
            # for each char of the buffer frame we looking for the end byte
            for end in range(0, self.SBUS_FRAME_LEN):
                # looking for end byte, remember we working backwards
                if tempFrame[len(tempFrame)-1-end] == self.END_BYTE:
                    # looking for start from last hit point minus FRAMELEN

                    if tempFrame[len(tempFrame)-end-self.SBUS_FRAME_LEN] == self.START_BYTE:
                        # if it is the right char, frame look good :')
                        # remember data arrive in 8E2 packet so it was already parity verified

                        # so the frame have to be remap only if it different (cpu time is precious)
                        lastUpdate = tempFrame[len(tempFrame)-end-self.SBUS_FRAME_LEN:len(tempFrame)-1-end]
                        if not self.sbusFrame == lastUpdate:
                            self.sbusFrame = lastUpdate
                            self.decode_frame()

                        self.lastFrameTime = time.time()  # keep trace of the last update
                        self.isReady = True
                        break


# excuted if this doc is not imported
# for testing purpose only
if __name__ == '__main__':

    sbus = SBUSReceiver('/dev/ttyS0')

    while True:
        time.sleep(0.005)

        # Call sbus.get_new_data() every about 7 to 10 ms.
        # to be sure to not calling it to much verify your serial.inWaiting() size of your SBUSReceiver instance.
        # if beetween call your serial is growing to much (> 50) you can call it more often.
        # if it raise you < 50 multiples times in row, you calling it too soon.
        sbus.update()

        # anywere in your code you can call sbus.get_rx_channels() to get all data or
        # sbus.get_rx_channels()[n] to get value of n channel
        # or get_rx_channel(self, num_ch) to get channel you whant.
        print(sbus.get_failsafe_status(), sbus.get_rx_channels(),
              str(sbus.ser.inWaiting()).zfill(4), (time.time()-sbus.lastFrameTime))
