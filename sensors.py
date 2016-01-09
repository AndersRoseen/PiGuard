from abc import ABCMeta, abstractmethod


class ISensor(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def update_status(self, status):
        pass