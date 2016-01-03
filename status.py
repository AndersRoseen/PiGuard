from abc import ABCMeta, abstractmethod
from enum import Enum
import datetime
import factory

class Status:
    
    def __init__(self):
        self.timestamp = datetime.datetime.now()
        self.picture = None

class Event(Enum):
    empty = "empty"
    motionDetected = "motionDetected"
        


class StatusGenerator:
    
    def __init__(self):
        self.__sensors = factory.get_sensors()
    
    def get_current_status(self):
        status = Status()
        for sensor in self.__sensors:
            sensor.update_status(status)
        
        return status


class StatusHandler:
    
    def __init__(self):
        self.__analyzers = factory.get_status_analyzers()
        self.__actions = factory.get_actions()
        self.__actions_per_event = factory.get_actions_per_event()
        
    def manage_status(self, status):
        events = self.__analyze(status)
        actions = self.__prepare_actions(events)
        self.__process_actions(actions, status)
    
    def __analyze(self, status):
        events = []
        for analyzer in self.__analyzers:
            curr_events = analyzer.analyze_status(status)
            events.extend(curr_events)
        
        events.append(Event.empty)
        return events
    
    def __prepare_actions(self, events):
        action_types = {}
        for event in events:
            actions_per_event = self.__actions_per_event[event]
            for action_type in actions_per_event:
                if action_type in action_types:
                    action_types[action_type].append(event)
                else:
                    action_types[action_type] = [event]
        
        return action_types
    
    def __process_actions(self, actions, status):
        for action_type, events in actions.items():
            action = self.__actions[action_type]
            action.perform_action(status, events)
            

class IStatusAnalyzer(metaclass=ABCMeta):
    
    @abstractmethod
    def analyze_status(self, status):
        pass
        

class ActionType(Enum):
    sendMail = "sendMail"
    uploadStatus = "uploadStatus"
    


class IAction(metaclass=ABCMeta):
        
    @abstractmethod
    def perform_action(self, status, events):
        pass