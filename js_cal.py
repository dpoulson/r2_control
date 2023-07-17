""" Script to help calibrate a servo """
import sys
import Adafruit_PCA9685


channel = sys.argv[2]
bus = int(sys.argv[1], 16)
FREQ = 60
print(f"Channel {channel} : Frequency {FREQ}")


def drive_servo(channel, pulse):
    """ Set a servo """
    period = 1/float(FREQ)
    bit_duration = period/4096
    pulse_duration = bit_duration*pulse*1000000
    if __debug__:
        print("Channel %s : pulse %5.5f : Duration: %s" % (channel, pulse, pulse_duration))
    try:
        i2c.set_pwm(channel, 0, int(pulse))
    except Exception:
        print("Failed to send command")


i2c = Adafruit_PCA9685.PCA9685(address=bus, busnum=1)
i2c.set_pwm_freq(FREQ)


while True:
    global pulse
    pulse = input("Enter value > ")
    drive_servo(int(channel), float(pulse))
