from Utils import Status, logger
from Constants import LEFT, RIGHT, CAR_LENGTH, UNKNOWN

# parking states
DISABLED = 1
SEARCH = 2
FORWARD = 3
PARKING = 4
PARKING2 = 5
CENTER = 6
STOP = 7

class Parking:

    def __init__(self, distanceSensors, positioning):
        self.distanceSensors = distanceSensors
        self.positioning = positioning

        self.status = DISABLED

        self.angle = 0.0
        self.speed = 0.0

        # working set variables
        self.leftIsEmpty = False
        self.rightIsEmpty = False
        self.leftStartingPosition = 0.0  # start point of the left parking lot
        self.rightStartingPosition = 0.0 # start point of the right parking lot
        self.sideOfParking = UNKNOWN

    def update(self):
        if self.status != DISABLED:
            self.computeParkingAngleAndSpeed()
    
    def isEnabled(self):
        return self.status != DISABLED

    def enable(self):
        self.status = SEARCH

    def disable(self):
        self.status = DISABLED

    def isParking(self):
        return self.status == PARKING or self.status == PARKING2

    def getSpeed(self):
        return self.speed

    def getAngle(self):
        return self.angle

    def computeParkingAngleAndSpeed(self):
        
        logger.debug("PARKING STATE: " + str(self.status))
        # get distance sensors
        ds = self.distanceSensors

        distanceTraveled = self.positioning.getActualDistance()

        if self.status == SEARCH:

            # set slow speed 
            self.speed = 0.2

            # set straight wheels
            self.angle = 0.0

            #log info for debug
            logger.debug("Left Distance Sensor: " + str(ds.sideLeft.getValue()))
            #logger.debug("Left Wheel CAR_LENGTH: " + str(distanceTraveled) + " m")
            #logger.debug("Starting position: " + str(self.leftStartingPosition) + " m")
            logger.debug("Parking Lot CAR_LENGTH: " + str(distanceTraveled - self.leftStartingPosition) + " m")

            sideThreshold = 650
            leftSensorValue = ds.sideLeft.getValue()
            rightSensorValue = ds.sideRight.getValue()
            
            # checking parking lot on the LEFT side
            if leftSensorValue < sideThreshold and not self.leftIsEmpty:
                self.leftIsEmpty = True
                self.leftStartingPosition = distanceTraveled # 100
            
            elif leftSensorValue > sideThreshold and self.leftIsEmpty:
                self.leftIsEmpty = False

            elif self.leftIsEmpty and distanceTraveled - self.leftStartingPosition > CAR_LENGTH + CAR_LENGTH/3:
                self.leftStartingPosition = distanceTraveled # 200 - 100 
                self.sideOfParkingLot = LEFT
                self.status = FORWARD

            # checking parking lot on the RIGHT side
            if rightSensorValue < sideThreshold and not self.rightIsEmpty:
                self.rightIsEmpty = True
                self.rightStartingPosition = distanceTraveled
            
            elif rightSensorValue > sideThreshold and self.rightIsEmpty:
                self.rightIsEmpty = False

            elif self.rightIsEmpty and distanceTraveled - self.rightStartingPosition > CAR_LENGTH + CAR_LENGTH/3:
                self.rightStartingPosition = distanceTraveled
                self.sideOfParkingLot = RIGHT
                self.status = FORWARD

        # this ensure that the parking manoeuvre starts after going forward and not as soon as the parking lot is detected
        elif self.status == FORWARD:
            distance = 0.19
            if self.sideOfParkingLot == LEFT:
                if distanceTraveled - self.leftStartingPosition > distance:
                    self.status = PARKING
            elif self.sideOfParkingLot == RIGHT:
                if distanceTraveled - self.rightStartingPosition > distance:
                    self.status = PARKING
            else:
                logger.warning("Parking lot not found! I don't know if right or left.")
                self.status = SEARCH

        # starting the parking manoeuvre
        elif self.status == PARKING:
            if self.sideOfParkingLot != LEFT and self.sideOfParkingLot != RIGHT:
                logger.error("side of parking lot unknown.")
            
            # stop the vehicle, turn the wheels and go backCenter
            self.speed = 0.0
            self.angle = self.sideOfParkingLot
            self.speed = -0.1

            # when should it turn the other way
            backCenterThreshold = 400
            ds = self.distanceSensors
            rear = ds.backCenter.getValue()

            logger.debug("backCenter sensor: " + str(rear))

            if rear > backCenterThreshold:
                self.status = PARKING2

        elif self.status == PARKING2:
            self.angle = -1 * self.sideOfParkingLot

            threshold = 945
            rear = self.distanceSensors.backCenter.getValue()
            if rear > threshold:
                self.status = CENTER

        elif self.status == CENTER:
            
            self.angle = 0.0
            self.speed = 0.2

            rear = self.distanceSensors.backCenter.getValue()
            front = self.distanceSensors.frontCenter.getValue()

            if rear - front < 20:
                self.status = STOP
            
        elif self.status == STOP:
            self.speed = 0.0
            self.angle = 0.0

            # if obstacle is cleared go forward
            #if not self.avoidObstacle() and self.prevStatus == PARKING2:
                #self.status = FORWARD

        else:
            logger.warning("Invalid parcking status")

        
    

