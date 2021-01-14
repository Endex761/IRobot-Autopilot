from enum import IntEnum, auto
from Constants import DEBUG
HEIGHT = 16
WIDTH = 24

# useless?
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
    FOLLOW_LINE = auto()
    CENTER = auto()
    TURN = auto()
    
class Orientation(IntEnum):
    NORD = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

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
        exit(1)

    def warning(self, message):
        self.log(message, self.WARNING)

    def info(self, message):
        self.log(message, self.INFO)

    def debug(self, message):
        self.log(message, self.DEBUG)

# DEFINE LOGGER TO BE USED IN THE PROGRAM
logger = Logger()
logger.DEBUG_ENABLED = DEBUG

class Position:

    def __init__(self, x, y):
        self.x = 0
        self.y = 0
        self.setX(x)
        self.setY(y)

    def getX(self):
        return int(round(self.x,0))

    def getY(self):
        return int(round(self.y, 0))

    def setX(self, x):
        if x >= 0 and x < HEIGHT:
            self.x = x

    def setY(self, y):
        if y >= 0 and y < WIDTH:
            self.y = y

    def getPositionArray(self):
        return (self.getX(), self.getY())

    def __str__(self):
        return "[X: " + str(self.x) + ", Y:" + str(self.y) + "]"
    
    def __eq__(self, other):
        try:
            return self.x == other.x and self.y == other.y
        except:
            return False
       


       