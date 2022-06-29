import RPi.GPIO as GPIO
import requests

baseurl = 'http://localhost:5000/'

outputs = {
	"16": "scripts/r2kt/0",
	"18": "scripts/leia/0",
	"11": "scripts/failure/0",
	"13": "scripts/march/0",
	"22": "sound/random" }

GPIO.setmode(GPIO.BOARD)

def cb(button):
        print(f"Button {button} pressed. URL is {outputs[str(button)]}")
	
        url = baseurl + outputs[str(button)]
        try:
                r = requests.get(url)
        except:
                if __debug__:
                        print("Fail....")

for pin in outputs:
	print(f"Setting up pin {pin}")
	GPIO.setup(int(pin), GPIO.IN, pull_up_down=GPIO.PUD_UP)	
	GPIO.add_event_detect(int(pin), edge=GPIO.RISING, callback=cb, bouncetime=500)

GPIO.setmode(GPIO.BOARD)

while True:
    x = 0;
