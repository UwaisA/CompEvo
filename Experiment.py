import Environment
from Environment import *
import time
import numpy as np
import os
import cPickle as pickle

def RunSim(experimentFunc=None, noSteps=500, saveData=True, mapFile = None):
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
    diffDeadCreatures_info = diffDeadCreatures_infoFunc(world.deadCreatures())
    worldHistory = [[livingCreatures_info, diffDeadCreatures_info, np.copy(world.resources()[0], 1.)]]
    # dump(worldHistory)
    for step in xrange(noSteps):
        t1 = time.time()
        if world.livingCreatures().isEmpty():
            break
        else:
            if experimentFunc is not None:
                if experimentFunc == increaseResources:
                    resourceMultiplier = experimentFunc(step, world)
                else:
                    experimentFunc(step, world)
                    resourceMultiplier = 1.
            else:
                resourceMultiplier = 1.
            world.clearTempDeadCreatures()
            world.step()
            t2 = time.time()
            livingCreatures_info = livingCreatures_infoFunc(world.livingCreatures())
            diffDeadCreatures_info = diffDeadCreatures_infoFunc(world.deadCreatures())
            worldHistory.append([livingCreatures_info, diffDeadCreatures_info, np.copy(world.resources()[0]), resourceMultiplier])
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
            pickler.dump([worldHistory, resourcesGRMaxE, np.copy(world.natVar()), world.mapFileDump()])
    return worldHistory

#Experiment funcs must have step and world as params

def massExtinction(step, world):
    if step == 500:
        world.livingCreatures().killProportion(0.9)

def randomDeaths(step, world):
    if step == 100:
        world.randomDeaths = 0.

def increaseResources(step, world):
    multiplyFactor = 1.04
    if step > 40 and step < 60:
        world.multiplyResources(multiplyFactor)
        return multiplyFactor
    else:
        return 1.

def empty(step, world):
    pass

RunSim(massExtinction, noSteps=1000, mapFile='MediumGrassAndShrubCyclicalConnectedIslands.tmx')
