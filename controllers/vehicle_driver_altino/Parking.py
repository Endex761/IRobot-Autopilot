from Utils import Status, logger
from Constants import LEFT, RIGHT, CAR_LENGTH, UNKNOWN

# parking states
DISABLED = 1    # parking serivice is disabled
SEARCH = 2      # parking serivice is active and in looking for a parking lot
FORWARD = 3     # parking lot found and going a little bit forward to start the maneuver
PARKING = 4     # parking maneuver one: go back and steer
PARKING2 = 5    # parking maneuver two: go back and countersteer
CENTER = 6      # park is complete, now center the car between the front and back one
STOP = 7        # car is parked

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
        self.sideOfParking = UNKNOWN     # tells the side of the parking lot found

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

            elif self.leftIsEmpty and distanceTraveled - self.leftStartingPosition > CAR_LENGTH + CAR_LENGTH/3:
                self.leftStartingPosition = distanceTraveled
                self.sideOfParkingLot = LEFT
                self.status = FORWARD

            # checking parking lot on the RIGHT side
            if rightSensorValue < sideThreshold and not self.rightIsEmpty:
                self.rightIsEmpty = True
                self.rightStartingPosition = distanceTraveled
            
            elif rightSensorValue > sideThreshold and self.rightIsEmpty:
                self.rightIsEmpty = False

            elif self.rightIsEmpty and distanceTraveled - self.rightStartingPosition > CAR_LENGTH + (CAR_LENGTH/2):
                self.rightStartingPosition = distanceTraveled
                self.sideOfParkingLot = RIGHT
                self.status = FORWARD

        # FORWARD status 3
        # this ensure that the parking manoeuvre starts after going forward and not as soon as the parking lot is detected
        elif self.status == FORWARD:
            # distance to travel before starting the maneuver
            distance = 0.2

            # check if distance traveled is greater than distance to travel
            if self.sideOfParkingLot == LEFT:
                if distanceTraveled - self.leftStartingPosition > distance:
                    self.status = PARKING
            elif self.sideOfParkingLot == RIGHT:
                if distanceTraveled - self.rightStartingPosition > distance:
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
            # tanto più sono vicino al parcheggio, tanto più alto deve essere il threshold
            backCenterThreshold = 580
            backSideThreshold = 420

            # get back distance sensors values
            ds = self.distanceSensors
            bc = ds.backCenter.getValue()
            bl = ds.backLeft.getValue()
            br = ds.backRight.getValue()    
            sideSensor = 0

            # debug log
            logger.debug("BC: " + str(bc) + " BL: " + str(bl) + " BR: " + str(br))

            # get the side back sensor nearest to the wall
            if self.sideOfParkingLot == RIGHT:
                sideSensor = br
            elif self.sideOfParkingLot == LEFT:
                sideSensor = bl

            # if true countersteer
            if sideSensor > backSideThreshold or bc > backCenterThreshold:
                self.status = PARKING2

        # PARKING2 status 5
        elif self.status == PARKING2:
            # set countersteering angle
            self.angle = -1 * self.sideOfParkingLot
            self.speed = -0.05

            # set side and back threshold
            rearThreshold = 965
            sideThreshold = 945
            
            # get rear and side sensors values
            rear = self.distanceSensors.backCenter.getValue()
            side = 0
            bside = 0
            fside = 0
            if self.sideOfParkingLot == RIGHT:
                side = self.distanceSensors.sideRight.getValue()
                bside = self.distanceSensors.backRight.getValue()
                fside = self.distanceSensors.frontRight.getValue()
            elif self.sideOfParkingLot == LEFT:
                side = self.distanceSensors.sideLeft.getValue()
                bside = self.distanceSensors.backLeft.getValue()
                fside = self.distanceSensors.frontLeft.getValue()

            # debug log
            logger.debug("sideOfParkingLot: " + str(self.sideOfParkingLot) + " side: " + str(side))
            
            # check if the park is completed
            #if side > sideThreshold or rear > rearThreshold or ( abs(bside - fside) < 20 and side > 850):
                #self.status = CENTER

            # check if the park is completed
            if side > sideThreshold or rear > rearThreshold or (bside < fside and side > 850):
                self.status = CENTER

        # CENTER status 6
        elif self.status == CENTER:

            bside = 0
            fside = 0
            if self.sideOfParkingLot == RIGHT:
                bside = self.distanceSensors.backRight.getValue()
                fside = self.distanceSensors.frontRight.getValue()
            elif self.sideOfParkingLot == LEFT:
                bside = self.distanceSensors.backLeft.getValue()
                fside = self.distanceSensors.frontLeft.getValue()                
                
            # get front and back center sensors values
            rear = self.distanceSensors.backCenter.getValue()
            front = self.distanceSensors.frontCenter.getValue()

            
            if rear > 950:
                self.speed = 0.1
            elif front > 950:
                self.speed = -0.1
            
            # set angle streight
            if abs(bside - fside) < 50 and abs(rear - front) < 40:
                self.angle = 0.0
                self.status = STOP
                logger.warning("TRYING TO STAY CENTER: same distance sides and rear and front!")
            elif abs(bside - fside) < 20:
                self.angle = 0.0
                logger.warning("TRYING TO STAY CENTER: same distance sides!")
            else:
                #TODO: left parking miss
                self.angle = self.sideOfParkingLot * 0.2 * (1 if fside > bside else -1)
                self.angle *= (-1 if self.speed > 0 else 1)
                logger.warning("TRYING TO STAY CENTER: not same distance")

            # if the rear and front sensor are the same stop the car else continue the centering manoeuver
            #if abs(rear - front) < 10:
            #    self.status = STOP
            #el

        # STOP status 7
        elif self.status == STOP:
            self.speed = 0.0
            self.angle = 0.0


        # invalid status
        else:
            logger.warning("Invalid parcking status")

    def resetParkingPosition(self):
        self.leftIsEmpty = False
        self.rightIsEmpty = False
    

