
DISABLED = 0
ENABLED = 1
class ManualDrive:

    def __init__(self, keyboard):
        self.keyboard = keyboard

        self.speed = 0.0
        self.angle = 0.0

        self.status = DISABLED


    def update(self):
        if self.isEnabled():
            self.updateCommands()

    def updateCommands(self):
        # get current state
        speed = self.speed
        angle = self.angle
        # logger.debug("Current Key: " + str(currentKey))

        currentKey = self.keyboard.getKey()
        # keyboard controlls 
        # accelerate
        if currentKey == self.keyboard.keyboard.UP:
            if speed < 0:
                speed += 0.02
            else:
                speed += 0.01
        
        # break
        elif currentKey == self.keyboard.keyboard.DOWN:
            if speed > 0:
                speed -= 0.02
            else:
                speed -= 0.01
        
        # turn left
        elif currentKey == self.keyboard.keyboard.LEFT:
            angle -= 0.05

        # turn right
        elif currentKey == self.keyboard.keyboard.RIGHT:
            angle += 0.05
        
        # handbreak
        elif currentKey == ord(' '):
            speed /= 4
        
        # update state
        self.speed = speed
        self.angle = angle

    def getSpeed(self):
        return self.speed

    def getAngle(self):
        return self.angle
    
    def isEnabled(self):
        return self.status != DISABLED

    def enable(self):
        self.status = ENABLED

    def disable(self):
        self.status = DISABLED


    