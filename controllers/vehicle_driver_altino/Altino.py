# import Driver from Webots
from CollisionAvoidance import CollissionAvoidance
from Utils import Position
from vehicle import Driver
from Devices import Actuators, Compass, DistanceSensors, PositionSensors
from LineFollower import LineFollower
from Positioning import Positioning
from PathPlanner import PathPlanner
from PathRunner import PathRunner
from Motion import Motion

altino = Driver()


actuators = Actuators(altino)

distanceSensors = DistanceSensors(altino)
positionSensors = PositionSensors(altino)

compass = Compass(altino)

camera = altino.getDevice('camera')
camera.enable(int(2 * altino.getBasicTimeStep())) #fix

# this ensure sensors are correctly initialized
for i in range(int(altino.getBasicTimeStep() * 2/altino.getBasicTimeStep()) + 1): # fix
    altino.step()

collisionAvoidance = CollissionAvoidance(distanceSensors)

# each of this class must have and update method
lineFollower = LineFollower(camera)


positioning = Positioning(positionSensors, compass, lineFollower)


pathPlanner = PathPlanner(positioning)


pathRunner = PathRunner(positioning, pathPlanner, lineFollower, collisionAvoidance)

pathRunner.goTo(Position(14, 23))

motion = Motion(actuators, pathRunner)

# run
def run():
    while altino.step() != -1:
        collisionAvoidance.update()
        lineFollower.update()
        positioning.update()
        pathPlanner.update()
        pathRunner.update()
        motion.update()

# sistemare landmark






"""from Odometry import Odometry
from Utils import DistanceSensors, Position, PositionSensors
from Utils import logger, Status, DEBUG
from LineFollower import LineFollower, UNKNOWN
from Navigation import PathPlanner, NORD, EAST, SOUTH, WEST, LEFT, RIGHT, FORWARD

try:
    from vehicle import Driver
except ImportError:
    logger.error("Cannot find vehicle. Make sure you run this inside Webots.")
    exit(1)

# constants 
MAX_SPEED = 1.8
MAX_ANGLE = 0.52 # rads ~ 30°
# LEFT = -1
# RIGHT = 1
UNKNOWN = -2

# vehicle dimensions in meters
WHEEL_RADIUS = 0.020
LENGTH = 0.180
WIDTH = 0.098
HEIGHT = 0.061

class Altino:

    def __init__(self):
        # initialize devices
        self.initializeDevices()

        # initial speed and steering angle values
        self.speed = 0.0
        self.angle = 0.0

        # initial wheel length used to calculate how many m the wheels have traveled
        self.leftWheelDistance = 0.0
        self.rightWheelDistance = 0.0
        self.updateDistanceTraveled()

        # line forwared
        self.lineFollower = LineFollower(self.camera)

        # navigation
        self.nav = PathPlanner()
        self.nav.setRobotPosition(Position(4, 1))
        self.nav.setGoalPosition(Position(14, 23))
        self.nav.setRobotOrientation(SOUTH)
        self.nav.printStatus()

        # compute fastest route from robot to goal
        self.turns = self.nav.getFastestRoute()
        logger.debug("turns: " + str(self.turns))

        # odometry
        self.odometry = Odometry(self.positionSensors, self.compass, self.nav.getRobotPosition(), self.nav.getRobotOrientation())

    # running
    def run(self):
        logger.info("Running..")
        leftIsEmpty = False  # flag used to detect left parking lot
        rightIsEmpty = False # flag used to detect right parking lot
        leftStartingPosition = 0.0  # length of the left parking lot
        rightStartingPosition = 0.0 # length of the right parking lot
        sideOfParkingLot = 0 # indicates the side of the parking lot found: -1 left, 1 right, 0 not found yet
        actualTurn = 0

        while self.driver.step() != -1:
            
            ## here goes code that should be executed each step ##

            # get actual compass value
            #compassValues = self.compass.getValues()
            #logger.debug("COMPASS: " + str(compassValues))

            # update wheels' distance traveled in the current step
            self.updateDistanceTraveled()

            self.odometry.update()

            self.odometry.updatePosition()

            # stop vehicle if too close to an obstacle, disable if in manual
            if self.avoidObstacle() and self.status != Status.MANUAL and False:
                self.setStatus(Status.STOP)
                
            # check keyboard pressed keys and change status
            currentKey = self.keyboardCommands()

            ## here goes code for each STATUS ##
            # INIT STATUS 
            if self.status == Status.INIT:
                logger.debug("INIT status")
                
                # set wheel angle
                self.setAngle(0.0)

                # set starting speed
                self.setSpeed(0.5)

                # set new status
                self.setStatus(Status.TURN)

                # skip to next cycle to ensure everything is working fine
                continue
            
            # FOLLOW LINE STATUS
            if self.status == Status.FOLLOW_LINE:

                # set cruise speed
                self.setSpeed(0.5)

                # compute new angle
                newAngle = self.lineFollower.getNewSteeringAngle()

                # logger.debug("new steering angle: " + str(newAngle))

                # set new steering angle
                if newAngle != UNKNOWN:
                    self.setAngle(newAngle)
                else:
                    self.setStatus(Status.TURN)

            # TURN STATUS
            if self.status == Status.TURN:
                if actualTurn < len(self.turns):
                    turn = self.turns[actualTurn]
                    self.setAngle(0.5 * turn * MAX_ANGLE)
                else:
                    self.setStatus(Status.STOP)

                # compute new angle
                newAngle = self.lineFollower.getNewSteeringAngle()

                # if line is found
                if newAngle != UNKNOWN:
                    self.setStatus(Status.FOLLOW_LINE)
                    actualTurn += 1
                    continue
                
            # FORWARD STATUS
            if self.status == Status.FORWARD:
                # logger.debug("FORWARD status")

                # set cruise speed 
                self.setSpeed(0.2)

                # avoing obstacles
                ds = self.distanceSensors

                # get distance sensors values
                frontLeftSensor = ds.frontLeft.getValue()
                frontRightSensor = ds.frontRight.getValue()
                sideLeftSensor = ds.sideLeft.getValue()
                sideRightSensor = ds.sideRight.getValue()

                # set values of thresholds
                tolerance = 10
                sideThreshold = 950

                # check if front left obstacle, turn right
                if frontLeftSensor > frontRightSensor + tolerance:
                    self.setAngle(RIGHT * frontLeftSensor / 500.0 * MAX_ANGLE)
                    # logger.debug("Steering angle: " + str(RIGHT * frontLeftSensor / 1000.0 * MAX_ANGLE))
                    logger.debug("Steering angle: " + str(self.angle))

                # check if front right obstacle, turn left
                elif frontRightSensor > frontLeftSensor + tolerance:
                    self.setAngle(LEFT * frontRightSensor / 500.0 * MAX_ANGLE)
                    # logger.debug("Steering angle: " + str(LEFT * frontRightSensor / 1000.0 * MAX_ANGLE))
                    logger.debug("Steering angle: " + str(self.angle))

                # check if side left obstacle, turn slight right
                elif sideLeftSensor > sideThreshold:
                    self.setAngle(RIGHT * sideLeftSensor / 4000.0 * MAX_ANGLE)

                # check if side right obstacle, turn slight left
                elif sideRightSensor > sideThreshold:
                    self.setAngle(LEFT * sideRightSensor / 4000.0 * MAX_ANGLE)

                # if no obstacle go straight
                else:
                    self.setAngle(self.angle / 1.5)
            
            # SEARCHING_PARK STATUS
            if self.status == Status.SEARCHING_PARK:

                # set slow speed 
                self.setSpeed(0.2)

                # set straight wheels
                self.setAngle(0.0)

                # get distance and position sensors
                ds = self.distanceSensors
                ps = self.positionSensors

                #log info for debug
                logger.debug("Left Distance Sensor: " + str(ds.sideLeft.getValue()))
                logger.debug("Left Position Sensor: " + str(ps.frontLeft.getValue()) + " rad")
                logger.debug("Left Wheel Length: " + str(self.leftWheelDistance) + " m")
                logger.debug("Starting position: " + str(leftStartingPosition) + " m")
                logger.debug("Parking Lot Length: " + str(self.leftWheelDistance - leftStartingPosition) + " m")

                sideThreshold = 650
                leftSensorValue = ds.sideLeft.getValue()
                rightSensorValue = ds.sideRight.getValue()
                
                # checking parking lot on the LEFT side
                if leftSensorValue < sideThreshold and not leftIsEmpty:
                    leftIsEmpty = True
                    leftStartingPosition = self.leftWheelDistance # 100
                
                elif leftSensorValue > sideThreshold and leftIsEmpty:
                    leftIsEmpty = False

                elif leftIsEmpty and self.leftWheelDistance - leftStartingPosition > LENGTH + LENGTH/3:
                    leftStartingPosition = self.leftWheelDistance # 200 - 100 
                    sideOfParkingLot = LEFT
                    self.setStatus(Status.FORWARD2)

                # checking parking lot on the RIGHT side
                if rightSensorValue < sideThreshold and not rightIsEmpty:
                    rightIsEmpty = True
                    rightStartingPosition = self.rightWheelDistance
                
                elif rightSensorValue > sideThreshold and rightIsEmpty:
                    rightIsEmpty = False

                elif rightIsEmpty and self.rightWheelDistance - rightStartingPosition > LENGTH + LENGTH/3:
                    rightStartingPosition = self.rightWheelDistance
                    sideOfParkingLot = RIGHT
                    self.setStatus(Status.FORWARD2)

            # this ensure that the parking manoeuvre starts after going forward and not as soon as the parking lot is detected
            if self.status == Status.FORWARD2:
                distance = 0.19
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
                backThreshold = 400
                ds = self.distanceSensors
                rear = ds.back.getValue()

                logger.debug("Back sensor: " + str(rear))

                if rear > backThreshold:
                    self.status = Status.PARKING2

            if self.status == Status.PARKING2:
                self.setAngle(-1 * sideOfParkingLot * MAX_ANGLE)

                threshold = 945
                rear = self.distanceSensors.back.getValue()
                if rear > threshold:
                    self.setStatus(Status.CENTER)

            if self.status == Status.CENTER:
                
                self.setAngle(0.0)
                self.setSpeed(0.2)

                rear = self.distanceSensors.back.getValue()
                front = self.distanceSensors.frontCenter.getValue()

                if rear - front < 20:
                    self.setStatus(Status.STOP)
                
            if self.status == Status.STOP:
                self.setSpeed(0.0)
                self.setAngle(0.0)

                # if obstacle is cleared go forward
                if not self.avoidObstacle() and self.prevStatus == Status.PARKING2:
                    self.setStatus(Status.FORWARD)

            if self.status == Status.MANUAL:
                # get current state
                speed = self.speed
                angle = self.angle
                # logger.debug("Current Key: " + str(currentKey))

                # keyboard controlls 
                # accelerate
                if currentKey == self.keyboard.UP:
                    if speed < 0:
                        speed += 0.02
                    else:
                        speed += 0.008
                
                # break
                elif currentKey == self.keyboard.DOWN:
                    if speed > 0:
                        speed -= 0.02
                    else:
                        speed -= 0.008
                
                # turn left
                elif currentKey == self.keyboard.LEFT:
                    angle -= 0.01

                # turn right
                elif currentKey == self.keyboard.RIGHT:
                    angle += 0.01
                
                # handbreak
                elif currentKey == ord(' '):
                    speed /= 4
                
                # update state
                self.setSpeed(speed)
                self.setAngle(angle)
    
    # initialize Altino devices 
    def initializeDevices(self):
        # get Driver object from Webots
        self.driver = Driver()

        # set vehicle status
        self.status = Status.INIT
        self.prevStatus = Status.INIT

        # get timestep
        self.timestep = int(self.driver.getBasicTimeStep())

        # set sensor timestep
        self.sensorTimestep = 2 * self.timestep

        # get lights
        self.headLights = self.driver.getDevice("headlights")
        self.backLights = self.driver.getDevice("backlights")

        # turn on headLights
        # headLights.set(1)

        # get and enable camera
        self.camera = self.driver.getDevice("camera")
        self.camera.enable(self.sensorTimestep)

        

        

        

        # get and enable compass
        self.compass = self.driver.getDevice('compass')
        self.compass.enable(self.sensorTimestep)


        # get and enable keyboard controll
        self.keyboard = self.driver.getKeyboard()
        self.keyboard.enable(self.sensorTimestep)

        # this ensure sensors are correctly initialized
        for i in range(int(self.sensorTimestep/self.timestep) + 1):
            self.driver.step()
    
   

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

    # check if vehicle is too close to an obstacle
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
        
        # get current key
        currentKey = self.keyboard.getKey()

        if DEBUG and (currentKey == ord('s') or currentKey == ord('S')):
            logger.debug("Current status: " + str(self.status))

        # press P to find parking lot
        if currentKey == ord('p') or currentKey == ord('P'):
            logger.info("Looking for a parking lot")
            self.setStatus(Status.SEARCHING_PARK)
        
        # press M to manual control
        elif currentKey == ord('m') or currentKey == ord('M'):
            logger.info("Manual")
            self.setStatus(Status.MANUAL)

        # press A to auto control
        elif currentKey == ord('a') or currentKey == ord('A'):
            logger.info("Auto")
            self.setStatus(Status.FORWARD)

        # return current key to allow other controls 
        return currentKey
"""