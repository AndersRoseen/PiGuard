import Adafruit_DHT
from sensors import ISensor
from piguardtyping import Status


class DHTSensor(ISensor):

    def __init__(self, active_sensors: [str], model: str, gpio_pin: int):
        self.sensors = active_sensors
        self._pin = gpio_pin
        if model == "AM2302":
            self._sensor_model = Adafruit_DHT.Adafruit_DHT.AM2302
        elif model == "DHT22":
            self._sensor_model = Adafruit_DHT.Adafruit_DHT.DHT22
        else:
            self._sensor_model = Adafruit_DHT.Adafruit_DHT.DHT11

    def update_status(self, status: Status):
        humidity, temperature = Adafruit_DHT.read_retry(self._sensor_model, self._pin)
        if "temperature" in self.sensors:
            status["temperature"] = round(temperature, 2)
        if "humidity" in self.sensors:
            status["humidity"] = round(humidity, 2)
