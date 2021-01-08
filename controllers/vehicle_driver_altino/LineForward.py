# Compute steering angle using camera images

UNKNOWN = -2
FILTER_SIZE = 3
NUM_ZONES = 15
MAX_STEERING_ANGLE = 1
MIN_STEERING_ANGLE = -1

STEERING_ANGLE_STEP = ((MAX_STEERING_ANGLE - MIN_STEERING_ANGLE) / NUM_ZONES)

MIDDLE_ZONE = int(NUM_ZONES/2)

LINE_REFERENCE_COLOR = [228, 228, 42] # yellow
LINE_COLOR_TOLERANCE = 30

class LineForwarder:

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

        # compute zone width
        self.zoneSpace = self.cameraWidth / NUM_ZONES

    # process data from camera
    def processCameraImage(self):
        # if no pixel of line reference color is found, the line is lost
        lineNotFund = True

        # clear zone's pixel count
        for i in range(NUM_ZONES):
            self.zones[i] = 0

        # get image from camera
        image = self.camera.getImageArray()

        # scanning column by column
        for j in range(self.cameraHeight):
            for i in range(self.cameraWidth):
                # if pixel is similar to line reference color add pixel to zone count
                if self.colorDifference(image[i][j]) < LINE_COLOR_TOLERANCE:
                    self.zones[int(i / self.zoneSpace)] += 1
                    lineNotFund = False
        
        if lineNotFund:
            return UNKNOWN

        # find index of greatest zone
        index = self.indexOfMax(self.zones)

        # debug
        # print(self.zones)

        # if the middle zone is the greatest return 0
        if index == MIDDLE_ZONE:
            return 0
        else:
            # return angle according to greatest zone
            return MIN_STEERING_ANGLE + index * STEERING_ANGLE_STEP

    # compute index of greatest value in the array
    def indexOfMax(self, array):
        index = 0
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


    def getNewSteeringAngle(self):
        return self.processCameraImage()
        