import math
from Utils import Orientation, Position, logger
from Constants import CAR_LENGTH, MAX_ANGLE, MAX_SPEED, UNKNOWN
import Map

WHEEL_RADIUS = 0.020
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

        self.radios = 1

        self.lineAlreadyLost = False
        # TODO what if speed is negative 
        # how should i get the starting position? GPS?
        self.position = Position(7.5,9)
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
        logger.debug("Position: " + str(self.position))
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
    
    def getActualSteeringAngle(self):
        return (self.positionSensors.steerRight.getValue() + self.positionSensors.steerLeft.getValue()) / 2.0

    # update orientation using inaccurate compass orientation
    def updateOrientation(self):
        self.orientation = self.compass.getOrientation()
        self.inaccurateOrientation = self.compass.getInaccurateOrientation()

    def computePositionBasedOnLandmark2(self):
        # if the line get lost provably the robot is near an intersecion
        isLineLost = self.lineFollower.isLineLost()
        logger.debug("isLineLost: " + str(isLineLost) + " isLineAlreadyLost: " + str(self.lineAlreadyLost))
        if isLineLost and not self.lineAlreadyLost:
            self.lineAlreadyLost = True
            #if not Map.getValue(self.position) == Map.I:
            #if Map.getNearestWalkablePositionEquals(self.position, self.inaccurateOrientation, Map.I) != -1:
            logger.debug("Im not in a I position: " + str(self.position))
            nearestIntersecion = Map.findNearestIntersection(self.position, self.radios)
            logger.debug("L'intersezione più vicina è: " + str(nearestIntersecion))
            if nearestIntersecion != -1:
                self.reference = self.getActualDistance() - ((Map.MAP_RESOLUTION / 2)) 
                self.radios = 1
            else:
                #self.lineAlreadyLost = False
                logger.debug("Intersection not found")
            

            logger.debug("LINE IS LOST - REFERENCE: " + str(self.reference))
            distance = self.getActualDistance() - self.reference
            logger.debug("DIFFERENCE " + str(distance))

        elif not isLineLost:
            self.lineAlreadyLost = False

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

             # update positioning using map landmarks
    def computePositionBasedOnLandmark1(self):
        # if the line get lost provably the robot is near an intersecion
        isLineLost = self.lineFollower.isLineLost()
        logger.debug("isLineLost: " + str(isLineLost) + " isLineAlreadyLost: " + str(self.lineAlreadyLost))
        if isLineLost and not self.lineAlreadyLost:
            logger.debug("LINE IS LOST - REFERENCE: " + str(self.reference))
            distance = self.getActualDistance() - self.reference
            logger.debug("DIFFERENCE " + str(distance))
            self.lineAlreadyLost = True
            #if not Map.getValue(self.position) == Map.I:
            #if Map.getNearestWalkablePositionEquals(self.position, self.inaccurateOrientation, Map.I) != -1:
            #logger.debug("Im not in a I position: " + str(self.position))
            nearestIntersecion = Map.findNearestIntersection(self.position)
            #logger.debug("L'intersezione più vicina è: " + str(nearestIntersecion))
            if nearestIntersecion != -1:
                self.position = nearestIntersecion
                self.reference = self.getActualDistance() + ((Map.MAP_RESOLUTION / 2))
            else:
                #self.lineAlreadyLost = False
                logger.debug("Intersection not found")
        elif not isLineLost:
            self.lineAlreadyLost = False


    # update position based on odometry        
    def updatePosition1(self):
        logger.debug("COMPASS ANGLE: " + str(self.compass.getAngleFromOrientation()))
        #logger.debug("REFERENCE: " + str(self.reference))
        #logger.debug("ACTUAL DI: " + str(self.getActualDistance()))
        tolerance = 0
        turning = -0.6 * abs(self.getActualSteeringAngle() / MAX_ANGLE)
        if turning > -0.001:
            turning = 0
            tolerance = -0.05
        #logger.debug("ANGLE: " + str(turning))
        add = [0,0]
        if self.getActualDistance() - self.reference > Map.MAP_RESOLUTION + turning + tolerance:
            if self.inaccurateOrientation == Orientation.NORD:
                add = [-1, 0]
            elif self.inaccurateOrientation == Orientation.SOUTH:
                add = [1, 0]
            elif self.inaccurateOrientation == Orientation.EAST:
                add = [0, 1]
            elif self.inaccurateOrientation == Orientation.WEST:
                add = [0, -1]
            else:
                add = [0,0]
                
            #self.printStatus()
            self.reference = self.getActualDistance()

            x = self.position.getX()
            y = self.position.getY()

            newX = x + add[0]
            newY = y + add[1]
            
            newPosition = Position(newX,newY)
            newPosition = Map.getNearestWalkablePosition(newPosition, self.inaccurateOrientation)

            self.setPosition(newPosition)
            
        #if Map.isWalkable(Position(newX, newY)):
        #    self.position.setX(newX)
        #    self.position.setY(newY)


        # update position based on odometry        
    def updatePosition(self):
        logger.debug("COMPASS ANGLE: " + str(self.compass.getAngleFromOrientation()))
        
        speed = self.actuators.getSpeed()

        if speed != 0:
            x = self.position.x
            y = self.position.y

            linearMove = (((speed) * 2 * math.pi * WHEEL_RADIUS) / 25) * 2
            precision = 2
            
            logger.debug("X-COMPONENT: " + str(round(self.compass.getXComponent(), precision)))
            logger.debug("Y-COMPONENT: " + str(round(self.compass.getYComponent(), precision)))
            newX = x - round(self.compass.getXComponent(), precision) * linearMove * 1.5
            newY = y + round(self.compass.getYComponent(), precision) * linearMove * 1.5
        
            newPosition = Position(newX,newY)
            # wp = Map.getNearestWalkablePosition(newPosition, self.inaccurateOrientation)
            # if wp != None:
                # newPosition = wp

            self.setPosition(newPosition)

        

        

        
            
    


