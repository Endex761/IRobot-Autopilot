from Constants import UNKNOWN

class PathRunner:
    def __init__(self, positioning, pathPlanner, lineFollower):
        self.positioning = positioning
        self.pathPlanner = pathPlanner
        self.lineFollower = lineFollower

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
        
        if self.isGoalReach() and isLineLost and currentPath == UNKNOWN:
            self.speed = 0.0

        elif not isLineLost:
            self.steeringAngle = self.lineFollower.getNewSteeringAngle()
            self.actualTurn += 1

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