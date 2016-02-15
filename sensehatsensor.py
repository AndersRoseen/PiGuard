from sense_hat import SenseHat
from sensors import ISensor
from piguardtyping import Status


sense_hat = SenseHat()


class SenseHatSensor(ISensor):

    def __init__(self, active_sensors: [str]):
        self.sensors = active_sensors

    def update_status(self, status: Status):
        global sense_hat

        if "temperature" in self.sensors:
            status["temperature"] = round(sense_hat.temperature, 2)
            status["temperature_unit"] = "C"
        if "humidity" in self.sensors:
            status["humidity"] = round(sense_hat.humidity, 2)
            status["humidity_unit"] = "%"
        if "pressure" in self.sensors:
            status["pressure"] = round(sense_hat.pressure, 2)
            status["pressure_unit"] = "mbar"
