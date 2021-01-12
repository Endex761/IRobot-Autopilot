
# STATES
from Constants import LEFT, MAX_ANGLE, RIGHT
from Utils import logger

DETECT = 1
class CollissionAvoidance:

    def __init__(self, distanceSensors):
        self.distanceSensors = distanceSensors

        self.fl = 0
        self.fc = 0
        self.fr = 0
        
        self.sr = 0
        self.sl = 0
        self.bc = 0

        self.steeringAngle = 0.0
        self.speed = 0.0

        self.status = DETECT

    
    def computeSpeedAndAngle(self):
        # set values of thresholds
        tolerance = 0
        sideThreshold = 950

        # check if front left obstacle, turn right
        if self.fl > self.fr + tolerance:
            self.steeringAngle += (self.fl - self.fr)  / 1000
            #self.steeringAngle = RIGHT * self.fl / 500.0 * MAX_ANGLE
            # logger.debug("Steering angle: " + str(RIGHT * frontLeftSensor / 1000.0 * MAX_ANGLE))
            logger.debug("Steering angle: " + str(self.steeringAngle))

        # check if front right obstacle, turn left
        elif self.fr > self.fl + tolerance:
            self.steeringAngle -= (self.fl - self.fr) / 1000
            #self.steeringAngle = LEFT * self.fr / 500.0 * MAX_ANGLE
            # logger.debug("Steering angle: " + str(LEFT * frontRightSensor / 1000.0 * MAX_ANGLE))
            logger.debug("Steering angle: " + str(self.steeringAngle))

        # check if side left obstacle, turn slight right
        elif self.sl > sideThreshold:
            self.steeringAngle = RIGHT * self.sl / 4000.0 * MAX_ANGLE

        # check if side right obstacle, turn slight left
        elif self.sr > sideThreshold:
            self.steeringAngle = LEFT * self.sr / 4000.0 * MAX_ANGLE

        # if no obstacle go straight
        else:
            self.steeringAngle = self.steeringAngle / 1.5

        """if self.steeringAngle > 1:
            self.steeringAngle = 1
        
        if self.steeringAngle < -1:
            self.steeringAngle = -1"""

    def getSteeringAngle(self):
        return self.steeringAngle

    def update(self):
        self.updateSensorsValue()
        self.computeSpeedAndAngle()

    # update sensors values
    def updateSensorsValue(self):
        self.fl = self.distanceSensors.frontLeft.getValue()
        self.fc = self.distanceSensors.frontCenter.getValue()
        self.fr = self.distanceSensors.frontRight.getValue()

        self.sr = self.distanceSensors.sideLeft.getValue()
        self.sl = self.distanceSensors.sideRight.getValue()
        self.bc = self.distanceSensors.back.getValue()