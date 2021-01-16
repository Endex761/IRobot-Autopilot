
from Constants import DISABLED, ENABLED
from Constants import DEBUG, UNKNOWN
from Utils import logger

PATH_FOLLOWING = 1
PARKING = 2
COLLISION_AVOIDANCE = 3
MANUAL = 4

class ExternalController:

    def __init__(self, keyboard):
        self.keyboard = keyboard
        self.status = DISABLED
        self.motionStatus = UNKNOWN

    
    def update(self):
        if self.isEnabled():
            self.updateCommands()

    def getMotionStatus(self):
        return self.motionStatus

    def updateCommands(self):
        # get current key
        currentKey = self.keyboard.getKey()

        # press P to find parking lot
        if self.keyboard.isKeyPressed(currentKey, 'p'):
            logger.info("Looking for a parking lot")
            self.motionStatus = PARKING
        
        # press M to manual control
        elif self.keyboard.isKeyPressed(currentKey, 'm'):
            logger.info("Manual")
            self.motionStatus = MANUAL

        # press A to auto control
        elif self.keyboard.isKeyPressed(currentKey, 'a'):
            logger.info("Auto")
            self.motionStatus = PATH_FOLLOWING

        # return current key to allow other controls 
        return currentKey

    
    def isEnabled(self):
            return self.status != DISABLED

    def enable(self):
        self.status = ENABLED

    def disable(self):
        self.status = DISABLED
