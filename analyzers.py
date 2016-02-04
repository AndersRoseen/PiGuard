from abc import ABCMeta, abstractmethod


class IStatusAnalyzer(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def analyze_status(self, status):
        pass


def get_status_analyzers():
    import motiondetector
    analyzers = list()
    analyzers.append(motiondetector.MotionDetector())
    return analyzers
