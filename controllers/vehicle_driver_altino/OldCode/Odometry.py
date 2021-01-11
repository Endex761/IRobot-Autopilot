from Navigation import EAST, NORD, SOUTH, WEST
from Utils import PositionSensors, Position

WHEEL_RADIUS = 0.020
MAP_STEP = 0.5

class Odometry:
    def __init__(self, positionSensors, compass, initialPosition, initialOrientation):
        self.frontLeft = positionSensors.frontLeft
        self.frontRight = positionSensors.frontRight
        self.compass = compass
        self.leftWheelDistance = 0.0
        self.rightWheelDistance = 0.0
        self.initalLeftWheelDistance = self.frontLeft.getValue()
        self.initalRightWheelDistance = self.frontRight.getValue()


        self.position = initialPosition
        self.orientation = initialOrientation

        self.reference = self.getActualDistance()

    
    def update(self):
        # get radiants from wheel
        radFLW = self.frontLeft.getValue()
        radFRW = self.frontRight.getValue()

        # compute distance traveled
        self.leftWheelDistance = radFLW * WHEEL_RADIUS
        self.rightWheelDistance = radFRW * WHEEL_RADIUS

        self.orientation = self.computeOrientation()



    def getActualDistance(self):
        return (self.leftWheelDistance + self.rightWheelDistance) / 2.0

    def getInitialDistance(self):
        return (self.initalLeftWheelDistance + self.initalRightWheelDistance) / 2-0

    def computeOrientation(self):
        compassData = self.compass.getValues()
        yComponent = compassData[0]
        xComponent = compassData[2]

        newOrientation = self.orientation

        compassThreshold = 0.9
        if xComponent > compassThreshold:
            newOrientation = NORD
        elif xComponent < -compassThreshold:
            newOrientation = SOUTH
        elif yComponent > compassThreshold:
            newOrientation = EAST
        elif yComponent < -compassThreshold:
            newOrientation = WEST

        return newOrientation
        

    def updatePosition(self):
        tolerance = 0.00
        add = [0,0]
        if self.getActualDistance() - self.reference > MAP_STEP + tolerance:
            if self.orientation == NORD:
                add = [-1, 0]
            elif self.orientation == SOUTH:
                add = [1, 0]
            elif self.orientation == EAST:
                add = [0, 1]
            elif self.orientation == WEST:
                add = [0, -1]
            self.reference = self.getActualDistance()
            print("New Position: " + str(self.position) + " Orientation: " + self.orientation)

        x = self.position.getX()
        y = self.position.getY()

        self.position.setX(x + add[0])
        self.position.setY(y + add[1])

        
            
    


