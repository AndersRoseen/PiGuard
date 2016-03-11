from sensors import ISensor
from piguardtyping import Status
import Adafruit_BMP.BMP085 as BMP085

_bmp_sensor = BMP085.BMP085()


class BMPSensor(ISensor):

    def __init__(self, active_sensors: [str]):
        self.sensors = active_sensors

    def update_status(self, status: Status):
        if "pressure" in self.sensors:
            pressure = _bmp_sensor.read_pressure() / 10e1
            status["pressure"] = round(pressure, 2)
        if "altitude" in self.sensors:
            altitude = _bmp_sensor.read_altitude()
            status["altitude"] = round(altitude, 2)
