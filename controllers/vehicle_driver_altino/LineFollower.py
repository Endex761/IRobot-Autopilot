# Compute steering angle using camera images
from Constants import UNKNOWN
from Utils import logger

# constants  
NUM_ZONES = 13          # number of vertical zones of the image
MAX_STEERING_ANGLE = 1  # max steering angle allow to line following
MIN_STEERING_ANGLE = -1 # min steering angle allow to line folloving

# compute steering angle step for each zone of the image
STEERING_ANGLE_STEP = ((MAX_STEERING_ANGLE - MIN_STEERING_ANGLE) / NUM_ZONES)

# compute middle zone index
MIDDLE_ZONE = int(NUM_ZONES/2)

# set line reference color and tolerance 
LINE_REFERENCE_COLOR = [228, 228, 42] # yellow
LINE_COLOR_TOLERANCE = 60

# class to handle line following
class LineFollower:

    def __init__(self, camera):
        # get camera from Altino
        self.camera = camera    

        # get image dimensions
        self.cameraWidth = camera.getWidth()
        self.cameraHeight = camera.getHeight()

        # initialize image zone counters
        self.zones = []
        for i in range(NUM_ZONES):
            self.zones.append(0)

        # compute zone width, the image is dived in NUM_ZONES vertically of zoneSpace width
        self.zoneSpace = self.cameraWidth / NUM_ZONES

        # true if line is lost
        self.lineLost = False

        # angle to be set to follow the line
        self.newSteeringAngle = UNKNOWN

        # index of the last zone with the yellow line detected
        self.lastLineKnownZone = UNKNOWN

    # process data from camera
    def processCameraImage(self):
        # if no pixel of line reference color is found, the line is lost

        # clear zone's pixel count
        for i in range(NUM_ZONES):
            self.zones[i] = 0

        # get image from camera
        image = self.camera.getImageArray()

        # scanning column by column
        for i in range(self.cameraWidth):
            for j in range(self.cameraHeight):
                # if pixel is similar to line reference color add pixel to zone count
                if self.colorDifference(image[i][j]) < LINE_COLOR_TOLERANCE:
                    self.zones[int(i / self.zoneSpace)] += 1
        
        # lost line
        if sum(self.zones) == 0:
            #logger.debug("Last known line: " + str(self.lastLineKnownZone))
            return UNKNOWN

        # find index of greatest zone
        index = self.indexOfMax(self.zones)
        if index != -1:
            self.lastLineKnownZone = index

        # debug
        # print(self.zones)

        # if the middle zone is the greatest return 0
        if index == MIDDLE_ZONE:
            return 0
        elif index != -1:
            # return angle according to greatest zone
            return MIN_STEERING_ANGLE + index * STEERING_ANGLE_STEP
        else:
            return 0

    # compute index of greatest value in the array
    def indexOfMax(self, array):
        index = -1
        max = array[0]
        for i in range(1, NUM_ZONES - 1):
            if array[i] > max:
                max = array[i]
                index = i
        
        return index
    
    # compute color difference
    def colorDifference(self, pixelColor):
        difference = 0
        difference += abs(pixelColor[0] - LINE_REFERENCE_COLOR[0])
        difference += abs(pixelColor[1] - LINE_REFERENCE_COLOR[1])
        difference += abs(pixelColor[2] - LINE_REFERENCE_COLOR[2])

        return difference

    # update steering angle
    def update(self):
        self.newSteeringAngle = self.processCameraImage()
        self.lineLost = self.newSteeringAngle == UNKNOWN
        if self.lineLost:
            self.newSteeringAngle = 0.0

    # return steereng angle
    def getNewSteeringAngle(self):
        return self.newSteeringAngle

    # return if line is lost
    def isLineLost(self):
        return self.lineLost

    # return steereng angle based on last index where the line appeared, is usually called when line is lost
    def getSteeringAngleLineSearching(self):
        if self.lastLineKnownZone == MIDDLE_ZONE:
            return 0
         
        return (MIN_STEERING_ANGLE + self.lastLineKnownZone * STEERING_ANGLE_STEP) * 1

    # reset last line zone, this allow external control to line search
    def resetLastLineKnownZone(self, angle=0):
        if angle != 0 :
            self.lastLineKnownZone = int((angle - MIN_STEERING_ANGLE) / STEERING_ANGLE_STEP)
        else:
            self.lastLineKnownZone=MIDDLE_ZONE
            
        