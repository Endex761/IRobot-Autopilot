
from Devices import Actuators
from PathPlanner import U_TURN
from PathRunner import PathRunner
from Utils import logger


class Motion:

    def __init__(self, actuators, pathRunner, collisionAvoidance):
        self.actuators = actuators
        self.pathRunner = pathRunner
        self.collisionAvoidance = collisionAvoidance

        actuators.setSpeed(0.5)

    def update(self):
        self.updatePathRunner()

    def updatePathRunner(self):
        newSpeed = self.pathRunner.getSpeed()
        newAngle = self.pathRunner.getSteeringAngle()
        if newAngle != U_TURN:
            self.actuators.setAngle(newAngle)
            self.actuators.setSpeed(newSpeed)