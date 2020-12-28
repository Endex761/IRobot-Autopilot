from vehicle import Driver
import math
from Utils import DistanceSensors, PositionSensors
from Utils import Logger, Status

# constants 
MAX_SPEED = 1.8
MAX_ANGLE = 0.5
PI2 = math.pi * 2

# vehicle dimentions in meters
WHEEL_RADIUS = 0.020
LENGTH = 0.180
WIDTH = 0.098
HEIGHT = 0.061

logger = Logger()
logger.DEBUG_ENABLED = False

class Altino:

    def __init__(self):
        # get Driver object
        self.driver = Driver()

        # set vehicle status
        self.status = Status.INIT

        # get timestep
        self.timestep = int(self.driver.getBasicTimeStep())

        # set sensor timestep
        self.sensorTimestep = 4 * self.timestep

        # get lights
        headLights = self.driver.getLED("headlights")
        backLights = self.driver.getLED("backlights")

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

        # initial speed and steering angle values
        self.speed = 0.0
        self.angle = 0.0

        # initial wheel lenght used to calcule how many m the wheels have traveled
        self.leftWheelLenght = 0.0
        self.rightWheelLenght = 0.0

        # set starting and steering angle to 0
        self.driver.setSteeringAngle(self.speed)
        self.driver.setCruisingSpeed(self.angle)

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
        if (angle >= -1 * MAX_ANGLE and angle <= MAX_ANGLE):
            self.angle = angle
        elif (angle > MAX_ANGLE):
            self.angle = MAX_ANGLE
        elif (angle < -1 * MAX_ANGLE):
            self.angle = -1 * MAX_ANGLE
        self.driver.setSteeringAngle(self.angle)

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
    
    def updateDistanceTraveled(self):
        ps = self.positionSensors
        deltaFLW = ps.frontLeft.getValue()
        deltaFRW = ps.frontRight.getValue()

        self.leftWheelLenght = deltaFLW * WHEEL_RADIUS
        self.rightWheelLenght = deltaFRW * WHEEL_RADIUS

        logger.log("Left Wheel Lenght: " + str(self.leftWheelLenght) + " m", logger.DEBUG)

        
        
    # running
    def run(self):
        logger.log("Running..")
        park = False
        parkLength = 0.0 # lenght of the parking lot
        while self.driver.step() != -1:

            self.updateDistanceTraveled()

            if self.avoidObstacle():
                self.status = Status.STOP

            if self.status == Status.INIT:
                logger.log("INIT status", logger.DEBUG)
                # this ensure distance sensors are correctily created
                for i in range(int(self.sensorTimestep/self.timestep)):
                    self.driver.step()
                
                # set speed going forward
                self.setSpeed(0.2)

                # set new status
                self.status = Status.FORWARD

            if self.status == Status.FORWARD:
                logger.log("FORWARD status", logger.DEBUG)

                self.status = Status.SEARCHING_PARK
            
            if self.status == Status.SEARCHING_PARK:
                ds = self.distanceSensors
                logger.log("Left Distance Sensor: " + str(ds.sideLeft.getValue()), logger.DEBUG)
                ps = self.positionSensors
                logger.log("Left Position Sensor: " + str(ps.frontLeft.getValue()) + " rad", logger.DEBUG)

                threshold = 650
                logger.log("Parking Lot Length: " + str(self.leftWheelLenght - parkLength), logger.DEBUG)
                if ds.sideLeft.getValue() < threshold and not park:
                    park = True
                    parkLength = self.leftWheelLenght

                # park found
                if park == True and ds.sideLeft.getValue() > threshold:
                    if self.leftWheelLenght - parkLength > LENGTH + 0.02:
                        logger.log("Park Found!")
                        logger.log("Start Parking..")
                        parkLength = self.leftWheelLenght
                        
                        self.status = Status.PARKING

            if self.status == Status.PARKING:
                
                self.setSpeed(0.0)
                self.setAngle(-0.5)
                self.setSpeed(-0.1)

                threshold = 600
                ds = self.distanceSensors
                rear = ds.back.getValue()

                if rear > threshold:
                    self.status = Status.PARKING2

            if self.status == Status.PARKING2:
                self.setAngle(0.5)

            if self.status == Status.STOP:
                self.setSpeed(0.0)
                self.setAngle(0.0)
        

    


    
    
