from sense_hat import SenseHat
from sensors import ISensor


sense_hat = SenseHat()


class SenseHatSensor(ISensor):

    def update_status(self, status):
        global sense_hat

        status["temperature"] = round(sense_hat.temperature, 2)
        status["temperature_unit"] = "C"
        status["humidity"] = round(sense_hat.humidity, 2)
        status["humidity_unit"] = "%"
        status["pressure"] = round(sense_hat.pressure, 2)
        status["pressure_unit"] = "mbar"
