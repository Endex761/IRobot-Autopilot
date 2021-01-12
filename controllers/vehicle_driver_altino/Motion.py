from Constants import MAX_ANGLE, MAX_SPEED
from PathPlanner import U_TURN
from Utils import logger

# class to handle car motion service
class Motion:
    # initialize motion service
    def __init__(self, actuators, pathRunner):
        self.actuators = actuators
        self.pathRunner = pathRunner
        actuators.setSpeed(0.5)

    # update motion service
    def update(self):
        self.updatePathRunner()

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