from Constants import LEFT, RIGHT
from Utils import logger

# Collision Avoidance status
DISABLED = 1
ENABLED = 2

# class to handle collision avoidance service
class CollissionAvoidance:
    # initialize collision avoidance service
    def __init__(self, distanceSensors):
        self.distanceSensors = distanceSensors

        # initialize sensors values
        self.fl = 0
        self.fc = 0
        self.fr = 0
        
        self.sr = 0
        self.sl = 0
        
        self.bl = 0
        self.bc = 0
        self.br = 0
        
        # initialize steering angle and speed
        self.steeringAngle = 0.0
        self.speed = 0.0

        self.status = DISABLED

        # true if imminent collision is detected
        self.collisionDetected = False

        self.obstacleDetected = False

    def isEnabled(self):
        return self.status != DISABLED

    def enable(self):
        self.status = ENABLED

    def disable(self):
        self.status = DISABLED

    # return true is an imminent collision is detected 
    def isCollisionDetected(self):
        return self.collisionDetected

    def isObstacleDetected(self):
        return self.obstacleDetected

    def resetObstacleDetection(self):
        self.obstacleDetected = False

    # compute angle and speed to avoid obstacle 
    def computeSpeedAndAngle(self):
        # set values of thresholds

        tolerance = 10
        frontThreshold = 700
        frontSideThreshold = 620
        sideThreshold = 800

        # logging distance sensors
        logger.debug("SL: " + str(self.sl) + " SR: " + str(self.sr))
        logger.debug("FL: " + str(self.fl) + " FR: " + str(self.fr) + " FC: " + str(self.fc))
        logger.debug("BL: " + str(self.bl) + " BR: " + str(self.br) + " BC: " + str(self.bc))

        # if collission imminent lowering the tolerance
        if self.fc > frontThreshold:
            tolerance = 0
        else:
            tolerance = 10

        # if front obstacle reduce speed
        if self.fc > 750:
            self.speed = 0.2
        else:
            self.speed = 0.5

        # if no way to escape, obstacle is detected
        if self.fl > 850 and self.fr > 850 or self.fc > 850:
            logger.debug("Obstacle Detected!")
            self.obstacleDetected = True
        else:
            self.obstacleDetected = False

        # check if front left obstacle, turn right
        if self.fl > self.fr + tolerance and (self.fl > frontSideThreshold or self.fc > frontThreshold):
            # self.steeringAngle += (self.fl - self.fr)  / 500.0
            self.steeringAngle = RIGHT * (self.fl / 2000.0 + (self.fl - self.fr) / 2000.0 )
            # logger.debug("Steering angle: " + str(RIGHT * frontLeftSensor / 1000.0 * MAX_ANGLE))
            self.collisionDetected = True
            # logger.debug("Steering angle (FRONT LEFT): " + str(self.steeringAngle))

        # check if front right obstacle, turn left
        elif self.fr > self.fl + tolerance and (self.fr > frontSideThreshold or self.fc > frontThreshold):
            # self.steeringAngle -= (self.fl - self.fr) / 500.0
            self.steeringAngle = LEFT * (self.fr / 2000.0 + (self.fr - self.fl) / 2000.0 )
            # logger.debug("Steering angle: " + str(LEFT * frontRightSensor / 1000.0 * MAX_ANGLE))
            self.collisionDetected = True
            # logger.debug("Steering angle (FRONT RIGHT): " + str(self.steeringAngle))

        # check if side left obstacle, turn slight right
        elif self.sl > sideThreshold:
            self.steeringAngle = RIGHT * self.sl / 3000.0
            self.collisionDetected = True

        # check if side right obstacle, turn slight left
        elif self.sr > sideThreshold:
            self.steeringAngle = LEFT * self.sr / 3000.0
            self.collisionDetected = True

        # if no obstacle go straight
        else:
            self.steeringAngle = self.steeringAngle / 1.5
            self.collisionDetected = False

        # maxing out the steerign angle
        if self.steeringAngle > 1:
            self.steeringAngle = 1
        
        if self.steeringAngle < -1:
            self.steeringAngle = -1

        # reduce speed if collision detected
        if self.collisionDetected:
            self.speed = 0.3

    # get collision avoidance angle
    def getSteeringAngle(self):
        return self.steeringAngle

    # get collision avoidance speed
    def getSpeed(self):
        return self.speed

    # update collision avoidance service
    def update(self):
        if self.status == ENABLED:
            self.updateSensorsValue()
            self.computeSpeedAndAngle()

    # update sensors values
    def updateSensorsValue(self):
        self.fl = self.distanceSensors.frontLeft.getValue()
        self.fc = self.distanceSensors.frontCenter.getValue()
        self.fr = self.distanceSensors.frontRight.getValue()

        self.sr = self.distanceSensors.sideRight.getValue()
        self.sl = self.distanceSensors.sideLeft.getValue()

        self.bl = self.distanceSensors.backLeft.getValue()
        self.bc = self.distanceSensors.backCenter.getValue()
        self.br = self.distanceSensors.backRight.getValue()

    # return distance sensors instance
    def getDistanceSensor(self):
        return self.distanceSensors
