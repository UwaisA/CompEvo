import numpy as np
import os
from pytmx import *

__module__ = ''' This is to classify creature objects in environment
             Check readme.txt for more info
             '''

# CREATURE CLASS ______________________________________________________________
class Creature(object):
    ''' Creature Object to be tested in virtual environment '''
    # pxPerTile = 32

    # Initialises Creature with position, genetics and physical condition
    def __init__(self, creatureNo, creature=None, environment=None,
                    pos=np.array([0,0]), N_o=2., T_r=10., Agg=0., Speed=3.,
                    MouthSize=2., Vis=1., E=6.):
        self.__enviro = environment
        self.__creatureNo = creatureNo
        if creature != None:
            pos = creature.pos()
            self.__enviro = creature.enviro()
            rand = ranPN(posNeg = self.enviro().natVar()*100., size=5)
            T_r = creature.gen()['ReprThresh'] + rand[0]/100.
            Speed = abs(creature.gen()['Speed']+rand[1]/100.)
            Vis = abs(creature.gen()['Vis']+rand[2]/100.)
            MouthSize = abs(creature.gen()['MouthSize']+rand[3]/100.)
            E = (int)(creature.physChar()['energy']/creature.gen()['NumOff'])
        
        self.__gen = {'NumOff': N_o, 'ReprThresh': T_r, 'Aggr': Agg,
                      'Speed': Speed, 'MouthSize': MouthSize, 'Vis': Vis}
        self.__physChar = {'energy': E}
        self.__pos = pos
        mapFile = "isometric_grass_and_water2.tmx" #This is the filename of the map to be used for the display of this simulation
        mydir = os.path.dirname(os.path.realpath(__file__))
        subdir = 'Maps'
        mapfilepath = os.path.join(mydir, subdir, mapFile)
        tmxdata = TiledMap(mapfilepath)
        self.pxPerTile = int(tmxdata.get_tile_properties(0,0,0)['height']/2.)
    
    def __repr__(self):
        return "Creature: pos=%s"%(self.__pos)

    def __str__(self):
        return ("pos=%s\ngen=%s\nphysChar=%s"%(self.pos(), self.gen(), self.physChar()))

    # Returns current creature position
    def pos(self):
        return self.__pos
    
    def gridPos(self):
        return self.pos()/self.pxPerTile

    # Returns creature genetics
    def gen(self):
        return self.__gen

    # Returns current creature physical condition
    def physChar(self):
        return self.__physChar

    def enviro(self):
        return self.__enviro

    def creatureNo(self):
        return self.__creatureNo

    def setPos(self, newPos):
        self.__pos = newPos

    def setEnergy(self, newEnergy):
        self.__physChar['energy'] = newEnergy

    def step(self):
        self.move()
        self.__physChar['energy'] -= self.costOfLiv()
        if self.physChar()['energy'] <= 0:
            self.die()
        elif self.enviro().resources()[0][self.gridPos()[0]][self.gridPos()[1]] > 0:
            self.eat()
        #resolve conflict - eat or be eaten
        #if(self.pos() in (i.pos() for i in self.__enviro.livingCreatures)):

    def eat(self):
        energyIncrease = min(self.gen()['MouthSize'], #can be eaten vs E available
            self.enviro().resources()[0][self.gridPos()[0]][self.gridPos()[1]])
        self.setEnergy(self.physChar()['energy'] + energyIncrease)
        self.enviro().resources()[0][self.gridPos()[0]][self.gridPos()[1]] -= energyIncrease
        if(self.physChar()['energy'] > self.gen()['ReprThresh']):
            self.reproduce()

    def move(self):
        x = int(self.gridPos()[0])
        y = int(self.gridPos()[1])
        goodVis = (int) (self.gen()['Vis'])
        mapW = self.enviro().mapDims()[0]
        mapH = self.enviro().mapDims()[1]
        toLookAt = np.copy(self.enviro().resources()[0][max(x-goodVis, 0):min(x+goodVis+1, mapW),
                                                        max(y-goodVis, 0):min(y+goodVis+1, mapH)])
        lookAtDist = distFactor(2*goodVis+1)*self.pxPerTile/(self.gen()['Speed']*3)*self.costOfLiv()
        addAtPos(lookAtDist, toLookAt, (abs(np.clip((x-goodVis), -mapW-1, 0)), abs(np.clip((y-goodVis), -mapH-1, 0))))
        #print toLookAt, self.gridPos(), goodVis
        maxLoc = np.argmax(lookAtDist)
        maxDir = unitVec(np.array([(int) (maxLoc/(2*goodVis+1)) - goodVis, (int) (maxLoc%(2*goodVis+1)) - goodVis]))
        #newPos = ranPN(self.gen()['Speed']*3, 2)+self.pos()
        if str(maxDir)=='[0 0]' or goodVis == 0:
            newMov = ranPN(self.gen()['Speed']*3, 2)
        else:
            newMov = maxDir*((int)(self.gen()['Speed']*3))
        #bounding the creature to the map
        self.setPos((newMov+self.pos())%(mapH*self.pxPerTile))

    def die(self):
        try:
            self.enviro().deadCreatures_add(self)
            self.enviro().livingCreatures_pop(self.__creatureNo)
        except KeyError:
            print 'creature already dead'

    def reproduce(self):
        #kill parent
        self.die()
        #create N_o children in living creatures
        for i in xrange(int(self.gen()['NumOff'])):
            key = self.enviro().maxCreatureNo() + 1
            creature = Creature(key, self)
            self.enviro().livingCreatures_add(creature)
    
    def costOfLiv(self):
        aggrFactor = self.gen()['Aggr']/2.
        speedFactor = self.gen()['Speed']/5.
        visionFactor = self.gen()['Vis']/6.
        energyFactor = self.physChar()['energy']/12.
        return aggrFactor+speedFactor+energyFactor+visionFactor
    
def ranPN(posNeg, size=None):
    if size == None:
        return np.random.randint(-posNeg, 1+posNeg)
    else:
        return np.random.randint(-posNeg, 1+posNeg, size)

def distFactor(size):
    assert size%2 == 1, 'size must be odd'
    out=np.zeros((size,size))-(int(size)/2)
    counter = 1
    while out[int(size)/2, int(size)/2]!=0:
        addAtPos(out, np.ones((size-counter*2, size-counter*2)), (counter, counter))
        counter += 1
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
    mat1[coor_x:end_x, coor_y:end_y] = mat1[coor_x:end_x, coor_y:end_y] + mat2
    return mat1