from queue import Empty
from systemstatus import Mode
from sensors import ISensor
from piguardtyping import Status
import actions
import analyzers
import datetime
import queue


class StatusGenerator(object):
    
    def __init__(self, sensors_list: [ISensor]):
        self._sensors = sensors_list

    def _new_status(self) -> Status:
        status = dict()
        status["timestamp"] = datetime.datetime.now()
        return status
    
    def get_current_status(self) -> Status:
        status = self._new_status()
        for sensor in self._sensors:
            sensor.update_status(status)
        
        return status


class StatusHandler(object):
    
    def __init__(self, analyzers_list: [analyzers.IStatusAnalyzer], actions_list: {actions.ActionType: actions.IAction}, actions_per_event: {Mode: {actions.Event: actions.ActionType}}, action_queue: queue.Queue):
        self._analyzers = analyzers_list
        self._actions = actions_list
        self._actions_per_event = actions_per_event
        self._on_demand_actions_queue = action_queue
        
    def manage_status(self, status: Status, mode: Mode):
        events = self._analyze(status)
        actions_list = self._prepare_actions(events, mode)
        self._process_actions(actions_list, status)
    
    def _analyze(self, status: Status) -> [actions.Event]:
        events = list()
        for analyzer in self._analyzers:
            curr_events = analyzer.analyze_status(status)
            events.extend(curr_events)
        
        return events
    
    def _prepare_actions(self, events: [actions.Event], mode: Mode):
        action_types = set()
        for event in events:
            actions_per_event = self._actions_per_event[mode][event]
            for action_type in actions_per_event:
                action_types.add(action_type)

        while True:
            try:
                action_type = self._on_demand_actions_queue.get_nowait()
                action_types.add(action_type)
            except Empty:
                break
        
        return action_types
    
    def _process_actions(self, actions_list: [actions.ActionType], status: Status):
        for action_type in actions_list:
            action = self._actions[action_type]
            try:
                action.perform_action(status)
            except:
                print("Issue while performing ", action_type)


def get_status_handler(action_queue: queue.Queue) -> StatusHandler:
    analyzers_list = analyzers.get_status_analyzers()
    actions_list = actions.get_actions()
    actions_per_event = actions.get_actions_per_event()

    return StatusHandler(analyzers_list, actions_list, actions_per_event, action_queue)


