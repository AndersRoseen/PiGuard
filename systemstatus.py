from enum import Enum


class Mode(Enum):
    monitoring = "monitoring"
    surveillance = "surveillance"


class SystemStatus(Enum):
    started = "started"
    stopped = "stopped"
