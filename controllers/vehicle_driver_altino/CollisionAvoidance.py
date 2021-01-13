from Constants import LEFT, RIGHT
from Utils import logger

DETECT = 1

# class to handle collision avoidance service
class CollissionAvoidance:
    # initialize collision avoidance service
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

        # true if imminent collision is detected
        self.collisionDetect = False

    # return true is an imminent collision is detected 
    def isCollisionDetect(self):
        return self.collisionDetect

    # compute angle and speed to avoid obstacle 
    def computeSpeedAndAngle(self):
        # set values of thresholds

        tolerance = 10
        frontThreshold = 700
        frontSideThreshold = 750
        sideThreshold = 890

        logger.debug("SL: " + str(self.sl) + " SR: " + str(self.sr))
        logger.debug("FL: " + str(self.fl) + " FR: " + str(self.fr) + " FC: " + str(self.fc))

        if self.fc > frontThreshold:
            tolerance = -1
        else:
            tolerance = 10

        if self.fc > 750:
            self.speed = 0.2
        else:
            self.speed = 0.5

        if self.fl > 750 and self.fr > 750 or self.fc > 950:
            self.speed = 0.0
            logger.debug("Street is closed")

        # check if front left obstacle, turn right
        if self.fl > self.fr + tolerance and (self.fl > frontSideThreshold or self.fc > frontThreshold):
            # self.steeringAngle += (self.fl - self.fr)  / 500.0
            self.steeringAngle = RIGHT * (self.fl / 2000.0 + (self.fl - self.fr) / 2000.0 )
            # logger.debug("Steering angle: " + str(RIGHT * frontLeftSensor / 1000.0 * MAX_ANGLE))
            self.collisionDetect = True
            logger.debug("Steering angle (FRONT LEFT): " + str(self.steeringAngle))

        # check if front right obstacle, turn left
        elif self.fr > self.fl + tolerance and (self.fr > frontSideThreshold or self.fc > frontThreshold):
            # self.steeringAngle -= (self.fl - self.fr) / 500.0
            self.steeringAngle = LEFT * (self.fr / 2000.0 + (self.fr - self.fl) / 2000.0 )
            # logger.debug("Steering angle: " + str(LEFT * frontRightSensor / 1000.0 * MAX_ANGLE))
            self.collisionDetect = True
            logger.debug("Steering angle (FRONT RIGHT): " + str(self.steeringAngle))

        # check if side left obstacle, turn slight right
        elif self.sl > sideThreshold:
            self.steeringAngle = RIGHT * self.sl / 2000.0
            self.collisionDetect = True

        # check if side right obstacle, turn slight left
        elif self.sr > sideThreshold:
            self.steeringAngle = LEFT * self.sr / 2000.0
            self.collisionDetect = True

        # if no obstacle go straight
        else:
            self.steeringAngle = self.steeringAngle / 1.5
            self.collisionDetect = False

        if self.steeringAngle > 1:
            self.steeringAngle = 1
        
        if self.steeringAngle < -1:
            self.steeringAngle = -1

    # get collision avoidance angle
    def getSteeringAngle(self):
        return self.steeringAngle

    # get collision avoidance speed
    def getSpeed(self):
        return self.speed

    # update collision avoidance service
    def update(self):
        self.updateSensorsValue()
        self.computeSpeedAndAngle()

    # update sensors values
    def updateSensorsValue(self):
        self.fl = self.distanceSensors.frontLeft.getValue()
        self.fc = self.distanceSensors.frontCenter.getValue()
        self.fr = self.distanceSensors.frontRight.getValue()

        self.sr = self.distanceSensors.sideRight.getValue()
        self.sl = self.distanceSensors.sideLeft.getValue()
        self.bc = self.distanceSensors.backCenter.getValue()

    # return distance sensors instance
    def getDistanceSensor(self):
        return self.distanceSensors
