""" Thread for each servo """
import threading
from queue import Queue, Empty
import time
import Adafruit_PCA9685
from future import standard_library
standard_library.install_aliases()


q = Queue

ADDRESS = 0x40
MAX = 0
MIN = 0
CURRENT = 0
HOME = 0
CHANNEL = 0


class ServoThread(threading.Thread):
    def __init__(self, Address, Max, Min, Home, Channel, q):
        if __debug__:
            print(f"Initialising thread - {Address}/{Max}/{Min}/{Home}/{Channel}")
        self.q = q
        self.Address = Address
        self.Max = Max
        self.Min = Min
        self.Home = Home
        self.current_position = Home
        self.original_position = Home
        self.Channel = Channel
        self.destination_position = Home
        self.destination_start = 0
        self.destination_time = 0
        self.processing = False
        threading.Thread.__init__(self)
        try:
            if __debug__:
                print(f"Address is of type: {type(self.Address)}")
                print(f"Address as hex: {self.Address}")
                print(f"Address as dec: {int(self.Address, 16)}")
            self.i2c = Adafruit_PCA9685.PCA9685(address=int(self.Address, 16), busnum=int(1))
            self.i2c.set_pwm_freq(60)
        except Exception as e:
            print(f"Failed to initialise servo at {self.Address}/{self.Channel}. Exception: {e}")
            raise Exception("Failed to initialise server")
        return

    def sendCommand(self):
        current_time = int(round(time.time() * 1000))
        if self.processing:
            if __debug__:
                print("Processing and sending command")
            if self.destination_time <= current_time:
                position = self.destination_position
            else:
                if __debug__:
                    print("Current time: %s | destination_start: %s | destination_time: %s | destination_position: %s | original_position: %s" %  # noqa: E501
                          (current_time, self.destination_start, self.destination_time, self.destination_position, self.original_position))  # noqa: E501
                    print(f"(current_time - self.destination_start): {(current_time - self.destination_start)} ")
                    print(f"(self.destination_time - self.destination_start): {(self.destination_time - self.destination_start)}")
                progress = float(current_time - self.destination_start) / float(self.destination_time - self.destination_start)
                if __debug__:
                    print(f"Currently {progress} way through this move")
                if self.original_position > self.destination_position:
                    if __debug__:
                        print("Closing slowly...")
                    position = int(round(self.original_position -
                                         ((self.original_position - self.destination_position) * progress)))
                else:
                    if __debug__:
                        print("Opening slowly....")
                    position = int(round(((self.destination_position - self.original_position) * progress) +
                                         self.original_position))
                if __debug__:
                    print(f"Current position request: {position} ")
            try:
                self.i2c.set_pwm(self.Channel, 0, position)
                self.current_position = position
            except Exception:
                print(f"Failed to send command {self.Address}/{self.Channel} -> {position}")
#            if self.destination_position == self.current_position:
#               if __debug__:
#                   print("Reached final position")
#               self.processing = False
        if (self.destination_time + 200 < current_time) and self.processing is True:
            # Reset the servo and set processing to False
            if __debug__:
                print("Resetting servo")
            try:
                self.i2c.set_pwm(self.Channel, 4096, 0)
                self.processing = False
            except Exception:
                if __debug__:
                    print(f"Failed to send command (reset) {self.Address}/{self.Channel}")
        return

    def run(self):
        if __debug__:
            print("Starting Thread")
        while True:
            try:
                command = self.q.get(False)
                position = command[0]
                duration = command[1]
                if position > 1 or position < 0:
                    print(f"Invalid position ({position})")
                else:
                    self.destination_position = int(((self.Max - self.Min) * position) + self.Min)
                    self.processing = True
                self.destination_start = int(round(time.time() * 1000))
                self.destination_time = self.destination_start + (duration * 1000)
                self.original_position = self.current_position
                if __debug__:
                    print(f"Duration:    {duration}")
                    print(f"Destination: {self.destination_position}")
                    print(f"Original:    {self.original_position}")
                    print(f"Start time:  {self.destination_start}")
                    print(f"End time:    {self.destination_time}")
                self.sendCommand()                            # Main Command Loop
            except Empty:
                if self.processing is not False:
                    self.sendCommand()
            time.sleep(0.005)

        return
