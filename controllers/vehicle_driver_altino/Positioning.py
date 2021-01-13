from Utils import Orientation, Position, logger
from Constants import UNKNOWN
import Map

WHEEL_RADIUS = 0.020
# class for handling postioning service using odometry
class Positioning:

    #initialize positioning service
    def __init__(self, positionSensors, compass, lineFollower):
        self.frontLeft = positionSensors.frontLeft
        self.frontRight = positionSensors.frontRight
        self.compass = compass
        self.lineFollower = lineFollower

        self.leftWheelDistance = 0.0
        self.rightWheelDistance = 0.0
        self.reference = self.getActualDistance()

        self.lineAlreadyLost = False
        # TODO what if speed is negative
        # how should i get the starting position? GPS?
        self.position = Position(4,1)
        self.orientation = UNKNOWN
        self.inaccurateOrientation = UNKNOWN
        self.updateOrientation()

    # set robot position in the map
    def setPosition(self, position):
        x = position.getX()
        y = position.getY()
        if x > 0 and x < Map.HEIGHT - 1:
            if y > 0 and y < Map.WIDTH - 1:
                self.position = position
                return
        logger.warning("Invalid Position")
    
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
        logger.info("Positioning: " + str(self.position) + " Orientation: " + str(self.orientation))

    # update positioning service
    def update(self):
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
        if isLineLost and not self.lineAlreadyLost:
            logger.debug("isLineLost: " + str(isLineLost) + "isLineAlreadyLost: " + str(self.lineAlreadyLost))
            self.lineAlreadyLost = True
            if not Map.getValue(self.position) == Map.I:
                nearestIntersecion = Map.findNearestIntersection(self.position)
                if nearestIntersecion != -1:
                    self.position = nearestIntersecion
                    self.reference = self.getActualDistance()
                else:
                    self.lineAlreadyLost = False
        elif not isLineLost:
            self.lineAlreadyLost = False

    # update position based on odometry        
    def updatePosition(self):
        tolerance = -0.02
        add = [0,0]
        if self.getActualDistance() - self.reference > Map.MAP_RESOLUTION + tolerance:
            if self.inaccurateOrientation == Orientation.NORD:
                add = [-1, 0]
            elif self.inaccurateOrientation == Orientation.SOUTH:
                add = [1, 0]
            elif self.inaccurateOrientation == Orientation.EAST:
                add = [0, 1]
            elif self.inaccurateOrientation == Orientation.WEST:
                add = [0, -1]
                
            self.printStatus()
            self.reference = self.getActualDistance()

        x = self.position.getX()
        y = self.position.getY()

        newX = x + add[0]
        newY = y + add[1]
        logger.debug("New Position: " + str(Position(newX,newY)))
        self.position = Map.getNearestWalkablePosition(Position(newX,newY), self.inaccurateOrientation)
        #if Map.isWalkable(Position(newX, newY)):
        #    self.position.setX(newX)
        #    self.position.setY(newY)


        
        

        

        
            
    


