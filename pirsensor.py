from gpiomanager import GPIO
from sensors import ISensor
from piguardtyping import Status


class PIRSensor(ISensor):

    def __init__(self, gpio_pin: int):
        GPIO.setup(gpio_pin, GPIO.IN)
        self._pin = gpio_pin

    def update_status(self, status: Status):
        if GPIO.input(self._pin) == 1:
            status["motion"] = True
        else:
            status["motion"] = False
