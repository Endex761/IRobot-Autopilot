from typing import Counter
from Utils import DistanceSensors, PositionSensors
from Utils import Logger, Status
import math

logger = Logger()
logger.DEBUG_ENABLED = True # False

try:
    from vehicle import Driver
except ImportError:
    logger.error("Cannot find vehicle. Make sure you run this inside Webots.")
    exit(1)

# constants 
MAX_SPEED = 1.8
MAX_ANGLE = 0.52 # rads ~ 30°
LEFT = -1
RIGHT = 1

# vehicle dimensions in meters
WHEEL_RADIUS = 0.020
LENGTH = 0.180
WIDTH = 0.098
HEIGHT = 0.061


class Altino:

    def __init__(self):
        # get Driver object from Webots
        self.driver = Driver()

        # set vehicle status
        self.status = Status.INIT
        self.prevStatus = Status.INIT

        # get timestep
        self.timestep = int(self.driver.getBasicTimeStep())

        # set sensor timestep
        self.sensorTimestep = 4 * self.timestep

        # get lights
        self.headLights = self.driver.getLED("headlights")
        self.backLights = self.driver.getLED("backlights")

        # turn on headLights
        # headLights.set(1)

        # get distance sensors
        self.distanceSensors = DistanceSensors()
        self.distanceSensors.frontLeft = self.driver.getDistanceSensor("front_left_sensor")
        self.distanceSensors.frontCenter = self.driver.getDistanceSensor('front_center_sensor')
        self.distanceSensors.frontRight = self.driver.getDistanceSensor('front_right_sensor')

        self.distanceSensors.sideLeft = self.driver.getDistanceSensor('side_left_sensor')
        self.distanceSensors.sideRight = self.driver.getDistanceSensor('side_right_sensor')
        self.distanceSensors.back = self.driver.getDistanceSensor('back_sensor')

        # enable distance sensors
        self.distanceSensors.frontLeft.enable(self.sensorTimestep)
        self.distanceSensors.frontCenter.enable(self.sensorTimestep) 
        self.distanceSensors.frontRight.enable(self.sensorTimestep)

        self.distanceSensors.sideLeft.enable(self.sensorTimestep)
        self.distanceSensors.sideRight.enable(self.sensorTimestep) 
        self.distanceSensors.back.enable(self.sensorTimestep) 

        # get position sensors
        self.positionSensors = PositionSensors()
        self.positionSensors.frontLeft  = self.driver.getPositionSensor('left_front_sensor')
        self.positionSensors.frontRight = self.driver.getPositionSensor('right_front_sensor')
        self.positionSensors.rearLeft   = self.driver.getPositionSensor('left_rear_sensor')
        self.positionSensors.rearRight  = self.driver.getPositionSensor('right_rear_sensor')

        # enable position sensors
        self.positionSensors.frontLeft.enable(self.sensorTimestep)
        self.positionSensors.frontRight.enable(self.sensorTimestep)
        self.positionSensors.rearLeft.enable(self.sensorTimestep)
        self.positionSensors.rearRight.enable(self.sensorTimestep)

        # get and enable keyboard controll
        self.keyboard = self.driver.getKeyboard()
        self.keyboard.enable(self.sensorTimestep)

        # this ensure sensors are correctly initialized
        for i in range(int(self.sensorTimestep/self.timestep) + 1):
            self.driver.step()

        # initial speed and steering angle values
        self.speed = 0.0
        self.angle = 0.0

        # initial wheel length used to calculate how many m the wheels have traveled
        self.leftWheelDistance = 0.0
        self.rightWheelDistance = 0.0
        self.updateDistanceTraveled()

    # update cruising speed
    def setSpeed(self, speed):
        if (speed >= -1 * MAX_SPEED and speed <= MAX_SPEED):
            self.speed = speed
        elif (speed > MAX_SPEED):
            self.speed = MAX_SPEED
        elif (speed > -1 * MAX_SPEED):
            self.speed = -1 * MAX_SPEED
        self.driver.setCruisingSpeed(self.speed)

    # update steering angle
    def setAngle(self, angle):
        # ensure angle stays between -MAX_ANGLE and MAX_ANGLE
        if (angle >= -1 * MAX_ANGLE and angle <= MAX_ANGLE):
            self.angle = angle
        elif (angle > MAX_ANGLE):
            self.angle = MAX_ANGLE
        elif (angle < -1 * MAX_ANGLE):
            self.angle = -1 * MAX_ANGLE
        self.driver.setSteeringAngle(self.angle)

    def setStatus(self, status):
        # check if new status is a valid state.
        if status not in list(map(int, Status)):
            logger.warning("Status: " + str(status) + " is invalid, setting STOP status.")
            self.status = Status.STOP
            return
        
        # backup last status
        self.prevStatus = self.status

        # set new status
        self.status = status

    def avoidObstacle(self):
        threshold = 950
        ds = self.distanceSensors
        fl = ds.frontLeft.getValue()
        fc = ds.frontCenter.getValue()
        fr = ds.frontRight.getValue()

        rear = ds.back.getValue()

        if fl > threshold or fc > threshold or fr > threshold:
            return True
        
        if rear > threshold:
            return True
    
    # compute distance traveled by wheels in meters
    def updateDistanceTraveled(self):
        # get position sensors
        ps = self.positionSensors

        # get radiants from wheel
        radFLW = ps.frontLeft.getValue()
        radFRW = ps.frontRight.getValue()

        # compute distance traveled
        self.leftWheelDistance = radFLW * WHEEL_RADIUS
        self.rightWheelDistance = radFRW * WHEEL_RADIUS

        # logger.debug("Distance Updated - Left Wheel Length: " + str(self.leftWheelLength) + " m")
    
    # check keyboard pressed keys and change status
    def keyboardCommands(self):

        currentKey = self.keyboard.getKey()

        if currentKey == ord('p') or currentKey == ord('P'):
            logger.info("Looking for a parking lot")
            self.setStatus( Status.SEARCHING_PARK)
            return

    # running
    def run(self):
        logger.info("Running..")
        leftIsEmpty = False  # flag used to detect left parking lot
        rightIsEmpty = False # flag used to detect right parking lot
        leftStartingPosition = 0.0  # length of the left parking lot
        rightStartingPosition = 0.0 # length of the right parking lot
        sideOfParkingLot = 0 # indicates the side of the parking lot found: -1 left, 1 right, 0 not found yet

        while self.driver.step() != -1:
            
            ## here goes code that should be executed each step ##

            # update wheels' distance traveled in the current step
            self.updateDistanceTraveled()

            # check keyboard pressed keys and change status
            self.keyboardCommands()

            # stop vehicle if too close to an obstacle
            if self.avoidObstacle():
                self.setStatus(Status.STOP)

            ## here goes code for each STATUS ##
            # INIT STATUS 
            if self.status == Status.INIT:
                logger.debug("INIT status")
                
                # set wheel angle
                self.setAngle(0.0)

                # set starting speed
                self.setSpeed(0.0)

                # set new status
                self.setStatus(Status.FORWARD)

                # skip to next cycle to ensure everything is working fine
                continue

            # FORWARD STATUS
            if self.status == Status.FORWARD:
                # logger.debug("FORWARD status")

                # set cruise speed 
                self.setSpeed(0.2)
                
                ds = self.distanceSensors

                frontLeftSensor = ds.frontLeft.getValue()
                frontRightSensor = ds.frontRight.getValue()
                sideLeftSensor = ds.sideLeft.getValue()
                sideRightSensor = ds.sideRight.getValue()

                frontThreshold = 200
                tolerance = 10
                sideThreshold = 950
                if frontLeftSensor > frontThreshold and frontLeftSensor > frontRightSensor + tolerance:
                    self.setAngle(RIGHT * frontLeftSensor / 1000.0 * MAX_ANGLE)
                    logger.debug("Steering angle: " + str(RIGHT * frontLeftSensor / 1000.0 * MAX_ANGLE))

                elif frontRightSensor > frontThreshold and frontRightSensor > frontLeftSensor + tolerance:
                    self.setAngle(LEFT * frontRightSensor / 1000.0 * MAX_ANGLE)
                    logger.debug("Steering angle: " + str(LEFT * frontRightSensor / 1000.0 * MAX_ANGLE))

                elif sideLeftSensor > sideThreshold:
                    self.setAngle(RIGHT * sideLeftSensor / 4000.0 * MAX_ANGLE)

                elif sideRightSensor > sideThreshold:
                    self.setAngle(LEFT * sideRightSensor / 4000.0 * MAX_ANGLE)

                else:
                    self.setAngle(0.0)

            
            # SEARCHING_PARK STATUS
            if self.status == Status.SEARCHING_PARK:
 
                ds = self.distanceSensors
                ps = self.positionSensors

                #log info for debug
                logger.debug("Left Distance Sensor: " + str(ds.sideLeft.getValue()))
                logger.debug("Left Position Sensor: " + str(ps.frontLeft.getValue()) + " rad")
                logger.debug("Left Wheel Length: " + str(self.leftWheelDistance) + " m")
                logger.debug("Starting position: " + str(leftStartingPosition) + " m")
                logger.debug("Parking Lot Length: " + str(self.leftWheelDistance - leftStartingPosition) + " m")

                frontThreshold = 650
                leftSensorValue = ds.sideLeft.getValue()
                rightSensorValue = ds.sideRight.getValue()
                
                # checking parking lot on the LEFT side
                if leftSensorValue < frontThreshold and not leftIsEmpty:
                    leftIsEmpty = True
                    leftStartingPosition = self.leftWheelDistance
                
                elif leftSensorValue > frontThreshold and leftIsEmpty:
                    leftIsEmpty = False

                elif leftIsEmpty and self.leftWheelDistance - leftStartingPosition > LENGTH + LENGTH/3:
                    leftStartingPosition = self.leftWheelDistance
                    sideOfParkingLot = LEFT
                    self.setStatus(Status.FORWARD2)

                # checking parking lot on the RIGHT side
                if rightSensorValue < frontThreshold and not rightIsEmpty:
                    rightIsEmpty = True
                    rightStartingPosition = self.rightWheelDistance
                
                elif rightSensorValue > frontThreshold and rightIsEmpty:
                    rightIsEmpty = False

                elif rightIsEmpty and self.rightWheelDistance - rightStartingPosition > LENGTH + LENGTH/3:
                    rightStartingPosition = self.rightWheelDistance
                    sideOfParkingLot = RIGHT
                    self.setStatus(Status.FORWARD2)

            # this ensure that the parking manoeuvre starts after going forward and not as soon as the parking lot is detected
            if self.status == Status.FORWARD2:
                distance = 0.13
                if sideOfParkingLot == LEFT:
                    if self.leftWheelDistance - leftStartingPosition > distance:
                        self.status = Status.PARKING
                elif sideOfParkingLot == RIGHT:
                    if self.rightWheelDistance - rightStartingPosition > distance:
                        self.status = Status.PARKING
                else:
                    logger.warning("Parking lot not found! I don't know if right or left.")
                    self.setStatus(Status.SEARCHING_PARK)

            # starting the parking manoeuvre
            if self.status == Status.PARKING:
                if sideOfParkingLot != LEFT and sideOfParkingLot != RIGHT:
                    logger.error("side of parking lot unknown.")
                    exit(1)
                
                # stop the vehicle, turn the wheels and go back
                self.setSpeed(0.0)
                self.setAngle(sideOfParkingLot * MAX_ANGLE)
                self.setSpeed(-0.1)

                # when should it turn the other way
                frontThreshold = 600
                ds = self.distanceSensors
                rear = ds.back.getValue()

                if rear > frontThreshold:
                    self.status = Status.PARKING2

            if self.status == Status.PARKING2:
                self.setAngle(-1 * sideOfParkingLot * MAX_ANGLE)

            if self.status == Status.STOP:
                self.setSpeed(0.0)
                self.setAngle(0.0)

                # if obstacle is cleared go forward
                if not self.avoidObstacle() and self.prevStatus == Status.PARKING2:
                    self.status = Status.FORWARD