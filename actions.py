from enum import Enum
from abc import ABCMeta, abstractmethod
from systemstatus import Mode
from piguardtyping import Status


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
    def perform_action(self, status: Status):
        pass


def get_actions() -> {ActionType: IAction}:
    import mailsender
    import uploader

    actions = dict()
    actions[ActionType.sendMail] = mailsender.get_mail_sender()
    actions[ActionType.uploadStatus] = uploader.get_uploader()
    return actions


def get_actions_per_event() -> {Mode: {Event: ActionType}}:
    ea = dict()
    ea[Mode.surveillance] = dict()
    ea[Mode.surveillance][Event.empty] = [ActionType.uploadStatus]
    ea[Mode.surveillance][Event.motionDetected] = [ActionType.sendMail, ActionType.uploadStatus]

    ea[Mode.monitoring] = dict()
    ea[Mode.monitoring][Event.empty] = [ActionType.uploadStatus]
    ea[Mode.monitoring][Event.motionDetected] = list()

    return ea

