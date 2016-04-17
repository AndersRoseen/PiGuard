from abc import ABCMeta, abstractmethod
from piguardtyping import Status
import configmanager


class ISensor(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def update_status(self, status: Status):
        pass


def _get_picamera_sensor() -> ISensor:
    from camerasensor import CameraSensor
    return CameraSensor()


def _get_sense_hat_sensor() -> ISensor:
    from sensehatsensor import SenseHatSensor
    active_sensors = configmanager.config["sensehat"]["active_sensors"].split(",")
    return SenseHatSensor(active_sensors)


def _get_pir_sensor() -> ISensor:
    from pirsensor import PIRSensor
    pin = configmanager.config.getint("pir", "gpio_pin")
    return PIRSensor(pin)


def _get_dht_sensor() -> ISensor:
    from dhtsensor import DHTSensor
    pin = configmanager.config.getint("dht", "gpio_pin")
    active_sensors = configmanager.config["dht"]["active_sensors"].split(",")
    model = configmanager.config["dht"]["model"]
    return DHTSensor(active_sensors, model, pin)


def _get_bmp_sensor() -> ISensor:
    from bmpsensor import BMPSensor
    active_sensors = configmanager.config["bmp"]["active_sensors"].split(",")
    return BMPSensor(active_sensors)


def _get_mqair_sensor() -> ISensor:
    from mqairsensor import MQ135Sensor
    cal_vol = configmanager.config.getfloat("mq135", "calibration_voltage")
    adc_port = configmanager.config.getint("mq135", "adc_port")
    rl = configmanager.config.getfloat("mq135", "r_load")
    return MQ135Sensor(cal_vol, rl, adc_port)


def _get_sensor_generators() -> dict:
    sensors = dict()
    sensors["picamera"] = _get_picamera_sensor
    sensors["sensehat"] = _get_sense_hat_sensor
    sensors["pir"] = _get_pir_sensor
    sensors["dht"] = _get_dht_sensor
    sensors["bmp"] = _get_bmp_sensor
    sensors["mqair"] = _get_mqair_sensor
    return sensors


def get_sensors() -> [ISensor]:
    sensors_list = list()

    sensors_to_use = configmanager.config["sensors"]["sensors_list"].split(",")
    generators = _get_sensor_generators()
    for sensor in sensors_to_use:
        sensors_list.append(generators[sensor]())

    return sensors_list
