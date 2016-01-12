import numpy as np
import pygame
import sys
from DeadCreatures import DeadCreatures
from LivingCreatures import LivingCreatures
import time
from Graphics import Graphics
import Analyse
import matplotlib.pyplot as plt
import cPickle as pickle
import os
import fnmatch
from pytmx import *

__module__ = ''' This is to simulate life-environment interactions
             Also evolution over discrete time steps
             Check readme.txt for more info
             '''

# ENVIRONMENT CLASS___________________________________________________________
class Environment(object):
    ''' Creature Object to be tested in virtual environment '''
    
    # Initialises Environment
    def __init__(self, natVar=0.3, mapFile = "isometric_grass_and_water2.tmx", randomDeaths=0.):
        self.randomDeaths = randomDeaths
        self.mapFile = mapFile #This is the filename of the map to be used for the display of this simulation
        mydir = os.path.dirname(os.path.realpath(__file__))
        subdir = 'Maps'
        mapfilepath = os.path.join(mydir, subdir, self.mapFile)
        tmxdata = TiledMap(mapfilepath)
        self.__mapW = int(tmxdata.properties['Width'])
        self.__mapH = int(tmxdata.properties['Width'])
        self.__resources = self.resources_add(propWithRes=0.4)
        # self.__resources = {'[5 6]': Food(self, E=10., pos=np.array([5,6]), growRate=1.),
        #                   '[ 9 21]': Food(self, E=15., pos=np.array([9,21]), growRate=1.3),
        #                   '[ 9 22]': Food(self, E=9., pos=np.array([9,22]), growRate=1.7),
        #                   '[4 6]': Food(self, E=10., pos=np.array([4,6]), growRate=1.),
        #                   '[ 8 21]': Food(self, E=15., pos=np.array([8,21]), growRate=1.3),
        #                   '[4 7]': Food(self, E=9., pos=np.array([4,7]), growRate=1.7),
        #                   '[5 6]': Food(self, E=10., pos=np.array([5,6]), growRate=1.),
        #                   '[ 7 22]': Food(self, E=15., pos=np.array([7,22]), growRate=1.3),
        #                   '[10 20]': Food(self, E=9., pos=np.array([10,20]), growRate=1.7),
        #                   '[5 5]': Food(self, E=10., pos=np.array([5,5]), growRate=1.),
        #                   '[ 8 19]': Food(self, E=15., pos=np.array([8,19]), growRate=1.3),
        #                   '[3 4]': Food(self, E=9., pos=np.array([3,4]), growRate=1.7)}
        self.__natVar = natVar
        
        self.__dCreats = DeadCreatures(self)
        self.__lCreats = LivingCreatures(self, self.__dCreats)
        self.__lCreats.addCreature(1, 30*32, 20*32)
        self.__lCreats.addCreature(2, 30*32, 30*32)
        self.__lCreats.addCreature(3, 30*32, 10*32)
        self.__lCreats.addCreature(4, 7*32, 19*32)
        self.__maxCreatureNo = self.__lCreats.creatures() + self.__dCreats.creatures()
        print self.__lCreats

    def __repr__(self):
        return ("Living Creatures: %s\n" % (self.livingCreatures()) +
                "Dead Creatures: %s\n" % (self.deadCreatures()) +
                "Resources: %s\n" % (self.resources()))

    def __str__(self):
        return ("natVar=%s\n"%(self.natVar) +
                "Living Creatures: %s\n" % (self.livingCreatures()) +
                "Dead Creatures: %s\n" % (self.deadCreatures()) +
                "Resources: %s" % (self.resources()))
                
    def mapDims(self):
        return np.array([self.__mapW, self.__mapH])
    
    def maxCreatureNo(self):
        return self.__maxCreatureNo
    
    def setMaxCreatureNo(self, newMaxCreatNo):
        self.__maxCreatureNo = newMaxCreatNo
    
    def livingCreatures(self):
        return self.__lCreats

    #def livingCreatures_pop(self, creatureNo):
    #    return self.__livingCreatures.pop(creatureNo)

    #def livingCreatures_add(self, creature):
    #    self.__lCreats.add[creature.creatureNo()] = creature
    #    self.__maxCreatureNo = max(creature.creatureNo(), self.maxCreatureNo())
    
    #def livingCreatures_set(self, newLivingCreatures):
    #    assert isinstance(newLivingCreatures, dict), 'newLivingCreatures is not a dict'
    #    self.__livingCreatures = newLivingCreatures
        
    def deadCreatures(self):
        return self.__dCreats
    
    def clearTempDeadCreatures(self):
        self.__dCreats.clearDiffDeadCreats()
    
    def diffDeadCreatures(self):
        return self.__dCreats.diffDeadCreats()

    #def deadCreatures_add(self, creature):
    #    self.__deadCreatures[creature.creatureNo()] = creature
    #    self.__diffDeadCreatures[creature.creatureNo()] = creature

    def resources(self):
        return self.__resources
    
    def multiplyResources(self, factor):
        self.__resources *= factor

    def natVar(self):
        return self.__natVar

    def mapFileDump(self):
        return self.mapFile

    def resources_add(self, propWithRes=0.5, maxE = 20.):
        resources = np.zeros((3, self.__mapW, self.__mapH))
        #0 = energy, 1 = grow rate, 2 = max energy
        resources[0] = np.random.randint(5, 21, size=(self.__mapW, self.__mapH))
        resources[1] = np.random.rand(self.__mapW, self.__mapH)*2.
        resources[2] = np.zeros((self.__mapW, self.__mapH)) + maxE
        if self.mapFile is not None:
            mydir = os.path.dirname(os.path.realpath(__file__))
            subdir = 'Maps'
            mapfilepath = os.path.join(mydir, subdir, self.mapFile)
            tmxdata = TiledMap(mapfilepath)
            resKiller = np.ones((self.__mapW, self.__mapH))
            noRes = {8:0,9:0,10:0,11:0,22:0,23:0,28:2,29:2,30:2,31:2,32:2,33:2,33:2,34:2,35:2,36:2,37:2,38:2}
            for y in xrange(self.__mapH):
                for x in xrange(self.__mapW):
                    resKiller[x][y] = noRes.get(int(tmxdata.get_tile_properties(x,y,0)['tID']), 1)
            resKiller*np.random.rand(self.__mapW, self.__mapH)
        else:
            resKiller = np.random.rand(self.__mapW, self.__mapH)
            resKiller[resKiller > propWithRes] = 1
            resKiller[resKiller <= propWithRes] = 0
            resKiller = 1 - resKiller
        resources *= resKiller*0.6
        return resources
    
    def resources_grow(self):
        self.resources()[0] += ((((self.resources()[0]**3.)*(np.exp(-(((self.resources()[0]/7.)-1.)**2.))))/500.)*self.resources()[1] + 0.3)
        self.resources()[0].clip(0, self.resources()[2], out=self.resources()[0]) #vals > max --> max
    
    def step(self):
        self.resources_grow()
        self.__lCreats.allStep()
        #for creature in self.__livingCreatures.values():
        #    creature.step()
        
# ACTUAL TEST_________________________________________________________________
def LiveTesting(mapFile = None):
    
    t0 = time.time()
    if mapFile is not None:
        world = Environment(mapFile=mapFile)
        g = Graphics(mapFile=mapFile)
    else:
        world = Environment()
        g = Graphics()
    g.DisplayMap(livingCreatures = world.livingCreatures(), resources = world.resources())

    step = 0
    while True:
        while True:
            try:
                input_var = str(raw_input('Proceed to next step (y/n)?: ')).lower()
            except ValueError:
                print 'Valid input type please.'
            if input_var == 'y' or 'n':
                break
            else:
                print 'Valid option please (y/n).'

        if input_var == 'n':
            break
        elif input_var == 'y':
                world.step()
                step += 1
                print 'Environment stepped forward...updating map. step no: %d' % step
                g.DisplayMap(livingCreatures = world.livingCreatures(), resources = world.resources())

    pygame.quit()
    print time.time() - t0
    sys.exit()

def LiveTestingNoConfirm(mapFile = None):
    t0 = time.time()
    if mapFile is not None:
        world = Environment(mapFile=mapFile)
        g = Graphics(mapFile=mapFile)
    else:
        world = Environment()
        g = Graphics()
    g.DisplayMap(livingCreatures = world.livingCreatures(), resources = world.resources())

    step = 0
    while True:
        t1 = time.time()
        world.step()
        step += 1
        print 'Environment stepped forward...updating map. step no: %d, time taken: %s' % (step, str(time.time() - t1))
        g.DisplayMap(livingCreatures = world.livingCreatures(), resources = world.resources())

    pygame.quit()
    print time.time() - t0
    sys.exit()

def livingCreatures_infoFunc(livingCreatures):
    return livingCreatures.allCreats()

#def deadCreatures_infoFunc(deadCreatures, temp_deadCreatures):
#    diff_deadCreatures = [(k, v) for k, v in deadCreatures.iteritems() if k not in temp_deadCreatures]
#    deadCreatures_info = np.zeros((len(diff_deadCreatures), 3))
#    for i in xrange(len(diff_deadCreatures)):
#        deadCreatures_info[i] = np.array([diff_deadCreatures[i][1].creatureNo(), diff_deadCreatures[i][1].pos()[0], diff_deadCreatures[i][1].pos()[1]])
#    return deadCreatures_info
    
def diffDeadCreatures_infoFunc(deadCreatures):
    return deadCreatures.diffDeadCreats()

def totPop(step, worldHistory):
    return len(worldHistory[step][0])

def totERes(step, worldHistory):
    return np.sum(worldHistory[step][2])

def avgSpeed(step, worldHistory):
    totSpeed = sum(creature[7] for creature in worldHistory[step][0])
    if totSpeed == 0:
        return 0
    return float(totSpeed)/totPop(step, worldHistory)

def avgTR(step, worldHistory):
    totTR = sum(creature[5] for creature in worldHistory[step][0])
    if totTR == 0:
        return 0
    return float(totTR)/totPop(step, worldHistory)

def avgVis(step, worldHistory):
    totVis = sum(creature[9] for creature in worldHistory[step][0])
    if totVis == 0:
        return 0
    return float(totVis)/totPop(step, worldHistory)

def biodiversity(step, worldHistory):
    '''Simpson's definition of diversity:
    1 - (probability of two randomly chosen items being in the same group)
    '''
    creatSpec = Analyse.findSpecies(worldHistory[step][0])
    specPops = {}
    for creat in creatSpec:
        specPops[creat[1]] = specPops.get(creat[1], 0)+1
    arr = np.array(specPops.values(), dtype=float)
    return 1- (np.sum(arr*(arr-1))/(np.sum(arr)*(np.sum(arr)-1)))

def speedVis(creature):
    return creature[7], creature[9]

def speedReprThreshVis(creature):
    return creature[7], creature[5], creature[9]

def speedReprThreshMouth(creature):
    return creature[7], creature[5], creature[8]

def DisplaySim(worldHistory, resourcesGRMaxE, displayVisualSim=True, mapFile=None):
    if displayVisualSim:
        if mapFile is not None:
            g = Graphics(mapFile=mapFile)
        else:
            g = Graphics()
        g.DisplaySavedMap(worldHistory, resourcesGRMaxE)
        # pygame.quit()
        print 'Simulation Complete.....Analysing Data'
    popForStep = np.ndarray(len(worldHistory))
    for step in xrange(len(worldHistory)):
        popForStep[step] = totPop(step, worldHistory)

    POI = np.clip(np.argmax(popForStep), 10, len(worldHistory)-16)
    Analyse.plotForSteps(avgSpeed, 1, 231, len(worldHistory), "Avg Speed", 'ro-', 1, (worldHistory))
    Analyse.plotForSteps(totPop, 1, 232, len(worldHistory), "Population", 'bo-', 1, (worldHistory))
    #Analyse.plotForCreatures(speedVis, 1, 233, worldHistory[POI][0], 'Speed', 'Vis', 'Speed vs Vision in 914th step')
    Analyse.plotForSteps(avgVis, 1, 234, len(worldHistory), "Avg Vis", 'go-', 1, (worldHistory))
    Analyse.plotForSteps(totERes, 1, 235, len(worldHistory), "Resource Energy", 'yo-', 1, (worldHistory))
    Analyse.plotForSteps(biodiversity, 1, 236, len(worldHistory), "Biodiversity", 'bo-', 20, (worldHistory))
    #Analyse.plotForCreatures(speedReprThreshMouth, 2, 231, worldHistory[POI-5][0], 'Speed', 'Repr Thresh', 'Mouth Size', 'Genetics Plot in %dth step'%(POI-4))
    #Analyse.plotForCreatures(speedReprThreshMouth, 2, 232, worldHistory[POI][0], 'Speed', 'Repr Thresh', 'Mouth Size', 'Genetics Plot in %dth step'%(POI+1))
    #Analyse.plotForCreatures(speedReprThreshMouth, 2, 233, worldHistory[POI+5][0], 'Speed', 'Repr Thresh', 'Mouth Size', 'Genetics Plot in %dth step'%(POI+6))
    #Analyse.plotForCreatures(speedReprThreshMouth, 2, 234, worldHistory[POI+25][0], 'Speed', 'Repr Thresh', 'Mouth Size', 'Genetics Plot in %dth step'%(POI+26))
    #Analyse.plotForCreatures(speedReprThreshMouth, 2, 235, worldHistory[POI+50][0], 'Speed', 'Repr Thresh', 'Mouth Size', 'Genetics Plot in %dth step'%(POI+51))
    Analyse.plotForCreatures(speedReprThreshMouth, 2, 121, worldHistory[899][0], 'Speed', 'Repr Thresh', 'Mouth Size', 'Genetics Plot in %dth step'%(POI))
    Analyse.plotForCreatures(speedReprThreshMouth, 2, 122, worldHistory[719][0], 'Speed', 'Repr Thresh', 'Mouth Size', 'Genetics Plot in %dth step'%(POI), True)
    #Analyse.plotForCreatures(speedReprThreshMouth, 3, 111, worldHistory[POI][0], 'Speed', 'Repr Thresh', 'Mouth Size', 'Genetics Plot in %dth step'%(POI), True)
    #Analyse.findSpecies(worldHistory[POI+599][0], True)

    plt.show()

def DisplayFrame(worldFrame, resourcesGRMaxE, mapFile, frameNo):
    creatSpec = Analyse.findSpecies(worldFrame[0])
    if np.max(creatSpec[:,1])==0:
        colours = np.array(creatSpec[:,1])
    else:
        colours = (np.array(creatSpec[:,1]))/float(np.max(creatSpec[:,1]))
    Analyse.plotForCreatures(speedReprThreshMouth, 1, 111, worldFrame[0], 'Speed', 'Repr Thresh', 'Mouth Size', 'Genetics Plot in %dth step'%(frameNo+1))

    plt.show()

    if mapFile is not None:
        Graphics(mapFile=mapFile).DisplaySavedMapFrame(worldFrame, resourcesGRMaxE, frameNo, colours, creatSpec)
    else:
        Graphics().DisplaySavedMapFrame(worldFrame, resourcesGRMaxE, frameNo, colours, creatSpec)

def DisplaySavedSim(displayVisualSim=True, frameNo=None):
    filenames = []
    mydir = os.path.dirname(os.path.realpath(__file__))
    subdir = 'Simulations/'
    sim_dir = os.path.join(mydir, subdir)
    for file in os.listdir(sim_dir):
        if fnmatch.fnmatch(file, '*.dat'):
            filenames.append(file)

    list.sort(filenames, reverse=True)

    print 'Simulations (date ordered):'
    for i, o in enumerate(filenames):
        print str(i+1) + ': ' + o

    try:
        choice = int(raw_input('Input number simulation number: '))
    except ValueError:
        print 'Please input an integer.'

    with open(sim_dir + filenames[choice-1], 'rb') as input:
        data = pickle.load(input)
        worldHistory = data[0]
        resourcesGRMaxE = data[1]
        natVar = data[2]
        if len(data) == 4:
            mapFile = data[3]
        else:
            mapFile = None
    if frameNo is None:    
        DisplaySim(worldHistory, resourcesGRMaxE, displayVisualSim, mapFile)
    else:
        DisplayFrame(worldHistory[frameNo], resourcesGRMaxE, mapFile, frameNo)

def dump(obj, nested_level=0, output=sys.stdout):
    spacing = '   '
    if type(obj) == dict:
        print >> output, '%s{' % ((nested_level) * spacing)
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print >> output, '%s%s:' % ((nested_level + 1) * spacing, k)
                dump(v, nested_level + 1, output)
            else:
                print >> output, '%s%s: %s' % ((nested_level + 1) * spacing, k, v)
        print >> output, '%s}' % (nested_level * spacing)
    elif type(obj) == list:
        print >> output, '%s[' % ((nested_level) * spacing)
        for v in obj:
            if hasattr(v, '__iter__'):
                dump(v, nested_level + 1, output)
            else:
                print >> output, '%s%s' % ((nested_level + 1) * spacing, v)
        print >> output, '%s]' % ((nested_level) * spacing)
    else:
        print >> output, '%s%s' % (nested_level * spacing, obj)

def quickCopy(d):
    return pickle.loads(pickle.dumps(d, -1))

def test_Res(steps=300, displayVisualSim=True):
    RunSim(steps)
    DisplaySavedSim(displayVisualSim)