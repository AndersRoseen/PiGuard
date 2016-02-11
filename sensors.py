from abc import ABCMeta, abstractmethod
import configmanager


class ISensor(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def update_status(self, status):
        pass


def _get_picamera_sensor():
    from camerasensor import CameraSensor
    return CameraSensor()


def _get_sense_hat_sensor():
    from sensehatsensor import SenseHatSensor
    active_sensors = configmanager.config["sensehat"]["active_sensors"].split(",")
    return SenseHatSensor(active_sensors)


def _get_pir_sensor():
    from pirsensor import PIRSensor
    pin = configmanager.config.getint("pir", "gpio_pin")
    return PIRSensor(pin)


def _get_sensor_generators():
    sensors = dict()
    sensors["picamera"] = _get_picamera_sensor
    sensors["sensehat"] = _get_sense_hat_sensor
    sensors["pir"] = _get_pir_sensor
    return sensors


def get_sensors():
    sensors_list = list()

    sensors_to_use = configmanager.config["sensors"]["sensors_list"].split(",")
    generators = _get_sensor_generators()
    for sensor in sensors_to_use:
        sensors_list.append(generators[sensor]())

    return sensors_list
