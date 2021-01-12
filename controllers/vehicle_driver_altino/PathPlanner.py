from Constants import UNKNOWN, LEFT, RIGHT, FORWARD, U_TURN
from Utils import logger, Position, Orientation
import Map
import AStar

# CARDINAL POINTS
#Orientation.NORD = 0
#Orientation.EAST = 1
#Orientation.SOUTH = 2
#Orientation.WEST = 3

# TURNS
#LEFT = -1
#RIGHT = 1
#FORWARD = 0
#U_TURN = 99

# MAP DIMENSIONS
#WIDTH = 25
#HEIGHT = 17

# MAP CONSTANS
#B = AStar.WALL
#O = AStar.WALL
#R = 1
#I = 2
#C = 3

# --- MAP ---
# o-----> Y      ^ N
# |              | 
# |        W <-- o --> E
# v X            |
#                v S
#                                       
#       Y  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24     X    map[X][Y]
#MAP =   [[B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B], # 0
#         [B, C, R, R, R, R, I, R, R, R, R, R, I, R, R, R, R, I, R, R, R, R, R, C, B], # 1
#         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 2
#         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 3
#         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 4
#         [B, I, R, R, R, R, I, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 5
#         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 6
#         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 7
#         [B, R, O, O, O, O, I, R, R, R, R, R, I, R, R, R, R, I, R, R, R, R, R, I, B], # 8
#         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 9
#         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 10
#         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 11
#         [B, R, O, O, O, O, R, O, O, O, O, O, I, R, R, R, R, I, R, R, R, R, R, I, B], # 12
#         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 13
#         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 14
#         [B, C, R, R, R, R, I, R, R, R, R, R, C, O, O, O, O, C, R, R, R, R, R, C, B], # 15
#         [B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B]] # 16

 # class to handle path planning service
class PathPlanner:

    # initialize path planning service
    def __init__(self, positioning):
        self.map = Map.MAP
        self.positioning = positioning
        self.robotPosition = positioning.getPosition()
        self.robotOrientation = positioning.getOrientation()
        self.goalPosition = Position (14, 23)

    # update path planning service
    def update(self):
        self.robotPosition = self.positioning.getPosition()
        self.robotOrientation = self.positioning.getOrientation()

    # update map to improve path planning when obstacle are found
    def updateMap(self):
        self.map = Map.MAP

    
    # return array containing a turn for each intersection in the path between robot position and goal
    def getFastestRoute(self):

        # update map status, this ensure new obstacles are detected
        self.updateMap()
        
        # get fastest route from AStar giving map, start position and goal position
        route = AStar.findPath(self.map, self.robotPosition.getPositionArray(), self.goalPosition.getPositionArray())

        # get only intersection nodes from AStar route
        intersections = self.getIntersectionNodesFromRoute(route)

        # get cardinal points directions based on intersection nodes
        directions = self.getDirectionsFromIntersections(intersections)
        
        # get turns based on robot directions and robot orientation
        turns = self.getTurnsFromDirections(directions)

        # remove curve turns
        turns = self.removeCurves(turns, intersections)

        # return the turns
        return turns

    #set goal position in the map
    def setGoalPosition(self, position):
        x = position.getX()
        y = position.getY()

        if x > 0 and x < Map.HEIGHT - 1:
            if y > 0 and y < Map.WIDTH - 1:
                self.goalPosition.setY(y)
                self.goalPosition.setX(x)
                return
        self.goalPosition = UNKNOWN
    
    def getGoalPosition(self):
        return self.goalPosition

    # return first, last and intersection nodes from AStar route
    def getIntersectionNodesFromRoute(self, route):
        intersections = []
        #if self.map[route[0][0]][route[0][1]] == I:
            # get first node
        intersections.append(route[0])

        # get intersection nodes
        for node in route[1:-1]:
            if self.map[node[0]][node[1]] == Map.I or self.map[node[0]][node[1]] == Map.C:
                intersections.append(node)

        # get last node
        intersections.append(route[-1]) 
        
        # return intersections
        return intersections

    # return cardinal points direction from one intersection to another
    def getDirectionsFromIntersections(self, intersections):
        directions = []

        # for each cople of nodes compute cardinal points direction between them
        prevNode = intersections[0]
        for currentNode in intersections[1:]:
            # check if X has changed
            if currentNode[0] > prevNode[0]:
                directions.append(Orientation.SOUTH)
            elif currentNode[0] < prevNode[0]:
                directions.append(Orientation.NORD)
            # check if Y has changed
            elif currentNode[1] > prevNode[1]:
                directions.append(Orientation.EAST)
            elif currentNode[1] < prevNode[1]:
                directions.append(Orientation.WEST)
            else:
                logger.error("Invalid intersetions")
            # go to next couple of node
            prevNode = currentNode
        
        return directions

    # contains a list of turns (RIGHT, LEFT, FORWARD, U_TURN) for each intersection based on robot orientation and next direction
    def getTurnsFromDirections(self, directions):
        turns = []

        # get actual robot orientation
        actualDirection = self.robotOrientation
        
        # for each cardinal point direction compute turn based on robot current and future orientation
        for direction in directions:
            # FORWARD case
            if actualDirection == direction:
                turns.append(FORWARD)
            # EST cases
            elif actualDirection == Orientation.EAST and direction == Orientation.SOUTH:
                turns.append(RIGHT)
            elif actualDirection == Orientation.EAST and direction == Orientation.NORD:
                turns.append(LEFT)
            elif actualDirection == Orientation.EAST and direction == Orientation.WEST:
                turns.append(U_TURN)
            # WEST cases
            elif actualDirection == Orientation.WEST and direction == Orientation.SOUTH:
                turns.append(LEFT)
            elif actualDirection == Orientation.WEST and direction == Orientation.NORD:
                turns.append(RIGHT)
            elif actualDirection == Orientation.WEST and direction == Orientation.EAST:
                turns.append(U_TURN)
            # NORD cases
            elif actualDirection == Orientation.NORD and direction == Orientation.EAST:
                turns.append(RIGHT)
            elif actualDirection == Orientation.NORD and direction == Orientation.WEST:
                turns.append(LEFT)
            elif actualDirection == Orientation.NORD and direction == Orientation.SOUTH:
                turns.append(U_TURN)
            # SOUTH cases
            elif actualDirection == Orientation.SOUTH and direction == Orientation.EAST:
                turns.append(LEFT)
            elif actualDirection == Orientation.SOUTH and direction == Orientation.WEST:
                turns.append(RIGHT)
            elif actualDirection == Orientation.SOUTH and direction == Orientation.NORD:
                turns.append(U_TURN)
            # change actual direction 
            actualDirection = direction

        return turns

    # remove curves from turns
    def removeCurves(self, turns, intersections):
        newTurns = [turns[0]]
        for i in range(1, len(intersections) - 2):
            node = intersections[i]
            if self.map[node[0]][node[1]] != Map.C:
                newTurns.append(turns[i])
        return newTurns

    # print actual status
    def printStatus(self):
        robotPosition = self.robotPosition
        goalPosition = self.goalPosition
        robotOrientation = "UNKNOWN"
        if self.robotOrientation == Orientation.NORD:
            robotOrientation = "Orientation.NORD"
        if self.robotOrientation == Orientation.EAST:
            robotOrientation = "EST"    
        if self.robotOrientation == Orientation.SOUTH:
            robotOrientation = "Orientation.SOUTH"
        if self.robotOrientation == Orientation.WEST:
            robotOrientation = "Orientation.WEST"
        
        print("Navigation Status: ")
        print("Robot Position: " + "(X: " + str(robotPosition.getX()) + ", Y: " + str(robotPosition.getY()) +")")
        print("Robot Orientation: " + str(robotOrientation))
        print("Goal Position: " + "(X: " + str(goalPosition.getX()) + ", Y: " + str(goalPosition.getY()) +")")

