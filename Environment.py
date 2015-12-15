import numpy as np
import pygame
import sys
from Creature import Creature
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
    def __init__(self, natVar=0.3, mapFile = "isometric_grass_and_water2.tmx"):
        self.__livingCreatures = {1: Creature(creatureNo=1, environment=self, pos=np.array([100,2900])),
                                  2: Creature(creatureNo=2, environment=self, pos=np.array([1600,1700])),
                                  3: Creature(creatureNo=3, environment=self, pos=np.array([2600,420]))}
        self.__deadCreatures = {}
        self.mapFile = mapFile #This is the filename of the map to be used for the display of this simulation
        mydir = os.path.dirname(os.path.realpath(__file__))
        subdir = 'Maps'
        mapfilepath = os.path.join(mydir, subdir, self.mapFile)
        tmxdata = TiledMap(mapfilepath)
        self.__mapW = int(tmxdata.properties['Width'])
        self.__mapH = int(tmxdata.properties['Width'])
        self.__maxCreatureNo = len(self.livingCreatures())+ len(self.deadCreatures())
        self.__diffDeadCreatures = {}
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
        print self.__livingCreatures

    def __repr__(self):
        return ("Living Creatures: %s" % (self.livingCreatures()) +
                "Dead Creatures: %s" % (self.deadCreatures()) +
                "Resources: %s" % (self.resources()))

    def __str__(self):
        return ("natVar=%s"%(self.natVar) +
                "Living Creatures: %s" % (self.livingCreatures()) +
                "Dead Creatures: %s" % (self.deadCreatures()) +
                "Resources: %s" % (self.resources()))
                
    def mapDims(self):
        return np.array([self.__mapW, self.__mapH])
    
    def maxCreatureNo(self):
        return self.__maxCreatureNo
    
    def livingCreatures(self):
        return self.__livingCreatures

    def livingCreatures_pop(self, creatureNo):
        return self.__livingCreatures.pop(creatureNo)

    def livingCreatures_add(self, creature):
        self.__livingCreatures[creature.creatureNo()] = creature
        self.__maxCreatureNo = max(creature.creatureNo(), self.maxCreatureNo())
    
    def livingCreatures_set(self, newLivingCreatures):
        assert isinstance(newLivingCreatures, dict), 'newLivingCreatures is not a dict'
        self.__livingCreatures = newLivingCreatures
        
    def deadCreatures(self):
        return self.__deadCreatures
    
    def clearTempDeadCreatures(self):
        self.__diffDeadCreatures.clear()
    
    def diffDeadCreatures(self):
        return self.__diffDeadCreatures

    def deadCreatures_add(self, creature):
        self.__deadCreatures[creature.creatureNo()] = creature
        self.__diffDeadCreatures[creature.creatureNo()] = creature

    def resources(self):
        return self.__resources

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
        resources *= resKiller*0.85
        return resources
    
    def resources_grow(self):
        self.resources()[0] += ((((self.resources()[0]**3.)*(np.exp(-(((self.resources()[0]/7.)-1.)**2.))))/500.)*self.resources()[1] + 0.3)
        self.resources()[0].clip(0, self.resources()[2], out=self.resources()[0]) #vals > max --> max
    
    def step(self):
        self.resources_grow()
        for creature in self.__livingCreatures.values():
            creature.step()
        
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

def RunSim(noSteps=500, saveData=True, mapFile = None):
    '''Produces nested output list with format:
    [[time0], [time1], [time2],..., [timeEnd]]
    Where each [time] is [livingCreatures, deadCreatures, resources]
    Except at [time0] = [livingCreatures, deadCreatures, resources, natVar]
    Also at each [time], deadCreatures is actually any new deadCreatures that [time] not the entire {dict}
    And livingCreatures, deadCreatures and resources are the {dicts} from Environment object
    '''
    t0 = time.time()
    if mapFile is not None:
        world = Environment(mapFile=mapFile)
    else:
        world = Environment()
    resourcesGRMaxE = np.copy(world.resources()[1:3,:,:])
    livingCreatures_info = livingCreatures_infoFunc(world.livingCreatures())
    deadCreatures_info = deadCreatures_infoFunc({})
    worldHistory = [[livingCreatures_info, deadCreatures_info, np.copy(world.resources()[0])]]
    # dump(worldHistory)
    for step in xrange(noSteps):
        t1 = time.time()
        if len(world.livingCreatures()) == 0:
            break
        else:
            if step == 400:
                creatures = len(world.livingCreatures())
                print world.livingCreatures()
                print world.livingCreatures().items()[int(creatures*0.9):]
                world.livingCreatures_set(dict(world.livingCreatures().items()[int(creatures*0.9):]))
            world.clearTempDeadCreatures()
            world.step()
            t2 = time.time()
            livingCreatures_info = livingCreatures_infoFunc(world.livingCreatures())
            deadCreatures_info = deadCreatures_infoFunc(world.diffDeadCreatures())
            worldHistory.append([livingCreatures_info, deadCreatures_info, np.copy(world.resources()[0])])
        print 'Step %d complete. worldHistory in %s seconds. step in %s seconds.' % (step+1, time.time()-t2, t2-t1)
    # dump(worldHistory)
    print 'Time for %d steps: %s seconds' %(noSteps, time.time()-t0)

    if saveData == True:
        print 'Saving simulation data.'
        mydir = os.path.dirname(os.path.realpath(__file__))
        subdir = 'Simulations/'
        sim_dir = os.path.join(mydir, subdir)
        # home = expanduser("~")
        # sim_directory = home +'/Simulations/'
        # sim_path = os.path.dirname(sim_directory)
        if os.path.exists(sim_dir) == False:
            os.mkdir(sim_dir)
        with open(sim_dir+'sim_%s_%s.dat'%(str(int(time.time())), str(noSteps)), 'wb') as out:
            pickler = pickle.Pickler(out, -1)
            pickler.dump([worldHistory, resourcesGRMaxE, quickCopy(world.natVar()), world.mapFileDump()])
    return worldHistory

def livingCreatures_infoFunc(livingCreatures):
    livingCreatures_info = np.zeros((len(livingCreatures), 10))
    for i, creature in enumerate(livingCreatures.itervalues()):
        livingCreatures_info[i] = np.array([creature.creatureNo(), creature.pos()[0], creature.pos()[1], creature.physChar()['energy'], creature.gen()['NumOff'], creature.gen()['ReprThresh'], creature.gen()['Aggr'], creature.gen()['Speed'], creature.gen()['MouthSize'], creature.gen()['Vis']])
    return livingCreatures_info

#def deadCreatures_infoFunc(deadCreatures, temp_deadCreatures):
#    diff_deadCreatures = [(k, v) for k, v in deadCreatures.iteritems() if k not in temp_deadCreatures]
#    deadCreatures_info = np.zeros((len(diff_deadCreatures), 3))
#    for i in xrange(len(diff_deadCreatures)):
#        deadCreatures_info[i] = np.array([diff_deadCreatures[i][1].creatureNo(), diff_deadCreatures[i][1].pos()[0], diff_deadCreatures[i][1].pos()[1]])
#    return deadCreatures_info
    
def deadCreatures_infoFunc(diff_deadCreatures):
    deadCreatures_info = np.zeros((len(diff_deadCreatures), 3))
    for i, creature in enumerate(diff_deadCreatures.itervalues()):
        deadCreatures_info[i] = np.array([creature.creatureNo(), creature.pos()[0], creature.pos()[1]])
    return deadCreatures_info

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

def speedVis(creature):
    return creature[7], creature[9]

def speedReprThreshVis(creature):
    return creature[7], creature[5], creature[9]

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
<<<<<<< HEAD
    POI = 400 #np.clip(np.argmax(popForStep), 10, len(worldHistory)-16)
    #Analyse.plotForSteps(avgSpeed, 231, len(worldHistory), "Avg Speed", 'ro-', (worldHistory))
    #Analyse.plotForSteps(totPop, 232, len(worldHistory), "Population", 'bo-', (worldHistory))
    #Analyse.plotForSteps(avgVis, 234, len(worldHistory), "Avg Vis", 'go-', (worldHistory))
    #Analyse.plotForSteps(totERes, 235, len(worldHistory), "Resource Energy", 'yo-', (worldHistory))
    #Analyse.plotForCreatures(speedVis, worldHistory[915][0], 233, 'Speed', 'Vis', 'Speed vs Vision in 914th step')
    Analyse.plotForCreatures(speedReprThreshVis, worldHistory[POI-10][0], 231, 'Speed', 'Repr Thresh', 'Vision', 'Genetics Plot in %dth step'%(POI-9))
    Analyse.plotForCreatures(speedReprThreshVis, worldHistory[POI-5][0], 232, 'Speed', 'Repr Thresh', 'Vision', 'Genetics Plot in %dth step'%(POI-4))
    Analyse.plotForCreatures(speedReprThreshVis, worldHistory[POI][0], 233, 'Speed', 'Repr Thresh', 'Vision', 'Genetics Plot in %dth step'%(POI+1))
    Analyse.plotForCreatures(speedReprThreshVis, worldHistory[POI+5][0], 234, 'Speed', 'Repr Thresh', 'Vision', 'Genetics Plot in %dth step'%(POI+6))
    Analyse.plotForCreatures(speedReprThreshVis, worldHistory[POI+10][0], 235, 'Speed', 'Repr Thresh', 'Vision', 'Genetics Plot in %dth step'%(POI+11))
    Analyse.plotForCreatures(speedReprThreshVis, worldHistory[POI+15][0], 236, 'Speed', 'Repr Thresh', 'Vision', 'Genetics Plot in %dth step'%(POI+16))
=======
    POI = np.clip(np.argmax(popForStep),10, len(worldHistory)-16)
    Analyse.plotForSteps(avgSpeed, 231, len(worldHistory), "Avg Speed", 'ro-', (worldHistory))
    Analyse.plotForSteps(totPop, 232, len(worldHistory), "Population", 'bo-', (worldHistory))
    Analyse.plotForSteps(avgVis, 234, len(worldHistory), "Avg Vis", 'go-', (worldHistory))
    Analyse.plotForSteps(totERes, 235, len(worldHistory), "Resource Energy", 'yo-', (worldHistory))
    Analyse.plotForCreatures(speedVis, worldHistory[915][0], 233, 'Speed', 'Vis', 'Speed vs Vision in 914th step')
    #Analyse.plotForCreatures(speedReprThreshVis, worldHistory[POI-10][0], 231, 'Speed', 'Repr Thresh', 'Vision', 'Genetics Plot in %dth step'%(POI-9))
    #Analyse.plotForCreatures(speedReprThreshVis, worldHistory[POI-5][0], 232, 'Speed', 'Repr Thresh', 'Vision', 'Genetics Plot in %dth step'%(POI-4))
    #Analyse.plotForCreatures(speedReprThreshVis, worldHistory[POI][0], 233, 'Speed', 'Repr Thresh', 'Vision', 'Genetics Plot in %dth step'%(POI+1))
    #Analyse.plotForCreatures(speedReprThreshVis, worldHistory[POI+5][0], 234, 'Speed', 'Repr Thresh', 'Vision', 'Genetics Plot in %dth step'%(POI+6))
    #Analyse.plotForCreatures(speedReprThreshVis, worldHistory[POI+10][0], 235, 'Speed', 'Repr Thresh', 'Vision', 'Genetics Plot in %dth step'%(POI+11))
    #Analyse.plotForCreatures(speedReprThreshVis, worldHistory[POI+15][0], 236, 'Speed', 'Repr Thresh', 'Vision', 'Genetics Plot in %dth step'%(POI+16))
>>>>>>> origin/master
    plt.show()

def DisplaySavedSim(displayVisualSim=True):
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
        
    DisplaySim(worldHistory, resourcesGRMaxE, displayVisualSim, mapFile)

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