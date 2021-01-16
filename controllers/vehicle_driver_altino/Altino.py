# import devices and serivices to use in the altino toy car
from Constants import GPX, GPY
from ExternalController import ExternalController
from vehicle import Driver
from CollisionAvoidance import CollissionAvoidance
from Utils import Position, logger
from Devices import Actuators, Camera, Compass, DistanceSensors, Keyboard, PositionSensors
from LineFollower import LineFollower
from Positioning import Positioning
from PathPlanner import PathPlanner
from PathRunner import PathRunner
from Parking import Parking
from ManualDrive import ManualDrive
from Motion import Motion

# altino states
RUN = 1
STOP = 2

class Altino:

    def __init__(self):
        
        self.status = STOP
        
        # initialize altino driver
        self.driver = Driver()
             
        # initialize actuators
        self.actuators = Actuators(self.driver)
        
        # initialize distance and position sensors
        self.distanceSensors = DistanceSensors(self.driver)
        self.positionSensors = PositionSensors(self.driver)
        
        # initialize compass
        self.compass = Compass(self.driver)
        
        # initialize camera
        self.camera = Camera(self.driver)

        # initialize keyboard
        self.keyboard = Keyboard(self.driver)
        
        # this ensure sensors are correctly initialized
        self.devicesInitialization()

        # extern keyboard controller
        self.externalController = ExternalController(self.keyboard)
        self.externalController.enable()

        # collision avoidance service
        self.collisionAvoidance = CollissionAvoidance(self.distanceSensors)
        self.collisionAvoidance.enable()
        
        # line following service
        self.lineFollower = LineFollower(self.camera)
        
        # positioning service
        self.positioning = Positioning(self.positionSensors, self.compass, self.lineFollower, self.actuators)
        
        # path planning serivice
        self.pathPlanner = PathPlanner(self.positioning)
        
        # path running service
        self.pathRunner = PathRunner(self.positioning, self.pathPlanner, self.lineFollower, self.distanceSensors)
        self.pathRunner.enable()
        
        # set path runner destination
        self.pathRunner.goTo(Position(GPX, GPY))

        self.parking = Parking(self.distanceSensors, self.positioning, self.lineFollower)
        # self.parking.enable()

        self.manualDrive = ManualDrive(self.keyboard)
        # self.manualDrive.enable()
        
        # motion serivice
        self.motion = Motion(self.actuators, self.pathRunner, self.parking, self.collisionAvoidance, self.manualDrive, self.externalController)


    # run
    def run(self):
        logger.info("Altino is running.")
        self.status = RUN
        # for each timestep update services
        while self.driver.step() != -1 and self.status == RUN:
            logger.debug("__________ NEW CYCLE _____________")
            self.keyboard.update()
            self.externalController.update()
            self.collisionAvoidance.update()
            self.lineFollower.update()
            self.positioning.update()
            self.pathPlanner.update()
            self.pathRunner.update()
            self.parking.update()
            self.manualDrive.update()
            self.motion.update()

    # stop
    def stop(self):
        logger.info("Altino is stopping.")
        self.status = STOP

    # to be sure sensors are correctly initialized before using them
    def devicesInitialization(self):
        for i in range(int(self.driver.getBasicTimeStep() * 2/self.driver.getBasicTimeStep()) + 1):
            self.driver.step()