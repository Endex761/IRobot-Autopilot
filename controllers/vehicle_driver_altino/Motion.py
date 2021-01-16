from Constants import MAX_ANGLE, MAX_SPEED, UNKNOWN
from PathPlanner import U_TURN
from Utils import logger

PATH_FOLLOWING = 1
PARKING = 2
COLLISION_AVOIDANCE = 3
MANUAL = 4

# class to handle car motion service
class Motion: #TODO global planner
    # initialize motion service
    def __init__(self, actuators, pathRunner, parking, collisionAvoidance, manualDrive, externalController):
        self.actuators = actuators
        self.pathRunner = pathRunner
        self.collisionAvoidance = collisionAvoidance
        self.parking = parking
        self.manualDrive = manualDrive
        self.externalController = externalController

        self.status = PATH_FOLLOWING
        self.prevStatus = UNKNOWN
        actuators.setSpeed(0.5)

    def update(self):
        self.updateExternalController()
        collisionImminent = False
        isUTurning = self.pathRunner.isUTurning()
        isParking = self.parking.isParking()
        isParked = self.parking.isParked()
        isSearchingPark = self.parking.isSearchingPark()
        isManualActive = self.manualDrive.isEnabled()
        isGoalReached = self.pathRunner.isGoalReach()

        collisionImminent = self.collisionAvoidance.isCollisionDetected()
        obstacleDetected = self.collisionAvoidance.isObstacleDetected()

        logger.debug("collissionImminent: " + str(collisionImminent) + " obstacleDetected: " + str(obstacleDetected) + " isUTurning: " + str(isUTurning) )

        if self.status == PATH_FOLLOWING:
            logger.debug("MOTION: PathFollowing")
            self.updatePathRunner()

            # During path find a object that can be avoid
            if collisionImminent and not isUTurning:
                self.setStatus(COLLISION_AVOIDANCE)

            if isGoalReached:
                self.parking.enable()
                self.setStatus(PARKING)

            
        elif self.status == PARKING:
            logger.debug("MOTION: Parking")
            self.updateParking()

            if isParked:
                self.setSpeed(0)
                self.setAngle(0)

            # During parking find a object that can be avoid
            if collisionImminent and isSearchingPark:
                self.setStatus(COLLISION_AVOIDANCE)

        elif self.status == COLLISION_AVOIDANCE:
            logger.debug("MOTION: Collision Avoidance")
            self.updateCollisionAvoidance()

            if not collisionImminent:
                self.setPrevStatus()

            # During path find a object that can't be avoid
            if obstacleDetected and not isUTurning and self.prevStatus == PATH_FOLLOWING:
                logger.debug("Reset Path")
                self.pathRunner.updatePath()
                collisionImminent = False            
                self.collisionAvoidance.resetObstacleDetection()
                self.setStatus(PATH_FOLLOWING)

        elif self.status == MANUAL:
            logger.debug("MOTION: Manual")
            self.manualDrive.enable()
            self.updateManualDrive()
        
        else:
            logger.warning("MOTION STATUS: " + str(self.status))

    def setPrevStatus(self):
        tempStatus = self.prevStatus
        self.prevStatus = self.status
        self.status = tempStatus

    def setStatus(self, status):
        if self.status != status:
            self.prevStatus = self.status
            self.status = status

    # update parking commands
    def updateParking(self):
        if self.parking.isEnabled():
            newSpeed = self.parking.getSpeed()
            newAngle = self.parking.getAngle()
            logger.debug("Parking - Speed: " + str(newSpeed) + " Angle: " + str(newAngle))
            self.setAngleAndSpeed(newAngle, newSpeed)

    # update path runner commands
    def updatePathRunner(self):
        if self.pathRunner.isEnabled():
            newSpeed = self.pathRunner.getSpeed()
            newAngle = self.pathRunner.getSteeringAngle()
            logger.debug("Path Runner - Speed: " + str(newSpeed) + " Angle: " + str(newAngle))
            if self.pathRunner.isGoalReach():
                self.pathRunner.disable()
                self.parking.enable()
            self.setAngleAndSpeed(newAngle, newSpeed)

    # update collision avoidance commands
    def updateCollisionAvoidance(self):
        if self.collisionAvoidance.isEnabled():
            newSpeed = self.collisionAvoidance.getSpeed()
            newAngle = self.collisionAvoidance.getSteeringAngle()
            logger.debug("Collision Avoidance - Speed: " + str(newSpeed) + " Angle: " + str(newAngle))
            self.setAngleAndSpeed(newAngle, newSpeed)
    
    def updateManualDrive(self):
        if self.manualDrive.isEnabled():
            newSpeed = self.manualDrive.getSpeed()
            newAngle = self.manualDrive.getAngle()
            logger.debug("Manual Drive - Speed: " + str(newSpeed) + " Angle: " + str(newAngle))
            self.setAngleAndSpeed(newAngle, newSpeed)

    def updateExternalController(self):
        if self.externalController.isEnabled():
            status = self.externalController.getMotionStatus()
            if status != UNKNOWN:
                self.status = self.externalController.getMotionStatus()

    # set angle and speed on the actuators    
    def setAngleAndSpeed(self, angle, speed):
        logger.debug("Setting Actuators - Angle: " + str(angle) + " - Speed: " + str(speed))
        self.actuators.setAngle(angle * MAX_ANGLE)
        self.actuators.setSpeed(speed * MAX_SPEED)

    # set actuators speed
    def setSpeed(self, speed):
        self.actuators.setSpeed(speed)

    # set actuators steering angle
    def setAngle(self, angle):
        self.actuators.setAngle(angle)