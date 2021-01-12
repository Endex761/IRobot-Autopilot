from Utils import logger, Orientation
from Constants import UNKNOWN, MAX_ANGLE
import Map

FOLLOW_LINE = 1
TURN = 2
SEARCH_LINE = 3
COLLISION_AVOIDANCE = 4
GO_FORWARD = 5
U_TURN = 6

class PathRunner:
    def __init__(self, positioning, pathPlanner, lineFollower, collisionAvoidance):
        self.positioning = positioning
        self.pathPlanner = pathPlanner
        self.lineFollower = lineFollower
        self.collisionAvoidance = collisionAvoidance

        self.status = FOLLOW_LINE
        self.uTurnStatus = UNKNOWN
        self.uTurnGoalOrientation = UNKNOWN
        self.actualTurn = 0
        self.currentPath = UNKNOWN
        self.goalReach = False
        self.steeringAngle = UNKNOWN
        self.speed = 0.5

        self.collisionAvoidanceCount = 0

    def update(self):
        self.updateSpeedAndAngle()
        self.updateGoalStatus()

    def updatePath(self):
        self.currentPath = self.pathPlanner.getFastestRoute()

    def updateGoalStatus(self):
        currentPosition = self.positioning.getPosition()
        goalPosition = self.pathPlanner.getGoalPosition()

        self.goalReach = currentPosition == goalPosition
    
    def updateSpeedAndAngle(self):
        isLineLost = self.lineFollower.isLineLost()
        currentPath = self.currentPath

        lineFollowerAngle = self.lineFollower.getNewSteeringAngle()
        collisionAvoidanceAngle  = self.collisionAvoidance.getSteeringAngle()

        logger.debug("Status: " + str(self.status) + "CD: " + str(self.collisionAvoidance.isCollisionDetect()) + " LF: " + str(lineFollowerAngle) + " CA: " + str(collisionAvoidanceAngle))

        if self.collisionAvoidance.isCollisionDetect():
            if self.status == TURN:
                logger.info("Can't turn")
            self.status = COLLISION_AVOIDANCE
        """

        if currentPath != UNKNOWN and self.actualTurn == 0:
            # here i should change the orientation
            self.actualTurn += 1
            self.status = U_TURN
            pass

        
        """
        if self.status == COLLISION_AVOIDANCE:
            
            self.steeringAngle = collisionAvoidanceAngle
            if not self.collisionAvoidance.isCollisionDetect():
                #self.proceedForward(0.05)
                self.status = SEARCH_LINE
                
        
        elif self.status == FOLLOW_LINE:

            if abs(collisionAvoidanceAngle) > abs(lineFollowerAngle) + 0.1:
                self.status = COLLISION_AVOIDANCE

            self.steeringAngle = lineFollowerAngle

            if self.isGoalReach():
                self.speed = 0.0
                logger.info("Destination Reached")

            if isLineLost and currentPath == UNKNOWN:
                self.speed = 0.0
            elif isLineLost and currentPath != UNKNOWN and Map.getValue(self.positioning.getPosition()) == Map.I:
                self.status = TURN
            elif isLineLost and Map.findNearestIntersection(self.positioning.getPosition()) == -1:
                self.status = SEARCH_LINE
            

        elif self.status == TURN:
            if  currentPath != UNKNOWN and self.actualTurn < len(currentPath):
                turn = currentPath[self.actualTurn]
                self.steeringAngle = 0.57 * turn
            else:
                self.currentPath = UNKNOWN
            
            if not isLineLost:
                self.actualTurn += 1
                self.status = FOLLOW_LINE

        elif self.status == SEARCH_LINE:
            self.steeringAngle = self.lineFollower.getSteeringAngleLineSearching()

            if not isLineLost:
                logger.debug("Line was lost and i found it!")
                self.status = FOLLOW_LINE

        if self.status == GO_FORWARD:
            pass

        #To Be Implement
        if self.status == U_TURN:            
            # prendo i sensori 
            self.sensors = self.collisionAvoidance.getDistanceSensor()

            logger.debug("U_TURN: Front Left Position Sensor: " + str(self.sensors.frontLeft.getValue()) + ", cm: " + str(self.sensors.frontLeftCM()))
            logger.debug("U_TURN: Front Right Position Sensor: " + str(self.sensors.frontRight.getValue()) + ", cm: " + str(self.sensors.frontRightCM()))
            logger.debug("U_TURN: Back Left Position Sensor: " + str(self.sensors.backLeft.getValue()) + ", cm: " + str(self.sensors.backLeftCM()))
            logger.debug("U_TURN: Back Right Position Sensor: " + str(self.sensors.backRight.getValue()) + ", cm: " + str(self.sensors.backRightCM()))
            logger.debug("U_TURN: Compass value: "+ str(self.positioning.getOrientation()))     
            logger.debug("U_TURN: Status: " + str(self.uTurnStatus))

            if self.uTurnStatus == UNKNOWN:
                # set slow speed 
                self.speed= 0.2                
                # set steering MAX
                self.steeringAngle = 1
                self.uTurnStatus = 1
                self.uTurnGoalOrientation = Orientation((self.positioning.getOrientation() + 2) % 4)    
                logger.debug("U_TURN: Start Orientation: " + str(self.positioning.getOrientation()))     
                logger.debug("U_TURN: Goal Orientation: " + str(self.uTurnGoalOrientation))
            elif self.uTurnStatus == 1:
                if self.sensors.frontRight.getValue() > 900 or self.sensors.sideRight.getValue() > 900:
                    logger.debug("Trovato ostacolo a destra, giro tutto a sinistra")
                    self.steeringAngle = -1
                    self.uTurnStatus += 1
            elif self.uTurnStatus == 2:
                if self.sensors.frontRight.getValue() < 500:
                    self.uTurnStatus += 1
            elif self.uTurnStatus == 3:
                if self.sensors.frontLeft.getValue() > 900 or self.sensors.frontCenter.getValue() > 900 or self.sensors.frontRight.getValue() > 900:
                    logger.debug("Trovato ostacolo a sinistra o davanti, vado indietro a destra")
                    self.speed= -0.2
                    self.steeringAngle = 1
                    self.uTurnStatus += 1
            elif self.uTurnStatus == 4:
                if self.sensors.backLeft.getValue() > 900 or self.sensors.backCenter.getValue() > 900:
                    logger.debug("Trovato ostacolo dietro, vado avanti a sinistra e cerco la linea")
                    self.speed= 0.2
                    self.steeringAngle = -1
                    self.uTurnStatus += 1

                if self.positioning.getOrientation() == self.uTurnGoalOrientation:
                    self.uTurnStatus += 1
            elif self.uTurnStatus == 5:
                if self.sensors.frontLeft.getValue() > 900 or self.sensors.frontCenter.getValue() > 900 or self.sensors.frontRight.getValue() > 900:
                    self.uTurnStatus = 3

                elif self.positioning.getOrientation() == self.uTurnGoalOrientation:
                    self.uTurnStatus += 1
            else:
                self.speed= 0.2
                self.steeringAngle = -0.2
                self.status = FOLLOW_LINE  
                logger.debug("Manovra completata")


            
        # logger.debug("Steerign angle: " + str(self.steeringAngle) + " STATUS: " + str(self.status))


        isLineLost = self.lineFollower.isLineLost()
        currentPath = self.currentPath
        print(self.currentPath)
        if self.isGoalReach() and isLineLost and currentPath == UNKNOWN:
            self.speed = 0.0

        elif not isLineLost:
            self.steeringAngle = self.lineFollower.getNewSteeringAngle()
            # self.actualTurn += 1

        elif isLineLost and currentPath != UNKNOWN:
            if self.actualTurn < len(currentPath):
                turn = currentPath[self.actualTurn]
                self.steeringAngle = 0.5 * turn
                # what if U_TURN? Return it to motion to make u_turn?
            else:
                currentPath = UNKNOWN

        elif isLineLost and currentPath == UNKNOWN:
            # self.speed = 0.0
            pass


    def getSteeringAngle(self):
        return self.steeringAngle

    def getSpeed(self):
        return self.speed

    def isGoalReach(self):
        return self.goalReach

    def goTo(self, goal):
        self.pathPlanner.setGoalPosition(goal)
        self.currentPath = self.pathPlanner.getFastestRoute()
        print(self.currentPath)

    def proceedForward(self, meters):
        self.status = GO_FORWARD
        startingAngle = self.getSteeringAngle()
        start = self.positioning.getActualDistance()
        stop  = start + meters 
        while stop - start > 0:
            self.steeringAngle = 0.0
        
        self.steeringAngle = startingAngle
        
