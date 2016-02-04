from enum import Enum
from abc import ABCMeta, abstractmethod


class Event(Enum):
    empty = "empty"
    motionDetected = "motionDetected"
    onDemandRequest = "onDemandRequest"


class ActionType(Enum):
    sendMail = "sendMail"
    uploadStatus = "uploadStatus"


class IAction(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def perform_action(self, status, events):
        pass


def get_actions():
    import mailsender
    import uploader

    actions = dict()
    actions[ActionType.sendMail] = mailsender.get_mail_sender()
    actions[ActionType.uploadStatus] = uploader.get_uploader()
    return actions


def get_actions_per_event():
    from piguardsystem import Mode
    ea = dict()
    ea[Mode.surveillance] = dict()
    ea[Mode.surveillance][Event.empty] = [ActionType.uploadStatus]
    ea[Mode.surveillance][Event.motionDetected] = [ActionType.sendMail, ActionType.uploadStatus]

    ea[Mode.monitoring] = dict()
    ea[Mode.monitoring][Event.empty] = [ActionType.uploadStatus]
    ea[Mode.monitoring][Event.motionDetected] = list()

    return ea

