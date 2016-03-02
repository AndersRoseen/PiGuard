import Adafruit_DHT
from sensors import ISensor
from piguardtyping import Status


class DHTSensor(ISensor):

    def __init__(self, active_sensors: [str], model: str, gpio_pin: int):
        self.sensors = active_sensors
        self._pin = gpio_pin
        if model == "AM2302":
            self._sensor_model = Adafruit_DHT.AM2302
        elif model == "DHT22":
            self._sensor_model = Adafruit_DHT.DHT22
        else:
            self._sensor_model = Adafruit_DHT.DHT11

        self._old_temperature = 0
        self._old_humidity = 0

    def update_status(self, status: Status):
        humidity, temperature = Adafruit_DHT.read(self._sensor_model, self._pin)
        # the sensor may fail and since I do not want to use the read_retry function (waste too much time)
        # I store old values for humidity and temperature and if a sensor read fails the old ones are returned.
        # This is a good solution in case of short sampling intervals. If the sampling interval is long (above the
        # the minute) it's better to use the read_retry function instead.
        if humidity is None:
            humidity = self._old_humidity
        else:
            self._old_humidity = humidity

        if temperature is None:
            temperature = self._old_temperature
        else:
            self._old_temperature = temperature

        if "temperature" in self.sensors:
            status["temperature"] = round(temperature, 2)
        if "humidity" in self.sensors:
            status["humidity"] = round(humidity, 2)
