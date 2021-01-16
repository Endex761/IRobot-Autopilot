from Constants import DEVICE_TIMESTEP_MULTIPLIER, MAX_ANGLE, MAX_SPEED, UNKNOWN
from Utils import Orientation, logger
import math

# actuator class to handle speed and steering 
class Actuators:
    def __init__(self, driver):
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

# class to handle camera data
class Camera:
    def __init__(self, driver):
        deviceTimestep = int(driver.getBasicTimeStep() * DEVICE_TIMESTEP_MULTIPLIER)

        self.camera = driver.getDevice('camera')

        self.camera.enable(deviceTimestep) #fix

    # return camera image in array form
    def getImageArray(self):
        return self.camera.getImageArray()

    def getWidth(self):
        return self.camera.getWidth()
    
    def getHeight(self):
        return self.camera.getHeight()

# compass class to handle compass data        
class Compass:
    def __init__(self, driver):
        deviceTimestep = int(driver.getBasicTimeStep() * DEVICE_TIMESTEP_MULTIPLIER)
        
        self.compass = driver.getDevice('compass')
        self.compass.enable(deviceTimestep)

        self.orientation = UNKNOWN
        self.inaccurateOrientation = UNKNOWN
        self.orientation = self.getInaccurateOrientation()

    # get fine orientation for navigation purpose
    def getOrientation(self):
        threshold = 0.95
        self.orientation = self.computeOrientation(threshold, self.orientation)
        return self.orientation

    # get inaccurate orientation for positioning purpose
    def getInaccurateOrientation(self):
        threshold = 0.5
        self.inaccurateOrientation = self.computeOrientation(threshold, self.inaccurateOrientation)
        return self.inaccurateOrientation

    # get compass data and convert to orientation
    def computeOrientation(self, precision, oldOrientation):
        # this return 3d vector indicating nord pole
        compassData = self.compass.getValues()
        yComponent = compassData[0]
        xComponent = compassData[2]

        newOrientation = oldOrientation

        compassThreshold = precision
        if xComponent > compassThreshold:
            newOrientation = Orientation.NORD
        elif xComponent < -compassThreshold:
            newOrientation = Orientation.SOUTH
        elif yComponent > compassThreshold:
            newOrientation = Orientation.EAST
        elif yComponent < -compassThreshold:
            newOrientation = Orientation.WEST

        return newOrientation

    def getAngleFromOrientation(self):
        orientation = self.getOrientation()
        compassData = self.compass.getValues()
        xToll = 0.0
        yToll = 0.0
        xComponent = compassData[2] - xToll # this is 1 when going NORD -1 when SOUTH
        yComponent = compassData[0] - yToll # this is 1 when going EAST -1 when WEST

        angle = 0.0

        if orientation == Orientation.NORD:
            angle = math.acos(xComponent)
        elif orientation == Orientation.SOUTH:
            angle = math.acos(-xComponent)
        elif orientation == Orientation.EAST:
            angle = math.acos(yComponent)
        elif orientation == Orientation.WEST:
            angle = math.acos(-yComponent)
        
        return angle

    def getXComponent(self):
        compassData = self.compass.getValues()
        return compassData[2]
    
    def getYComponent(self):
        compassData = self.compass.getValues()
        return compassData[0]


        
# distance sensor class to handle distance sensor data
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

    # check if front sensors detect a distance less or equal to value
    def frontDistance(self, value):
        return self.frontLeft.getValue() > value or self.frontCenter.getValue() > value or self.frontRight.getValue() > value
    # check if back sensors detect a distance less or equal to value   
    def backDistance(self, value):
        return self.backLeft.getValue() > value or self.backCenter.getValue() > value or self.backRight.getValue() > value

# class to handle keyboard input
class Keyboard:
    def __init__(self, driver):
        deviceTimestep = int(driver.getBasicTimeStep() * DEVICE_TIMESTEP_MULTIPLIER)
        self.keyboard = driver.getKeyboard()
        self.keyboard.enable(deviceTimestep)

        self.pressedKey = UNKNOWN

    def getKey(self):
        return self.pressedKey

    def update(self):
        self.pressedKey = self.keyboard.getKey()

    # return true if char key or his uppercase is pressed
    def isKeyPressed(self, key ,char):
        return key == ord(char) or key == ord(char.upper())


# position sensor class to handle positon sensor data from wheels encoders
class PositionSensors:

    def __init__(self, driver):
        deviceTimestep = int(driver.getBasicTimeStep() * DEVICE_TIMESTEP_MULTIPLIER)
        # get position sensors
        self.frontLeft  = driver.getDevice('left_front_sensor')
        self.frontRight = driver.getDevice('right_front_sensor')
        self.rearLeft   = driver.getDevice('left_rear_sensor')
        self.rearRight  = driver.getDevice('right_rear_sensor')
        self.steerLeft  = driver.getDevice('left_steer_sensor')
        self.steerRight = driver.getDevice('right_steer_sensor')

        # enable position sensors
        self.frontLeft.enable(deviceTimestep)
        self.frontRight.enable(deviceTimestep)
        self.rearLeft.enable(deviceTimestep)
        self.rearRight.enable(deviceTimestep)
        self.steerLeft.enable(deviceTimestep)
        self.steerRight.enable(deviceTimestep)