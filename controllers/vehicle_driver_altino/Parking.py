from Utils import Status, logger
from Constants import LEFT, RIGHT, CAR_LENGTH, UNKNOWN

# parking states
DISABLED = 1        # parking serivice is disabled
SEARCH = 2          # parking serivice is active and in looking for a parking lot
FORWARD = 3         # parking lot found and going a little bit forward to start the maneuver
PARKING = 4         # parking maneuver one: go back and steer
PARKING2 = 5        # parking maneuver two: go back and countersteer
ADJUST_POSITION = 6 # during reverse countersteer found ostacle rear before be in good orientation
CENTER = 7          # park is complete, now center the car between the front and back one
STOP = 8            # car is parked

# class to handle parking service
class Parking:

    # initialize parking serivice
    def __init__(self, distanceSensors, positioning, lineFollower):
        # get distance sensors and positioning serivice
        self.distanceSensors = distanceSensors
        self.positioning = positioning
        self.lineFollower = lineFollower

        # set initial status
        self.status = DISABLED

        # set initial angle and speed
        self.angle = 0.0    # parking angle
        self.speed = 0.0    # parking speed

        # working set variables
        self.leftIsEmpty = False         # tells if left side is available for parking
        self.rightIsEmpty = False        # tells if right side is available for parking
        self.leftStartingPosition = 0.0  # start point of the left parking lot
        self.rightStartingPosition = 0.0 # start point of the right parking lot
        self.sideOfParkingLot = UNKNOWN     # tells the side of the parking lot found

    # update parking service
    def update(self):
        if self.status != DISABLED:
            self.computeParkingAngleAndSpeed()
    
    # return if parking service is enabled
    def isEnabled(self):
        return self.status != DISABLED

    # enable parking serivice
    def enable(self):
        self.status = SEARCH

    # disable parking service
    def disable(self):
        self.status = DISABLED

    # return if the car is parking
    def isParking(self):
        return self.status == PARKING or self.status == PARKING2 or self.status == CENTER

    # return if the car is parked
    def isParked(self):
        return self.status == STOP

    def isSearchingPark(self):
        return self.status == SEARCH

    # return parking speed
    def getSpeed(self):
        return self.speed

    # return parking angle
    def getAngle(self):
        return self.angle

    # compute parking and speed angle
    def computeParkingAngleAndSpeed(self):
        
        logger.debug("PARKING STATE: " + str(self.status))

        # get distance sensors
        ds = self.distanceSensors

        # set reference
        distanceTraveled = self.positioning.getActualDistance()

        side = 0
        front = 0
        rear = 0
        bside = 0
        fside = 0

        if self.status > SEARCH and self.sideOfParkingLot != UNKNOWN:
            # get rear and side sensors values
            rear = self.distanceSensors.backCenter.getValue()
            front = self.distanceSensors.frontCenter.getValue()
            
            if self.sideOfParkingLot == RIGHT:
                side = self.distanceSensors.sideRight.getValue()
                bside = self.distanceSensors.backRight.getValue()
                fside = self.distanceSensors.frontRight.getValue()
            elif self.sideOfParkingLot == LEFT:
                side = self.distanceSensors.sideLeft.getValue()
                bside = self.distanceSensors.backLeft.getValue()
                fside = self.distanceSensors.frontLeft.getValue()

        # SEARCH status 2
        if self.status == SEARCH:

            # set slow speed 
            self.speed = 0.2

            # set straight wheels
            self.angle = self.lineFollower.getNewSteeringAngle()

            if self.lineFollower.isLineLost():
                self.resetParkingPosition() 
                self.angle = self.lineFollower.getSteeringAngleLineSearching()

            logger.debug("PARKING angle from Line Follower: " + str(self.angle))
            if abs(self.angle) > 0.25:
                self.resetParkingPosition() 

            # side threshold, if side sensor is greather than threshold the parking lot if occupied
            sideThreshold = 650

            # get side left sensors values
            leftSensorValue = ds.sideLeft.getValue()
            rightSensorValue = ds.sideRight.getValue()
            
            # checking parking lot on the LEFT side
            if leftSensorValue < sideThreshold and not self.leftIsEmpty:
                self.leftIsEmpty = True
                self.leftStartingPosition = distanceTraveled
            
            elif leftSensorValue > sideThreshold and self.leftIsEmpty:
                self.leftIsEmpty = False

            elif self.leftIsEmpty and distanceTraveled - self.leftStartingPosition > CAR_LENGTH + (CAR_LENGTH*2/3):
                self.leftStartingPosition = distanceTraveled
                self.sideOfParkingLot = LEFT
                self.status = FORWARD

            # checking parking lot on the RIGHT side
            if rightSensorValue < sideThreshold and not self.rightIsEmpty:
                self.rightIsEmpty = True
                self.rightStartingPosition = distanceTraveled
            
            elif rightSensorValue > sideThreshold and self.rightIsEmpty:
                self.rightIsEmpty = False

            elif self.rightIsEmpty and distanceTraveled - self.rightStartingPosition > CAR_LENGTH + (CAR_LENGTH*2/3):
                self.rightStartingPosition = distanceTraveled
                self.sideOfParkingLot = RIGHT
                self.status = FORWARD

        # FORWARD status 3
        # this ensure that the parking manoeuvre starts after going forward and not as soon as the parking lot is detected
        elif self.status == FORWARD:
            # distance to travel before starting the maneuver
            distance = 0.12
            
            # check if distance traveled is greater than distance to travel
            if self.sideOfParkingLot == LEFT:
                if distanceTraveled - self.leftStartingPosition >= distance:
                    self.status = PARKING
            elif self.sideOfParkingLot == RIGHT:
                if distanceTraveled - self.rightStartingPosition >= distance:
                    self.status = PARKING
            else:
                # if parking is found but is not set the side
                logger.warning("Parking lot found! But I don't know if right or left. Looking for anther one.")
                self.status = SEARCH

        # starting the parking manoeuvre 4
        elif self.status == PARKING:
            # check is the side of the parking lot is known
            if self.sideOfParkingLot != LEFT and self.sideOfParkingLot != RIGHT:
                logger.error("Side of parking lot is unknown.")
            
            # stop the vehicle, turn the wheels and go back slowly
            self.angle = self.sideOfParkingLot
            self.speed = -0.1

            # back thresholds that tells when contursteer
            backCenterThreshold = 610
            backSideThreshold = 410
            if self.sideOfParkingLot == LEFT:
                backCenterThreshold = 625
                backSideThreshold = 425

            # debug log
            logger.debug("Rear: " + str(rear) + " Back Park Side: " + str(bside))

            # if true countersteer
            if bside > backSideThreshold or rear > backCenterThreshold:
                self.status = PARKING2

        # PARKING2 status 5
        elif self.status == PARKING2:
            # set countersteering angle
            if self.angle != 0:
                self.angle = -1 * self.sideOfParkingLot
            self.speed = -0.05

            # set side and back threshold
            rearThreshold = 985
            sideThreshold = 945
            backSideThreshold = 915

            # debug log
            logger.debug("sideOfParkingLot: " + str(self.sideOfParkingLot) + " side: " + str(side))

            # check if the park is completed
            if (bside <= fside and side >= 865):
                self.status = CENTER
            
            # check if need some orient adjust
            if self.distanceSensors.backDistance(sideThreshold): #and bside > fside:
                self.status = ADJUST_POSITION

        # ADJUST_POSITION status 6
        elif self.status == ADJUST_POSITION:
            # debug log
            logger.debug("Need to adjust position")

            # set angle
            self.angle = self.sideOfParkingLot
            self.speed = 0.05

            # check if the park is completed
            if (bside < fside and side > 865):
                self.status = CENTER
            
            if front > 925 or fside > 925 or not self.distanceSensors.backDistance(825):
                self.angle = -1 * self.sideOfParkingLot
                self.status = PARKING2

        # CENTER status 7
        elif self.status == CENTER:            
            if rear > 950 or ( rear < 100 and front < 700):
                self.speed = 0.05
            elif front > 950 or ( front < 100 and rear < 700):
                self.speed = -0.05
            
            # set angle streight
            if abs(bside - fside) < 50 and abs(rear - front) < 80:
                self.angle = 0.0
                self.status = STOP
                logger.debug("TRYING TO STAY CENTER: same distance sides and rear and front!")

            elif abs(bside - fside) < 50 and rear < 100 and front > 700:
                self.angle = 0.0
                self.status = STOP
                logger.debug("TRYING TO STAY CENTER: there's nothing behind, stay ahead!")

            elif abs(bside - fside) < 50 and rear < 100 and front > 700:
                self.angle = 0.0
                self.status = STOP
                logger.debug("TRYING TO STAY CENTER: there's nothing behind, stay ahead!")
                
            elif abs(bside - fside) < 50 and front < 100 and rear > 700:
                self.angle = 0.0
                self.status = STOP
                logger.debug("TRYING TO STAY CENTER: there's nothing ahead, stay behind!")

            elif abs(bside - fside) < 20:
                self.angle = 0.0
                logger.debug("TRYING TO STAY CENTER: same distance sides!")
            else:
                if self.speed > 0:
                    nextAngle = 0.2
                else:
                    nextAngle = -0.2

                if fside < bside:
                    nextAngle *= self.sideOfParkingLot
                else:
                    nextAngle *= -self.sideOfParkingLot
                self.angle = nextAngle
                logger.debug("TRYING TO STAY CENTER: NEED TO GO " + ("right" if self.angle > 0 else "left"))

        # STOP status 8
        elif self.status == STOP:
            self.speed = 0.0
            self.angle = 0.0

        # invalid status
        else:
            logger.debug("Invalid parcking status")

    def resetParkingPosition(self):
        self.leftIsEmpty = False
        self.rightIsEmpty = False
    

