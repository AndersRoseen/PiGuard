import MyPyDHT
from sensors import ISensor
from piguardtyping import Status


class DHTSensor(ISensor):

    def __init__(self, active_sensors: [str], model: str, gpio_pin: int):
        self.sensors = active_sensors
        self._pin = gpio_pin
        self._model = model

    def update_status(self, status: Status):
        try:
            humidity, temperature = MyPyDHT.sensor_read(self._pin, use_cache=True)

            if "temperature" in self.sensors:
                status["temperature"] = round(temperature, 2)
            if "humidity" in self.sensors:
                status["humidity"] = round(humidity, 2)

        except MyPyDHT.DHTException as error:
            print(error.message)


