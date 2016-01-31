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


def get_available_sensors():
    sensors = dict()
    sensors["picamera"] = _get_picamera_sensor
    sensors["sensehat"] = _get_sense_hat_sensor
    return sensors