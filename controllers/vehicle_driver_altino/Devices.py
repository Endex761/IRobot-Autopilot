from Constants import DEVICE_TIMESTEP_MULTIPLIER, MAX_ANGLE, MAX_SPEED, UNKNOWN
from Utils import Orientation, logger

class Actuators:
    def __init__(self, driver):
        #deviceTimestep = driver.getBasicTimeStep() * DEVICE_TIMESTEP_MULTIPLIER

        self.driver = driver
        self.speed = 0.0
        self.angle = 0.0
        self.driver.setSteeringAngle(self.angle)
        self.driver.setCruisingSpeed(self.speed)

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
    
    def getSpeed(self):
        return self.speed

    def getAngle(self):
        return self.angle
        
class Compass:
    def __init__(self, driver):
        deviceTimestep = int(driver.getBasicTimeStep() * DEVICE_TIMESTEP_MULTIPLIER)
        
        self.compass = driver.getDevice('compass')
        self.compass.enable(deviceTimestep)

        self.orientation = UNKNOWN

    def getOrientation(self):
        threshold = 0.95
        return self.computeOrientation(threshold)

    def getInaccurateOrientation(self):
        threshold = 0.5
        return self.computeOrientation(threshold)

    def computeOrientation(self, precision):
        compassData = self.compass.getValues()
        yComponent = compassData[0]
        xComponent = compassData[2]

        newOrientation = self.orientation

        compassThreshold = precision
        if xComponent > compassThreshold:
            newOrientation = Orientation.NORD
        elif xComponent < -compassThreshold:
            newOrientation = Orientation.SOUTH
        elif yComponent > compassThreshold:
            newOrientation = Orientation.EAST
        elif yComponent < -compassThreshold:
            newOrientation = Orientation.WEST

        self.orientation = newOrientation

        return newOrientation
        

class DistanceSensors:

    def __init__(self, driver):
        deviceTimestep = int(driver.getBasicTimeStep() * DEVICE_TIMESTEP_MULTIPLIER)
        # get distance sensors
        self.frontLeft = driver.getDevice('front_left_sensor')
        self.frontCenter = driver.getDevice('front_center_sensor')
        self.frontRight = driver.getDevice('front_right_sensor')

        self.sideLeft = driver.getDevice('side_left_sensor')
        self.sideRight = driver.getDevice('side_right_sensor')

        self.backLeft = driver.getDevice('back_left_sensor')
        self.backCenter = driver.getDevice('back_center_sensor')
        self.backRight = driver.getDevice('back_right_sensor')

        # enable distance sensors
        self.frontLeft.enable(deviceTimestep)
        self.frontCenter.enable(deviceTimestep) 
        self.frontRight.enable(deviceTimestep)

        self.sideLeft.enable(deviceTimestep)
        self.sideRight.enable(deviceTimestep) 

        self.backLeft.enable(deviceTimestep) 
        self.backCenter.enable(deviceTimestep) 
        self.backRight.enable(deviceTimestep) 

    def frontLeftCM(self):
        return (self.frontLeft.getValue() * (-0.06)) + 60

    def frontRightCM(self):
        return (self.frontRight.getValue() * (-0.06)) + 60

    def frontCenterCM(self):
        return (self.frontCenter.getValue() * (-0.06)) + 60

    def backLeftCM(self):
        return (self.backLeft.getValue() * (-0.06)) + 60

    def backRightCM(self):
        return (self.backRight.getValue() * (-0.06)) + 60

    def backCenterCM(self):
        return (self.backCenter.getValue() * (-0.06)) + 60

    def frontDistance(self, value):
        return self.frontLeft.getValue() > value or self.frontCenter.getValue() > value or self.frontRight.getValue() > value

    def backDistance(self, value):
        return self.backLeft.getValue() > value or self.backCenter.getValue() > value or self.backRight.getValue() > value

class PositionSensors:

    def __init__(self, driver):
        deviceTimestep = int(driver.getBasicTimeStep() * DEVICE_TIMESTEP_MULTIPLIER)
        # get position sensors

        self.frontLeft  = driver.getDevice('left_front_sensor')
        self.frontRight = driver.getDevice('right_front_sensor')
        self.rearLeft   = driver.getDevice('left_rear_sensor')
        self.rearRight  = driver.getDevice('right_rear_sensor')

        # enable position sensors
        self.frontLeft.enable(deviceTimestep)
        self.frontRight.enable(deviceTimestep)
        self.rearLeft.enable(deviceTimestep)
        self.rearRight.enable(deviceTimestep)
