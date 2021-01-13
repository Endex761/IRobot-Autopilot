from Constants import MAX_ANGLE, MAX_SPEED
from PathPlanner import U_TURN
from Utils import logger

# class to handle car motion service
class Motion:
    # initialize motion service
    def __init__(self, actuators, pathRunner, parking):
        self.actuators = actuators
        self.pathRunner = pathRunner
        self.parking = parking
        actuators.setSpeed(0.5)

    # update motion service
    def update(self):
        if self.parking.isEnabled():
            self.updateParking()
        else:
            self.updatePathRunner()

    def updateParking(self):
        newSpeed = self.parking.getSpeed()
        newAngle = self.parking.getAngle()
        self.actuators.setAngle(newAngle * MAX_ANGLE)
        self.actuators.setSpeed(newSpeed * MAX_SPEED)

    # update path runner comands
    def updatePathRunner(self):
        newSpeed = self.pathRunner.getSpeed()
        newAngle = self.pathRunner.getSteeringAngle()
        if newAngle != U_TURN:
            logger.log("ACTUAL ANGLE: " + str(newAngle))
            self.actuators.setAngle(newAngle * MAX_ANGLE)
            self.actuators.setSpeed(newSpeed * MAX_SPEED)

    # set actuators speed
    def setSpeed(self, speed):
        self.actuators.setSpeed(speed)

    # set actuators steering angle
    def setAngle(self, angle):
        self.actuators.setAngle(angle)