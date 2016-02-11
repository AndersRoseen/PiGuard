import RPi.GPIO as GPIO
from sensors import ISensor

GPIO.setmode(GPIO.BCM)


class PIRSensor(ISensor):

    def __init__(self, gpio_pin):
        GPIO.setup(gpio_pin,GPIO.IN)
        self._pin = gpio_pin

    def update_status(self, status):
        if GPIO.input(self._pin) == 1:
            status["motion"] = True
        else:
            status["motion"] = False
