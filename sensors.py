from abc import ABCMeta, abstractmethod

class ISensor(metaclass=ABCMeta):
    
    @abstractmethod
    def update_status(self, status):
        pass