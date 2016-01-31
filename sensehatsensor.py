from sense_hat import SenseHat
from sensors import ISensor


sense_hat = SenseHat()


class SenseHatSensor(ISensor):

    def update_status(self, status):
        global sense_hat

        status["temperature"] = sense_hat.temperature
        status["temperature_unit"] = "C"
        status["humidity"] = sense_hat.humidity
        status["humidity_unit"] = "%"
        status["pressure"] = sense_hat.pressure
        status["pressure_unit"] = "mbar"
