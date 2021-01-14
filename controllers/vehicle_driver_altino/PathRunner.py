from Utils import Position, logger, Orientation
from Constants import UNKNOWN, MAX_ANGLE
import Map

DISABLED = 0
FOLLOW_LINE = 1
TURN = 2
SEARCH_LINE = 3
COLLISION_AVOIDANCE = 4
GO_FORWARD = 5
U_TURN = 99

# class to handle path running service
class PathRunner:

    # initialize path running service
    def __init__(self, positioning, pathPlanner, lineFollower, distanceSensors):
        self.positioning = positioning
        self.pathPlanner = pathPlanner
        self.lineFollower = lineFollower
        self.distanceSensors = distanceSensors

        self.status = DISABLED
        self.uTurnStatus = UNKNOWN
        self.uTurnGoalOrientation = UNKNOWN
        self.uTurnStartingMeter = UNKNOWN
        self.actualTurn = 0
        self.currentPath = UNKNOWN
        self.goalReach = False
        self.steeringAngle = UNKNOWN
        self.speed = 0.5

        self.collisionImminent = False

    def isEnabled(self):
        return self.status != DISABLED

    def enable(self):
        self.status = FOLLOW_LINE

    def disable(self):
        self.status = DISABLED

    def isUTurning(self):
        return self.status == U_TURN

    def setCollisionImminent(self, value):
        self.collisionImminent = value

    # update path running service
    def update(self):
        if self.status != DISABLED:
            self.updateSpeedAndAngle()
            self.updateGoalStatus()
        

    # get new fastest path from actual position to goal if set
    def updatePath(self):
        if self.isEnabled():
            p = self.positioning.getPosition()
            x = p.getX()
            y = p.getY()
            Map.setNewObstacle(Position(x+1, y)) # TODO in base all'orientamento
            self.currentPath = self.pathPlanner.getFastestRoute()
            self.actualTurn = 0

    # check if robot have reached goal
    def updateGoalStatus(self):
        currentPosition = self.positioning.getPosition()
        goalPosition = self.pathPlanner.getGoalPosition()

        self.goalReach = currentPosition == goalPosition
    
    # update speed and angle of the robot
    def updateSpeedAndAngle(self):
        isLineLost = self.lineFollower.isLineLost()
        currentPath = self.currentPath

        logger.debug("Current Status: " + str(self.status))

        lineFollowerAngle = self.lineFollower.getNewSteeringAngle()

        if currentPath != UNKNOWN and self.actualTurn == 0:
            if self.currentPath[self.actualTurn] == U_TURN:
                self.status = U_TURN
            self.actualTurn += 1
        
        elif self.status == FOLLOW_LINE:

            self.steeringAngle = lineFollowerAngle

            if self.isGoalReach():
                self.speed = 0.0
                logger.info("Destination Reached")

            if isLineLost and currentPath == UNKNOWN:
                self.speed = 0.0
            elif isLineLost and currentPath != UNKNOWN and Map.findNearestIntersection(self.positioning.getPosition()) != -1:
                logger.log("go to TURN")
                self.status = TURN
            elif isLineLost and Map.findNearestIntersection(self.positioning.getPosition()) == -1:
                self.status = SEARCH_LINE
            
        elif self.status == TURN:
            if  currentPath != UNKNOWN and self.actualTurn < len(currentPath):
                logger.debug("CURRENT TURN: " + str(self.actualTurn))
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

        elif self.status == GO_FORWARD:
            pass

        #To Be Implement
        elif self.status == U_TURN:    
            logger.debug("Orientamento attuale: " + str(self.positioning.getOrientation()) + " orientamento goal: " + str(self.uTurnGoalOrientation))        
            self.sensors = self.distanceSensors
            logger.debug("U_TURN: Status: " + str(self.uTurnStatus))

            if self.uTurnStatus == UNKNOWN:
                #controlli se posso fare l'inversione
                self.uTurnStatus = 1
                self.steeringAngle = 1
                self.uTurnGoalOrientation = Orientation((self.positioning.inaccurateOrientation + 2) % 4) 

            if self.uTurnStatus == 1:
                if self.sensors.frontDistance(950) or self.positioning.getOrientation() == ((self.uTurnGoalOrientation + 1) % 4) or self.positioning.getOrientation() == ((self.uTurnGoalOrientation - 1) % 4):
                    logger.debug("U_TURN: Primo passo completato, vado indietro (Status 1)")
                    self.speed = -0.2
                    self.steeringAngle = -1 * self.steeringAngle
                    self.uTurnStatus = 3
                    self.uTurnStartingMeter = self.positioning.getActualDistance()       
                else:
                    self.speed = 0.2 
                    self.steeringAngle = 1

            elif self.uTurnStatus == 2:
                if self.sensors.frontDistance(950):
                    logger.debug("U_TURN: Primo passo completato, vado indietro (status 2)")
                    self.speed = -0.2
                    self.steeringAngle = -1 * self.steeringAngle
                    self.uTurnStatus += 1
                    self.uTurnStartingMeter = self.positioning.getActualDistance()

                if self.positioning.getOrientation() == self.uTurnGoalOrientation:
                    self.uTurnStatus += 2

            elif self.uTurnStatus == 3:
                if self.sensors.backDistance(950):
                    logger.debug("U_TURN: Trovato ostacolo dietro, vado avanti")
                    self.speed= 0.2
                    self.steeringAngle = -1 * self.steeringAngle
                    self.uTurnStatus -= 1

                if self.positioning.getOrientation() == self.uTurnGoalOrientation:
                    self.uTurnStatus += 1

            else:
                logger.debug("U_TURN: Manovra completata")
                logger.debug("U_TURN: Spazio percorso: " + str(self.positioning.getActualDistance() - self.uTurnStartingMeter))
                distanzaPercorsa = self.positioning.getActualDistance() - self.uTurnStartingMeter
                if distanzaPercorsa >= 0:
                    self.steeringAngle = -0.5 * self.steeringAngle
                elif abs(distanzaPercorsa) > 0.07:
                    self.steeringAngle = -0.1 * self.steeringAngle                
                else:
                    self.steeringAngle = -0.2 * self.steeringAngle

                # if Map.getValue(self.positioning.getPosition()) == Map.C:
                self.steeringAngle *= - 5

                logger.debug("U_TURN: Spazio percorso: " + str(distanzaPercorsa) + ", Angolo di sterzata: " + str(self.steeringAngle))
                self.speed= 0.5    
                self.uTurnStatus = UNKNOWN
                self.uTurnGoalOrientation = UNKNOWN
                self.uTurnStartingMeter = UNKNOWN
                self.lineFollower.resetLastLineKnownZone(self.steeringAngle)
                self.status = SEARCH_LINE  


            
        # logger.debug("Steerign angle: " + str(self.steeringAngle) + " STATUS: " + str(self.status))
        elif self.isGoalReach() and isLineLost and currentPath == UNKNOWN:
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

    # get current steering angle setted by path runner
    def getSteeringAngle(self):
        return self.steeringAngle

    # get current speed setted by path runner
    def getSpeed(self):
        return self.speed

    # return if goal has been reached
    def isGoalReach(self):
        return self.goalReach

    # set goal
    def goTo(self, goal):
        self.pathPlanner.setGoalPosition(goal)
        self.currentPath = self.pathPlanner.getFastestRoute()
        logger.debug("Current Path to Goal: " + str(self.currentPath))

    # go forward for x meters (NOT WORKING)
    def proceedForward(self, meters):
        self.status = GO_FORWARD
        startingAngle = self.getSteeringAngle()
        start = self.positioning.getActualDistance()
        stop  = start + meters 
        while stop - start > 0:
            self.steeringAngle = 0.0
        
        self.steeringAngle = startingAngle
        
