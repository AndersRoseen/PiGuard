from abc import ABCMeta, abstractmethod


class IStatusAnalyzer(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def analyze_status(self, status: dict) -> list:
        return []


def get_status_analyzers() -> list:
    import motiondetector
    analyzers = list()
    analyzers.append(motiondetector.MotionDetector())
    return analyzers
