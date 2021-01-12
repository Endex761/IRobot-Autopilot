from Utils import Orientation, Position
from AStar import WALL

# MAP DIMENSIONS
WIDTH = 25
HEIGHT = 17
MAP_RESOLUTION = 0.5

# MAP CONSTANS
B = WALL
O = WALL
R = 1
I = 2
C = 3

# --- MAP ---
# o-----> Y      ^ N
# |              | 
# |        W <-- o --> E
# v X            |
#                v S
#                                       
#      Y  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24     X    map[X][Y]
MAP =   [[B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B], # 0
         [B, C, R, R, R, R, I, R, R, R, R, R, I, R, R, R, R, I, R, R, R, R, R, C, B], # 1
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
         [B, C, R, R, R, R, I, R, R, R, R, R, C, O, O, O, O, C, R, R, R, R, R, C, B], # 15
         [B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B]] # 16

def getValue(position):
    return MAP[position.getX()][position.getY()]

def isWalkable(position):
    x = position.getX()
    y = position.getY()
    value = MAP[x][y]
    
    return value == R or value == I or value == C

def getNearestWalkablePosition(position, orientation):
    if not isWalkable(position):
        x = position.getX()
        y = position.getY()
        if orientation == Orientation.NORD or orientation == Orientation.SOUTH:
            p = Position(x+1, y)
            if isWalkable(p):
                return p
            p = Position(x-1, y)
            if isWalkable(p):
                return p
        elif orientation == Orientation.EAST or orientation == Orientation.WEST:
            p = Position(x, y+1)
            if isWalkable(p):
                return p
            p = Position(x, y-1)
            if isWalkable(p):
                return p
    else:
        return position


# to be defined
def findNearestIntersection(position):
    x = position.getX()
    y = position.getY()
    radius = 1
    for i in range(x-radius, x+radius +1):
        for j in range(y-radius, y+radius +1):
            if i < HEIGHT and i > 1 and j < WIDTH and j > 1:
                if MAP[i][j] == I:
                    return Position(i, j)
    
    return -1

def setNewObstacle(position):
    x = position.getX()
    y = position.getY()
    if x> 1 and x < HEIGHT:
        if y > 1 and y < WIDTH:
            MAP[x][y] = O