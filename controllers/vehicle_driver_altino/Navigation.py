from Utils import Position
import AStar

B = 10
O = 10
R = 1
I = 2

NORD = 10
EST = 11
SOUTH = 12
WEST = 13

LEFT = -1
RIGHT = 1
FORWARD = 0
U_TURN = 99

WIDTH = 25
HEIGHT = 17
# o-----> Y      ^ N
# |              | 
# |        W <-- o --> E
# v X            |
#                v S
#                                       
#      Y= 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24     X    map[X][Y]
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
# [(8, 12), (8, 17), (12, 17), (12, 23), (15,23)]
# [(8, 12), (8, 13), (8, 14), (8, 15), (8, 16), (8, 17), (9, 17), (10, 17), (11, 17), (12, 17), (12, 18), (12, 19), (12, 20), (12, 21), (12, 22), (12, 23), (13, 23), (14, 23), (15, 23)]         
class Navigation:

    def __init__(self):
        self.map = MAP

        self.robotPosition = Position(0, 0)
        self.robotOrientation = WEST
        self.goalPosition = Position (0, 0)

    def getIntersectionNodes(self, route):
        intersections = []
        intersections.append(route[0])

        for i in range(1, len(route) - 1):
            node = route[i]
            if self.map[node[0]][node[1]] == I:
                intersections.append(node)
        
        intersections.append(route[-1]) 
        
        return intersections

    def getFastestRoute(self):
        directions = []
        # directions.append(self.robotOrientation)
        
        route = AStar.findPath(self.map, self.robotPosition.getPositionArray(), self.goalPosition.getPositionArray())
        print("AStar: " + str(route))

        route = self.getIntersectionNodes(route)
        print("Intersecitons:" + str(route))

        prevNode = route[0]
        for i in range(1,len(route)):
            currentNode = route[i]
            print("currentNode: " + str(currentNode))
            print("prevNode: " + str(prevNode))
            if currentNode[0] > prevNode[0]:
                directions.append(SOUTH)
            elif currentNode[0] < prevNode[0]:
                directions.append(NORD)
            elif currentNode[1] > prevNode[1]:
                directions.append(EST)
            elif currentNode[1] < prevNode[1]:
                directions.append(WEST)
            else:
                print("WTF?!?")
            prevNode = currentNode
        
        print("directions: " + str(directions))
            
        turns = []
        actualDirection = self.robotOrientation
        for i in range(len(directions)):
            direction = directions[i]
            print("actualDirection: " + str(actualDirection))
            print("direction: " + str(direction))
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
            actualDirection = direction



        print(turns)

        return

        # davide
        prevNode = route[0]
        for i in range(1,len(route)):
            currentNode = route[i]
            if currentNode[0] != prevNode[0] and currentNode[1] != prevNode[1]:
                pass


        #sp
        prevNode = route[0]
        for i in range(1, len(route)):
            currentNode = route[i]

            if currentNode[0] == prevNode[0]:
                if currentNode[1] > prevNode[0]:
                    if self.robotOrientation == EST:
                        directions.append(FORWARD)

        for position in route:
            if self.map(position[0], position[1]) == I:
                pass
                

    def setRobotPosition(self, array):
        x = array[0]
        y = array[1]

        if x > 0 and x < HEIGHT - 1:
            self.robotPosition.setX(x)

        if y > 0 and y < WIDTH - 1:
            self.robotPosition.setY(y)
    
    def setGoalPosition(self, array):
        x = array[0]
        y = array[1]

        if x > 0 and x < HEIGHT - 1:
            self.goalPosition.setX(x)

        if y > 0 and y < WIDTH - 1:
            self.goalPosition.setY(y)

    def setRobotOrientation(self, orientation):
        if orientation >= 0 and orientation <= 4:
            self.robotOrientation = orientation

    

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
        print(robotPosition.getPositionArray())
        print(goalPosition.getPositionArray())
        print("Robot Orientation: " + str(robotOrientation))
        print("Goal Position: " + "(X: " + str(goalPosition.getX()) + ", Y: " + str(goalPosition.getY()) +")")

