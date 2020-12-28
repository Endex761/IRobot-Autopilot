from vehicle import Driver
from Utils import DistanceSensors, PositionSensors
from Utils import Logger, Status

# constants 
MAX_SPEED = 1.8
MAX_ANGLE = 0.5

logger = Logger()
logger.DEBUG_ENABLED = True

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
        threshold = 900
        ds = self.distanceSensors
        fl = ds.frontLeft.getValue()
        fc = ds.frontCenter.getValue()
        fr = ds.frontRight.getValue()

        rear = ds.back.getValue()

        if fl > threshold or fc > threshold or fr > threshold:
            return True
        
        if rear > threshold:
            return True

        
    # running
    def run(self):
        logger.log("Running..")
        park = False
        while self.driver.step() != -1:

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
                logger.log("Left Position Sensor: " + str(ps.frontLeft.getValue()), logger.DEBUG)

                if ds.sideLeft.getValue() < 650:
                    park = True

                # park found
                if park == True and ds.sideLeft.getValue() > 650:
                    logger.log("Park Found!")
                    logger.log("Start Parking..")
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
        

    


    
    
