
from Utils import Color
UNKNOWN = 123456789
FILTER_SIZE = 3
KP = 0.25
KI = 0.006
KD = 2

class LineForwarder:
    def __init__(self, camera):
        self.camera = camera    

        self.cameraFov = camera.getFov()
        self.cameraWidth = camera.getWidth()
        self.cameraHeight = camera.getHeight()
        self.numberOfPixels = self.cameraWidth * self.cameraHeight - 1
        self.lineColorReference = [228, 228, 42]

        self.firstCall = True
        self.oldValue = []
        self.oldPidValue = 0.0
        self.integral = 0.0
        self.pid_need_reset = False
        for i in range(FILTER_SIZE):
            self.oldValue.append(0)
    
    def processCameraImage(self):
        sum = 0
        pixelCount = 0
        x = 0
        image = self.camera.getImageArray()

        for i in range(self.cameraWidth):
            for j in range(self.cameraHeight):
                x += 1
                # if(i == 127 and j == 63):
                    # print("pixel " + str(i) + " " + str(j) + ": " + str(image[i][j]))
                # pixelColor = Color(image[i][j])

                if self.colorDifference(image[i][j]) < 30:
                    sum += x % self.cameraWidth
                    pixelCount += 1
        
        if pixelCount == 0:
            return UNKNOWN

        return (sum / pixelCount / self.cameraWidth - 0.5) * self.cameraFov

    def filterAngle(self, newValue):

        if self.firstCall or newValue == UNKNOWN:
            self.firstCall = False
            for i in range(FILTER_SIZE):
                self.oldValue[i] = 0.0
        else:
            for i in range(FILTER_SIZE - 1):
                self.oldValue[i] = self.oldValue[i + 1]

        if newValue == UNKNOWN:
            return UNKNOWN
        else:
            self.oldValue[FILTER_SIZE - 1] = newValue
            sum = 0.0
            for i in range(FILTER_SIZE):
                sum += self.oldValue[i]
            return sum / FILTER_SIZE

    def applyPID(self, lineAngle):
        if self.pid_need_reset:
            self.oldPidValue = lineAngle
            self.integral = 0.0
            self.pid_need_reset = False
        
        if (self.oldPidValue >= 0 and lineAngle < 0) or (self.oldPidValue < 0 and lineAngle >= 0):
            self.integral = 0.0

        diff = lineAngle - self.oldPidValue

        if self.integral < 30 and self.integral > -30:
            self.integral += lineAngle

        self.oldPidValue = lineAngle
        return KP * lineAngle + KI * self.integral + KD * diff

        
    def colorDifference(self, pixelColor):
        referenceColor = self.lineColorReference
        difference = 0
        
        """difference += abs(pixelColor.getRed() - referenceColor.getRed())
        difference += abs(pixelColor.getGreen() - referenceColor.getGreen())
        difference += abs(pixelColor.getBlue() - referenceColor.getBlue())"""

        difference += abs(pixelColor[0] - referenceColor[0])
        difference += abs(pixelColor[1] - referenceColor[1])
        difference += abs(pixelColor[2] - referenceColor[2])


       # print("difference: " + str(difference))

        return difference

    def getNewSteeringAngle(self):
        lineAngle = self.filterAngle(self.processCameraImage())
        if lineAngle != UNKNOWN:
            angle = self.applyPID(lineAngle)
            return angle
        else:
            self.pid_need_reset = True