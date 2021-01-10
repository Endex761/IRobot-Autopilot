from Utils import Position
import AStar

# CARDINAL POINTS
NORD = 0
EST = 1
SOUTH = 2
WEST = 3

# TURNS
LEFT = -1
RIGHT = 1
FORWARD = 0
U_TURN = 99

# MAP DIMENSIONS
WIDTH = 25
HEIGHT = 17

# MAP CONSTANS
B = AStar.WALL
O = AStar.WALL
R = 1
I = 2

# --- MAP ---
# o-----> Y      ^ N
# |              | 
# |        W <-- o --> E
# v X            |
#                v S
#                                       
#      Y  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24     X    map[X][Y]
MAP =   [[B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B], # 0
         [B, R, R, R, R, R, I, R, R, R, R, R, I, R, R, R, R, I, R, R, R, R, R, R, B], # 1
         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 2
         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 3
         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 4
         [B, I, R, R, R, R, I, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 5
         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 6
         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 7
         [B, R, O, O, O, O, I, R, R, R, R, R, I, R, R, R, R, I, R, R, R, R, R, I, B], # 8
         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 9
         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 10
         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 11
         [B, R, O, O, O, O, R, O, O, O, O, O, I, R, R, R, R, I, R, R, R, R, R, I, B], # 12
         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 13
         [B, R, O, O, O, O, R, O, O, O, O, O, R, O, O, O, O, R, O, O, O, O, O, R, B], # 14
         [B, R, R, R, R, R, I, R, R, R, R, R, R, O, O, O, O, R, R, R, R, R, R, R, B], # 15
         [B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B]] # 16

 # Navigation class
class Navigation:

    def __init__(self):
        self.map = MAP

        self.robotPosition = Position(0, 0)
        self.robotOrientation = NORD
        self.goalPosition = Position (0, 0)
    
    # return array containing a turn for each intersection in the path between robot position and goal
    def getFastestRoute(self):
        
        # get fastest route from AStar giving map, start position and goal position
        route = AStar.findPath(self.map, self.robotPosition.getPositionArray(), self.goalPosition.getPositionArray())

        # get only intersection nodes from AStar route
        intersections = self.getIntersectionNodesFromRoute(route)

        # get cardinal points directions based on intersection nodes
        directions = self.getDirectionsFromIntersections(intersections)
        
        # get turns based on robot directions and robot orientation
        turns = self.getTurnsFromDirections(directions)

        # return the turns
        return turns

    # return first, last and intersection nodes from AStar route
    def getIntersectionNodesFromRoute(self, route):
        intersections = []
        # get first node
        intersections.append(route[0])

        # get intersection nodes
        for node in route[1:-1]:
            if self.map[node[0]][node[1]] == I:
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
                directions.append(SOUTH)
            elif currentNode[0] < prevNode[0]:
                directions.append(NORD)
            # check if Y has changed
            elif currentNode[1] > prevNode[1]:
                directions.append(EST)
            elif currentNode[1] < prevNode[1]:
                directions.append(WEST)
            else:
                print("ERROR: Invalid intersetions")
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
            elif actualDirection == EST and direction == SOUTH:
                turns.append(RIGHT)
            elif actualDirection == EST and direction == NORD:
                turns.append(LEFT)
            elif actualDirection == EST and direction == WEST:
                turns.append(U_TURN)
            # WEST cases
            elif actualDirection == WEST and direction == SOUTH:
                turns.append(LEFT)
            elif actualDirection == WEST and direction == NORD:
                turns.append(RIGHT)
            elif actualDirection == WEST and direction == EST:
                turns.append(U_TURN)
            # NORD cases
            elif actualDirection == NORD and direction == EST:
                turns.append(RIGHT)
            elif actualDirection == NORD and direction == WEST:
                turns.append(LEFT)
            elif actualDirection == NORD and direction == SOUTH:
                turns.append(U_TURN)
            # SOUTH cases
            elif actualDirection == SOUTH and direction == EST:
                turns.append(LEFT)
            elif actualDirection == SOUTH and direction == WEST:
                turns.append(RIGHT)
            elif actualDirection == SOUTH and direction == NORD:
                turns.append(U_TURN)
            # change actual direction 
            actualDirection = direction

        return turns

    # set robot position in the map
    def setRobotPosition(self, array):
        x = array[0]
        y = array[1]

        if x > 0 and x < HEIGHT - 1:
            self.robotPosition.setX(x)

        if y > 0 and y < WIDTH - 1:
            self.robotPosition.setY(y)
    
    # set robot orientation
    def setRobotOrientation(self, orientation):
        if orientation >= 0 and orientation <= 4:
            self.robotOrientation = orientation
    
    #set goal position in the map
    def setGoalPosition(self, array):
        x = array[0]
        y = array[1]

        if x > 0 and x < HEIGHT - 1:
            self.goalPosition.setX(x)

        if y > 0 and y < WIDTH - 1:
            self.goalPosition.setY(y)

    # print actual status
    def printStatus(self):
        robotPosition = self.robotPosition
        goalPosition = self.goalPosition
        robotOrientation = "UNKNOWN"
        if self.robotOrientation == NORD:
            robotOrientation = "NORD"
        if self.robotOrientation == EST:
            robotOrientation = "EST"    
        if self.robotOrientation == SOUTH:
            robotOrientation = "SOUTH"
        if self.robotOrientation == WEST:
            robotOrientation = "WEST"
        
        print("Navigation Status: ")
        print("Robot Position: " + "(X: " + str(robotPosition.getX()) + ", Y: " + str(robotPosition.getY()) +")")
        print("Robot Orientation: " + str(robotOrientation))
        print("Goal Position: " + "(X: " + str(goalPosition.getX()) + ", Y: " + str(goalPosition.getY()) +")")

