from sensors import ISensor
from piguardtyping import Status
import MyPyBMP180


class BMPSensor(ISensor):

    def __init__(self, active_sensors: [str]):
        self.sensors = active_sensors

    def update_status(self, status: Status):
        try:
            pressure, temperature = MyPyBMP180.sensor_read()
            if "pressure" in self.sensors:
                status["pressure"] = pressure
            if "temperature" in self.sensors:
                status["temperature"] = temperature
        except MyPyBMP180.BMP180Exception as error:
            print(error.message)


