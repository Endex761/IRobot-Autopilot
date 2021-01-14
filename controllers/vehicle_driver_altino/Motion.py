from Constants import MAX_ANGLE, MAX_SPEED
from PathPlanner import U_TURN
from Utils import logger

# class to handle car motion service
class Motion: #TODO global planner
    # initialize motion service
    def __init__(self, actuators, pathRunner, parking, collisionAvoidance, manualDrive):
        self.actuators = actuators
        self.pathRunner = pathRunner
        self.collisionAvoidance = collisionAvoidance
        self.parking = parking
        self.manualDrive = manualDrive
        actuators.setSpeed(0.5)

    # update motion service
    def update(self):
        collisionImminent = False
        isUTurning = self.pathRunner.isUTurning()
        isParking = self.parking.isParking()

        #self.updateManualDrive()
        #return

        if self.collisionAvoidance.isEnabled() and (not isUTurning or not isParking):
            collisionImminent = self.collisionAvoidance.isCollisionDetect()
            if collisionImminent:
                self.updateCollisionAvoidance()

        if self.parking.isEnabled() and (isParking or not collisionImminent):
            self.updateParking()
        
        if self.pathRunner.isEnabled() and (isUTurning or not collisionImminent):
            self.pathRunner.setCollisionImminent(collisionImminent)
            self.updatePathRunner()

    # update parking commands
    def updateParking(self):
        if self.parking.isEnabled():
            newSpeed = self.parking.getSpeed()
            newAngle = self.parking.getAngle()
            self.setAngleAndSpeed(newAngle, newSpeed)

    # update path runner commands
    def updatePathRunner(self):
        if self.pathRunner.isEnabled():
            newSpeed = self.pathRunner.getSpeed()
            newAngle = self.pathRunner.getSteeringAngle()
            if self.pathRunner.isGoalReach():
                self.pathRunner.disable()
                self.parking.enable()
            self.setAngleAndSpeed(newAngle, newSpeed)

    # update collision avoidance commands
    def updateCollisionAvoidance(self):
        if self.collisionAvoidance.isEnabled():
            newSpeed = self.collisionAvoidance.getSpeed()
            newAngle = self.collisionAvoidance.getSteeringAngle()
            self.setAngleAndSpeed(newAngle, newSpeed)
    
    def updateManualDrive(self):
        if self.manualDrive.isEnabled():
            newSpeed = self.manualDrive.getSpeed()
            newAngle = self.manualDrive.getAngle()
            self.setAngleAndSpeed(newAngle, newSpeed)

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