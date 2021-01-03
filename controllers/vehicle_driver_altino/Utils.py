from enum import IntEnum, auto

class Status(IntEnum):
    INIT = auto()
    PARK_FOUND = auto()
    SEARCHING_PARK = auto()
    PARKING = auto()
    PARKING2 = auto()
    FORWARD = auto()
    FORWARD2 = auto()
    STOP = auto()
    MANUAL = auto()
    

class DistanceSensors:

    def __init__(self):
        self.frontLeft = 0
        self.frontCenter = 0
        self.frontRight = 0
        
        self.sideLeft = 0
        self.sideRight = 0
        self.back = 0

class PositionSensors:

    def __init__(self):
        self.frontLeft = 0
        self.frontRight = 0
        self.rearLeft = 0
        self.rearRight = 0


class Logger:
    
    ENDC = '\033[0m'

    def __init__(self):
        self.INFO = 1
        self.WARNING = 2
        self.ERROR = 3
        self.DEBUG = 4

        self.INFO_ENABLED = True
        self.WARNING_ENABLED = True
        self.ERROR_ENABLED = True
        self.DEBUG_ENABLED = True

        self.INFO_COLOR = ''
        self.WARNING_COLOR = '\033[93m'
        self.ERROR_COLOR = '\033[91m'
        self.DEBUG_COLOR = '\033[92m'

    def log(self, message, level = 1):
        if   level == self.INFO and self.INFO_ENABLED:
            print(self.INFO_COLOR + "INFO: " + str(message) + self.ENDC)
        elif level == self.WARNING and self.WARNING_ENABLED:
            print(self.WARNING_COLOR + "WARNING: " + str(message) + self.ENDC)
        elif level == self.ERROR and self.ERROR_ENABLED:
            print(self.ERROR_COLOR + "ERROR: " + str(message) + self.ENDC)
        elif level == self.DEBUG and self.DEBUG_ENABLED:
            print(self.DEBUG_COLOR + "DEBUG: " + str(message) + self.ENDC)

    def error(self, message):
        self.log(message, self.ERROR)

    def warning(self, message):
        self.log(message, self.WARNING)

    def info(self, message):
        self.log(message, self.INFO)

    def debug(self, message):
        self.log(message, self.DEBUG)



