import numpy as np
from Creatures import Creatures

class DeadCreatures(Creatures):
    
    # For creatures array:
    # 0: creature No, 1: pos x, 2: pos y, 3: energy, 4: NumOff
    # 5: ReprThresh, 6: Aggr, 7: Speed, 8: MouthSize, 9: Vision
    
    def __init__(self, enviro):
        Creatures.__init__(self, enviro)
        self.nextFreeSpace = 0
        self.diffDeadCreatsPos = 0
    
    def add(self, toBeAdded):
        if len(toBeAdded.shape) == 1:
            toBeAdded = np.array([toBeAdded])
        assert toBeAdded[0].shape == self._creatsArr[0].shape, 'toBeAdded incorrect shape'
        for creat in toBeAdded:
            self._creatsArr[self.nextFreeSpace] = creat
            self.nextFreeSpace += 1
            if self.isFull():
                self.doubleCapacity()
    
    def isFull(self):
        return self.nextFreeSpace >= self.capacity()
    
    def clearDiffDeadCreats(self):
        self.diffDeadCreatsPos = self.nextFreeSpace
    
    def diffDeadCreats(self):
        toReturn = np.ones((self.capacity()), dtype=bool)
        toReturn[:self.diffDeadCreatsPos] = False
        toReturn[self.nextFreeSpace:] = False
        return self._creatsArr[toReturn]