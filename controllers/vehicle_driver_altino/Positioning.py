import math
from Utils import Orientation, Position, logger
from Constants import WHEEL_RADIUS, UNKNOWN, SPX, SPY
import Map

# class for handling postioning service using odometry
class Positioning:

    #initialize positioning service
    def __init__(self, positionSensors, compass, lineFollower, actuators):
        self.positionSensors = positionSensors
        self.frontLeft = positionSensors.frontLeft
        self.frontRight = positionSensors.frontRight
        self.compass = compass
        self.lineFollower = lineFollower
        self.actuators = actuators

        self.leftWheelDistance = 0.0
        self.rightWheelDistance = 0.0
        self.reference = self.getActualDistance()

        self.lineAlreadyLost = False

        self.position = Position(SPX,SPY)
        self.orientation = UNKNOWN
        self.inaccurateOrientation = UNKNOWN
        self.updateOrientation()

    # set robot position in the map
    def setPosition(self, position):
        x = position.getX()
        y = position.getY()
        if x > 0 and x < Map.HEIGHT - 1:
            self.position.setX(position.x)
        if y > 0 and y < Map.WIDTH - 1:
            self.position.setY(position.y)
                
        #logger.warning("Invalid Position")
    
    # set robot orientation
    def setOrientation(self, orientation):
        self.orientation = orientation

    # get current stimated robot position
    def getPosition(self):
        return self.position

    # get current stimated robot orientation
    def getOrientation(self):
        return self.orientation

    # print status of positioning
    def printStatus(self):
        logger.debug("Orientation: " + str(self.orientation) + " - Positioning: " + str(self.position))

    # update positioning service
    def update(self):
        self.printStatus()
        self.updateWheelTraveledDistance()
        self.updateOrientation()
        self.updatePosition()
        self.computePositionBasedOnLandmark()

    # update distance traveled by wheels using encoders
    def updateWheelTraveledDistance(self):
        # get radiants from wheel
        radFLW = self.frontLeft.getValue()
        radFRW = self.frontRight.getValue()

        # compute distance traveled
        self.leftWheelDistance = radFLW * WHEEL_RADIUS
        self.rightWheelDistance = radFRW * WHEEL_RADIUS

    # return current stimated traveled distance
    def getActualDistance(self):
        return (self.leftWheelDistance + self.rightWheelDistance) / 2.0

    # update orientation using inaccurate compass orientation
    def updateOrientation(self):
        self.orientation = self.compass.getOrientation()
        self.inaccurateOrientation = self.compass.getInaccurateOrientation()

    # update positioning using map landmarks
    def computePositionBasedOnLandmark(self):
        # if the line get lost provably the robot is near an intersecion
        isLineLost = self.lineFollower.isLineLost()
        logger.debug("isLineLost: " + str(isLineLost) + " isLineAlreadyLost: " + str(self.lineAlreadyLost))
        if isLineLost and not self.lineAlreadyLost:
            self.lineAlreadyLost = True
            nearestIntersecion = Map.findNearestIntersection(self.position)
            offset = 0.25
            if nearestIntersecion != -1:
                x = nearestIntersecion.getX()
                y = nearestIntersecion.getY()
                if self.orientation == Orientation.NORD:
                    nearestIntersecion.setX(x + offset)
                if self.orientation == Orientation.EAST:
                    nearestIntersecion.setY(y - offset)
                if self.orientation == Orientation.SOUTH:
                    nearestIntersecion.setX(x - offset)
                if self.orientation == Orientation.WEST:
                    nearestIntersecion.setY(y + offset)
                
                self.position = nearestIntersecion
        elif not isLineLost:
            self.lineAlreadyLost = False

        # update position based on dead reckoning        
    def updatePosition(self):
        
        speed = self.actuators.getSpeed()

        if speed != 0:
            # get actual float map position
            x = self.position.x
            y = self.position.y

            # 72 = 0.50 m/s * speed/MAX_SPEED [1.8] / 40 step/s / 0.5 m
            # linearMove = ((0.50 * (speed/MAX_SPEED)) / 40) * 2
            linearMove = speed/72

            # compass decimal digits
            precision = 2

            turnCoeficent = 1
            # if turning you need to do less meters in order to change position in the map
            steeringAngle = self.actuators.getAngle()
            if abs(steeringAngle) == 0.57:
                turnCoeficent = 1.2

            # update position    
            newX = x - round(self.compass.getXComponent(), precision) * linearMove * turnCoeficent
            newY = y + round(self.compass.getYComponent(), precision) * linearMove * turnCoeficent
        
            self.setPosition(Position(newX,newY))

        

        

        
            
    


