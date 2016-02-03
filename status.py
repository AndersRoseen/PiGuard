from abc import ABCMeta, abstractmethod
from enum import Enum
from queue import Empty
import datetime


class Event(Enum):
    empty = "empty"
    motionDetected = "motionDetected"
    onDemandRequest = "onDemandRequest"


class StatusGenerator(object):
    
    def __init__(self, sensors):
        self._sensors = sensors

    def _new_status(self):
        status = dict()
        status["timestamp"] = datetime.datetime.now()
        return status
    
    def get_current_status(self):
        status = self._new_status()
        for sensor in self._sensors:
            sensor.update_status(status)
        
        return status


class StatusHandler(object):
    
    def __init__(self, analyzers, actions, actions_per_event, action_queue):
        self._analyzers = analyzers
        self._actions = actions
        self._actions_per_event = actions_per_event
        self._on_demand_actions_queue = action_queue
        
    def manage_status(self, status, mode):
        events = self._analyze(status)
        actions = self._prepare_actions(events, mode)
        self._process_actions(actions, status)
    
    def _analyze(self, status):
        events = []
        for analyzer in self._analyzers:
            curr_events = analyzer.analyze_status(status)
            events.extend(curr_events)
        
        events.append(Event.empty)
        return events
    
    def _prepare_actions(self, events, mode):
        action_types = dict()
        for event in events:
            actions_per_event = self._actions_per_event[mode][event]
            for action_type in actions_per_event:
                if action_type in action_types:
                    action_types[action_type].append(event)
                else:
                    action_types[action_type] = [event]

        while True:
            try:
                action_type = self._on_demand_actions_queue.get_nowait()
                action_types[action_type] = [Event.onDemandRequest]
            except Empty:
                break
        
        return action_types
    
    def _process_actions(self, actions, status):
        for action_type, events in actions.items():
            action = self._actions[action_type]
            try:
                action.perform_action(status, events)
            except:
                print("Issue while performing ", action_type)
            

class IStatusAnalyzer(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def analyze_status(self, status):
        pass
        

class ActionType(Enum):
    sendMail = "sendMail"
    uploadStatus = "uploadStatus"
    

class IAction(object):
    __metaclass__ = ABCMeta
        
    @abstractmethod
    def perform_action(self, status, events):
        pass