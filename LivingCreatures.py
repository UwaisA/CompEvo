import numpy as np
from Creatures import Creatures
import time

class LivingCreatures(Creatures):
    
    # For creatures array:
    # 0: creature No, 1: pos x, 2: pos y, 3: energy, 4: NumOff
    # 5: ReprThresh, 6: Aggr, 7: Speed, 8: MouthSize, 9: Vision
    
    def __init__(self, enviro, deadCreatures):
        Creatures.__init__(self, enviro)
        self.__deadCreats = deadCreatures
    
    def add(self, toBeAdded):
        toBeAdded = np.array(toBeAdded)
        if len(toBeAdded.shape) == 1:
            toBeAdded = np.array([toBeAdded])
        assert toBeAdded[0].shape == self._creatsArr[0].shape, 'toBeAdded incorrect shape'
        #make sure there's enough space
        free = self.freeSpaces()
        while len(free) < len(toBeAdded):
            self.doubleCapacity()
            free = self.freeSpaces()
        #add creatures
        self._creatsArr[free[:len(toBeAdded)]] = toBeAdded
    
    def addCreature(self, creatNo, posX=0, posY=0, E=6., N_o=2., T_r=10., Agg=0., Speed=4., MouthSize=5., Vis=1.):
        self.add(np.array([creatNo, posX, posY, E, N_o, T_r, Agg, Speed, MouthSize, Vis]))
    
    def freeSpaces(self):
        return np.argwhere(self._creatsArr[:,0]==0).flatten()
    
    def genArr(self):
        return self._creatsArr[:,4:]
    
    def energy(self):
        return self._creatsArr[:,3]
    
    def setEnergy(self, newEnergyArr):
        self._creatsArr[:,3] = newEnergyArr
    
    def pos(self):
        return self._creatsArr[:,1:3].astype(int)
    
    def gridPos(self):
        return (self.pos()/self.pxPerTile).astype(int)
    
    def creatureNo(self):
        return self._creatsArr[:,0]
    
    def allCreats(self):
        return self._creatsArr[self._creatsArr[:,0] > 0]
    
    def costOfLiv(self):
        # energy, aggr, speed, vision - non-zero vals
        out = self._creatsArr*np.array([0,0,0,1/12.,0,0,0.5,0.25,0,0])
        out[:,9] = self._creatsArr[:,9].astype(int)*(1/12.)
        return np.sum(out, axis=1)
    
    def killProportion(self, propToDie):
        toDie = np.argwhere(self._creatsArr[:,0] > 0).flatten()
        self.die(np.random.choice(toDie, size=int(propToDie*len(toDie)), replace=False))
    
    def starveCheck(self, randDeaths):
        randKiller = np.random.rand(self.capacity()) >= randDeaths
        self.setEnergy(self.energy() * randKiller)
        toDie = np.argwhere(np.logical_and(self.energy()<=0, self.creatureNo()>0)).flatten()
        self.die(toDie)
    
    def die(self, toDie):
        '''
        toDie should be array of indicies of creatsArr to be moved to deadCreats
        '''
        if len(toDie) == 0:
            return
        if np.any(self._creatsArr[toDie][:,0] == 0):
            print 'creature no 0 cannot be moved to dead creats'
        self.__deadCreats.add(self._creatsArr[toDie])
        self._creatsArr[toDie] = 0
    
    def allMove(self):
        #self._creatsArr[:,1:3] += (np.random.rand(self.capacity(), 2)*2-1)*(np.array([self._creatsArr[:,7]*3]).T) - random movement
        mapDims = self.enviro().mapDims()
        dirDecisions = self.vDirDecision(self.gridPos()[:,0], self.gridPos()[:,1], self._creatsArr[:,7],
                        self._creatsArr[:,9].astype(int), self.costOfLiv(), mapDims[0], mapDims[1])
        #add randomness to non-movers
        dirDecisions += np.array([np.all(dirDecisions==np.array([0,0]), axis=1)]).T*(1-(np.random.rand(self.capacity(),
                        2)))*np.random.choice([-1, 1], size=(self.capacity(), 2))
        #unit vectorise
        dirDecisions /= np.array([np.linalg.norm(dirDecisions, axis=1)]).T
        #scale with speed
        dirDecisions *= np.array([self._creatsArr[:,7]*3]).T
        self._creatsArr[:,1:3] += dirDecisions
        self._creatsArr[:,1:3] %= self.enviro().mapDims()*self.pxPerTile
    
    def vDirDecision(self, gridPosX, gridPosY, speed, vis, costOfLiv, mapW, mapH):
        out = np.ndarray((len(gridPosX), 2), float)
        lims = np.ndarray((len(gridPosX), 6), int)
        lims[:,0] = gridPosX-vis
        lims[:,1] = gridPosX+vis+1
        lims[:,2] = gridPosY-vis
        lims[:,3] = gridPosY+vis+1
        lims[:,4] = -lims[:,0]
        lims[:,5] = -lims[:,2]
        lims = np.clip(lims, [0,0,0,0,0,0], [mapW, mapW, mapH, mapH, mapW+1, mapH+1])
        speedFactorMult = self.pxPerTile/(speed*3)*costOfLiv
        res0 = self.enviro().resources()[0]
        creatExists = self._creatsArr[:,0]>0
        #creatExists = np.argwhere(self._creatsArr[:,0]>0).flatten()
        for i in xrange(len(gridPosX)):
        #for i in creatExists:
            if creatExists[i]:
                toLookAt = res0[lims[i,0]:lims[i,1], lims[i,2]:lims[i,3]]
                lookAtDist = distFactor(2*vis[i]+1)*speedFactorMult[i]
                addAtPos(lookAtDist, toLookAt, lims[i,4:6])
                randRot = np.random.rand(2) > .5
                if randRot[0]:
                    lookAtDist = np.flipud(lookAtDist)
                if randRot[1]:
                    lookAtDist = np.fliplr(lookAtDist)
                maxDir = np.argmax(lookAtDist)
                maxDir0, maxDir1 = maxDir/(2*vis[i]+1) - vis[i], maxDir%(2*vis[i]+1) - vis[i]
                if randRot[0]:
                    maxDir0 = -maxDir0
                if randRot[1]:
                    maxDir1 = -maxDir1
                out[i,0] = maxDir0
                out[i,1] = maxDir1
        return out
    
    def allEat(self):
        posxy = self.gridPos()
        res0 = self.enviro().resources()[0]
        for i in np.argwhere(self._creatsArr[:,0]>0).ravel():
            energyIncrease = min(self._creatsArr[i,8], res0[posxy[i,0], posxy[i,1]])
            self._creatsArr[i,3] += energyIncrease
            res0[posxy[i,0], posxy[i,1]] -= energyIncrease
        #non-functioning vectorized version
        #food = np.copy(self.enviro().resources()[0, positions[:,0], positions[:,1]])
        #food = np.clip(food, 0, self._creatsArr[:,8])
        #self.enviro().resources()[0, positions[:,0], positions[:,1]] -= food
        #self.setEnergy(self.energy() + food)
        self.allReproduce()
    
    def allReproduce(self):
        reproducing = np.logical_and(self.energy() > self._creatsArr[:,5], self.creatureNo()>0)
        if np.any(reproducing):
            natVar = self.enviro().natVar()
            repros = np.copy(self._creatsArr[reproducing])
            repros[:,3] /= repros[:,4]
            repros = np.repeat(repros, repros[:,4].astype(int), axis=0)
            self.enviro().setMaxCreatureNo(self.enviro().maxCreatureNo()+len(repros))
            repros[:,0] = np.arange(self.enviro().maxCreatureNo()+1, self.enviro().maxCreatureNo()+1+len(repros))
            genVar = ((np.random.rand(len(repros), len(repros[0])-4)*2*natVar)-natVar)*np.array([0,1,0,1,1,1])
            repros[:,4:] += genVar
            np.abs(repros[:,4:], repros[:,4:])
            self.die(np.argwhere(reproducing).flatten())
            self.add(repros)
    
    def allStep(self):
        self.allMove()
        self.setEnergy(self.energy() - self.costOfLiv())
        self.starveCheck(self.enviro().randomDeaths)
        self.allEat()

distFactorOut = np.array([[0]])
def distFactor(size):
    assert size%2 == 1, 'size must be odd'
    global distFactorOut
    if len(distFactorOut) == size:
        return distFactorOut
    if len(distFactorOut) > size:
        start = (len(distFactorOut)-size)/2
        end = start + size
        return distFactorOut[start:end,start:end]
    if len(distFactorOut) < size:
        out=np.zeros((size,size))-(int(size)/2)
        for i in xrange(int(size)/2):
            addAtPos(out, np.ones((size-(i+1)*2, size-(i+1)*2)), (i+1, i+1))
        distFactorOut = out
        return out

def unitVec(arr):
    if np.all(arr==0):
        return arr
    return arr/np.linalg.norm(arr)

#method posted by EwyynTomato on StackOverflow
#    - mat1  : matrix to be added
#    - mat2  : add this matrix to mat1
#    - xycoor: tuple (x,y) containing coordinates
def addAtPos(mat1, mat2, xycoor):
    size_x, size_y = np.shape(mat2)
    coor_x, coor_y = xycoor
    end_x, end_y   = (coor_x + size_x), (coor_y + size_y)
    mat1[coor_x:end_x, coor_y:end_y] += mat2
    return mat1