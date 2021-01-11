from Utils import Orientation, Position, logger
import Map

WHEEL_RADIUS = 0.020

class Positioning:

    def __init__(self, positionSensors, compass, lineFollower):
        self.frontLeft = positionSensors.frontLeft
        self.frontRight = positionSensors.frontRight
        self.compass = compass
        self.lineFollower = lineFollower

        self.leftWheelDistance = 0.0
        self.rightWheelDistance = 0.0
        self.reference = self.getActualDistance()

        self.lineAlreadyLost = False

        # HOW? GPS?
        self.position = Position(4,1)
        self.orientation = self.updateOrientation()

    # set robot position in the map
    def setPosition(self, position):
        x = position.getX()
        y = position.getY()
        if x > 0 and x < Map.HEIGHT - 1:
            if y > 0 and y < Map.WIDTH - 1:
                self.position = position
                return
        logger.warning("Invalid Position")
    
    def setOrientation(self, orientation):
        self.orientation = orientation

    def getPosition(self):
        return self.position

    def getOrientation(self):
        return self.orientation

    def printStatus(self):
        logger.info("Positioning: " + str(self.position) + " Orientation: " + str(self.orientation))

    def update(self):
        self.updateWheelTraveledDistance()
        self.updateOrientation()
        self.updatePosition()
        self.computePositionBasedOnLandmark()

    def updateWheelTraveledDistance(self):
        # get radiants from wheel
        radFLW = self.frontLeft.getValue()
        radFRW = self.frontRight.getValue()

        # compute distance traveled
        self.leftWheelDistance = radFLW * WHEEL_RADIUS
        self.rightWheelDistance = radFRW * WHEEL_RADIUS


    def getActualDistance(self):
        return (self.leftWheelDistance + self.rightWheelDistance) / 2.0

    def getInitialDistance(self):
        return (self.initalLeftWheelDistance + self.initalRightWheelDistance) / 2-0

    def updateOrientation(self):
        self.orientation = self.compass.getOrientation()

    # to be improved   
    def computePositionBasedOnLandmark(self):
        isLineLost = self.lineFollower.isLineLost()
        if isLineLost and not self.lineAlreadyLost:
            logger.debug("Should be here once: ilLineLost " + str(isLineLost) + str(self.lineAlreadyLost))
            self.lineAlreadyLost = True
            if Map.getValue(self.position) == Map.I:
                logger.debug("Already in")
            else:
                logger.debug("Current pos to search: " + str(self.position))
                self.position = Map.findNearestIntersection(self.position)
                self.reference = self.getActualDistance()
                logger.debug("new pos: " + str(self.position))
        elif not isLineLost:
            self.lineAlreadyLost = False

        
                
        
    def updatePosition(self):
        tolerance = 0.00
        add = [0,0]
        if self.getActualDistance() - self.reference > Map.MAP_RESOLUTION + tolerance:
            if self.orientation == Orientation.NORD:
                add = [-1, 0]
            elif self.orientation == Orientation.SOUTH:
                add = [1, 0]
            elif self.orientation == Orientation.EAST:
                add = [0, 1]
            elif self.orientation == Orientation.WEST:
                add = [0, -1]
                
            self.printStatus()
            self.reference = self.getActualDistance()

        x = self.position.getX()
        y = self.position.getY()

        self.position.setX(x + add[0])
        self.position.setY(y + add[1])


        
        

        

        
            
    


