from sensors import ISensor
from piguardtyping import Status
import Adafruit_ADS1x15

adc = Adafruit_ADS1x15.ADS1115()


def r(vo, rl):
    return ((5.0/vo) - 1.0)*rl


class MQ135Sensor(ISensor):

    def __init__(self, calibration_voltage: float, rload: float, adc_port: int):
        self.a = 5.15
        self.b = -0.35
        self.rl = rload
        rs = r(calibration_voltage, self.rl)
        self.ro = rs / (self.a*pow(400, self.b))
        self.val_max = 32767
        self.vm = 4.096
        self.port = adc_port

    def r(self, vo):
        return ((5.0/vo) - 1.0)*self.rl

    def update_status(self, status: Status):
        adc_val = adc.read_adc(self.port, gain=1)
        vo = (adc_val/self.val_max)*self.vm
        ppm = int(pow(((r(vo)/self.ro)/self.a), 1/self.b))
        status["co2"] = ppm
