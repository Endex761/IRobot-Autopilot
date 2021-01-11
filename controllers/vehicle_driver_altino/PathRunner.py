from Constants import UNKNOWN
import Map

FOLLOW_LINE = 1
TURN = 2
SEARCH_LINE = 3

class PathRunner:
    def __init__(self, positioning, pathPlanner, lineFollower):
        self.positioning = positioning
        self.pathPlanner = pathPlanner
        self.lineFollower = lineFollower

        self.status = FOLLOW_LINE
        self.actualTurn = 0
        self.currentPath = UNKNOWN
        self.goalReach = False
        self.steeringAngle = UNKNOWN
        self.speed = 0.5

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
        
        if self.status == FOLLOW_LINE:
            self.steeringAngle = self.lineFollower.getNewSteeringAngle()
            if isLineLost and currentPath == UNKNOWN:
                self.speed = 0.0
            elif isLineLost and Map.getValue(self.positioning.position) != Map.I and Map.findNearestIntersection(self.positioning.position) == self.positioning.position:
                self.status = SEARCH_LINE
            elif isLineLost and currentPath != UNKNOWN:
                self.status = TURN

        if self.status == TURN:
            if self.actualTurn < len(currentPath) and currentPath != UNKNOWN:
                turn = currentPath[self.actualTurn]
                self.steeringAngle = 0.5 * turn
            else:
                self.currentPath = UNKNOWN
            
            if not isLineLost:
                self.actualTurn += 1
                self.status = FOLLOW_LINE

        if self.status == SEARCH_LINE:
            self.steeringAngle = self.lineFollower.getSteeringAngleLineSearching()

            if not isLineLost:
                self.status = FOLLOW_LINE



        """isLineLost = self.lineFollower.isLineLost()
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
            pass"""


    def getSteeringAngle(self):
        return self.steeringAngle

    def getSpeed(self):
        return self.speed

    def isGoalReach(self):
        return self.goalReach

    def goTo(self, goal):
        self.pathPlanner.setGoalPosition(goal)
        self.currentPath = self.pathPlanner.getFastestRoute()
