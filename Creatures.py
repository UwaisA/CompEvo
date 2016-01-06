import numpy as np
import os
from pytmx import TiledMap

class Creatures(object):
    
    # For creatures array:
    # 0: creature No, 1: pos x, 2: pos y, 3: energy, 4: NumOff
    # 5: ReprThresh, 6: Aggr, 7: Speed, 8: MouthSize, 9: Vision
    def __init__(self, enviro):
        self.__enviro = enviro
        mydir = os.path.dirname(os.path.realpath(__file__))
        subdir = 'Maps'
        mapfilepath = os.path.join(mydir, subdir, enviro.mapFile)
        tmxdata = TiledMap(mapfilepath)
        self.pxPerTile = int(tmxdata.get_tile_properties(0,0,0)['height']/2.)
        self._creatsArr = np.zeros((4,10)) #start with 4 creatures
    
    def __repr__(self):
        return "Creatures container: %d creatures, %d capacity"%(self.creatures(), self.capacity())
    
    def enviro(self):
        return self.__enviro
    
    def creatures(self):
        return len(self._creatsArr[self._creatsArr[:,0] > 0])
    
    def isFull(self):
        return np.all(self._creatsArr[:,0] != 0)
    
    def isEmpty(self):
        return np.all(self._creatsArr[:,0] == 0)
    
    def capacity(self):
        return len(self._creatsArr)
    
    def doubleCapacity(self):
        arrShape = self._creatsArr.shape
        newShape = (arrShape[0]*2, arrShape[1])
        self._creatsArr.resize(newShape, refcheck=False)