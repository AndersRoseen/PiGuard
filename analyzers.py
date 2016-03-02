from abc import ABCMeta, abstractmethod
from actions import Event
from piguardtyping import Status


class IStatusAnalyzer(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def analyze_status(self, status: Status) -> [Event]:
        return []


def get_status_analyzers() -> [IStatusAnalyzer]:
    import motiondetector
    analyzers = list()
    analyzers.append(motiondetector.MotionDetector())
    return analyzers
