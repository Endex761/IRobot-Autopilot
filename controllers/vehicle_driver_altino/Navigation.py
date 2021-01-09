from Utils import Position
B = 100
R = 1
O = 100
I = 1

NORD = 0
EST = 1
SOUTH = 2
WEST = 3

WIDTH = 25
HEIGHT = 17
# o-----> Y      ^ N
# |              | 
# |        W <-- o --> E
# v X            |
#                v S
#                                       
#         0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24   
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

class Navigation:

    def __init__(self):
        self.map = MAP

        self.robotPosition = Position(0, 0)
        self.robotOrientation = NORD
        self.goalPosition = Position (0, 0)

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

    def getFastestRoute(self):
        pass

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

