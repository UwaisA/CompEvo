import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import time
from itertools import combinations as combs
import functools

'''
func must take in step then *funcargs as params
'''
def plotForSteps(func, subplot, maxSteps, funcName="func Name", colour='ro-', *funcargs):
    xRes = np.arange(maxSteps)
    yRes = np.zeros(maxSteps)
    for i in xrange(maxSteps):
        yRes[i] = func(i, *funcargs)
    plot(subplot, xRes, yRes, colour=colour, xlabel="Step number", ylabel=funcName, title=funcName+" vs Time")

#draws a line graph using the parameters passed to it
def plot(subplot, x, y, colour = 'ro-', xlabel = "x", ylabel = "y", title = "Title"):
    plt.figure(1)
    plt.subplot(subplot)
    plt.plot(x, y, colour)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

def plotScatter(subplot, x, y, colour=None, xlabel="x", ylabel="y", title="Title"):
    plt.figure(1)
    plt.subplot(subplot)
    if colour==None:
        plt.scatter(x,y)
    else:
        plt.scatter(x, y, c=colour, cmap='gist_ncar')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

def plotScatter3D(subplot, x, y, z=None, colour=None, xlabel="x", ylabel="y", zlabel="z", title="Title"):
    fig = plt.figure(1)
    ax = fig.add_subplot(subplot, projection='3d')
    if colour==None:
        ax.scatter(x, y, z)
    else:
        ax.scatter(x, y, z, c=colour, cmap='gist_ncar')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    ax.set_title(title)

'''
func must take in Creature numpy representation and return x, y value for plot
'''
def plotForCreatures(func, livingCreatures, subplot, xlabel='x', ylabel='y', zlabel='z', title=''):
    xRes = np.ndarray(len(livingCreatures))
    yRes = np.ndarray(len(livingCreatures))
    dims = len(func(livingCreatures[0]))
    creatSpec = findSpecies(livingCreatures)
    colors = (np.array(creatSpec[:,1])-1)/float(np.max(creatSpec[:,1])-1)
    if dims == 3:
        zRes = np.ndarray(len(livingCreatures))
        for i in xrange(len(livingCreatures)):
            xRes[i], yRes[i], zRes[i] = func(livingCreatures[i])
        plotScatter3D(subplot, xRes, yRes, zRes, xlabel=xlabel, ylabel=ylabel, zlabel=zlabel, title=title, colour=colors)
    elif dims == 2:
        for i in xrange(len(livingCreatures)):
            xRes[i], yRes[i] = func(livingCreatures[i])
        plotScatter(subplot, xRes, yRes, xlabel=xlabel, ylabel=ylabel, title=title, colour=colors)

'''
livingCreatures should be formatted as a numpy array as it is stored in worldHist
'''
def findSpecies(livingCreatures):
    t0 = time.time()
   # genDistSqr = np.zeros((len(livingCreatures), len(livingCreatures)))
    #it = np.nditer(genDistSqr, flags=['multi_index'], op_flags=['writeonly'])
    creatureNoList = livingCreatures[:,0]
    creatIndicies = np.arange(len(livingCreatures))
    xCreat, yCreat = np.meshgrid(creatIndicies,creatIndicies)[0].flatten(), np.meshgrid(creatIndicies,creatIndicies)[1].flatten()
    func = functools.partial(genList, livingCreatures)
    genDistSqr = np.array(map(func, xCreat, yCreat)).reshape((len(livingCreatures), len(livingCreatures)))
    t1 = time.time()
    genDistSqr = np.triu(genDistSqr, 1)
    genDistSqr += genDistSqr.T
    nearestCreatArr = nsmall(genDistSqr, 1, 0)
    specieRad = nsmall(nearestCreatArr, int(0.99*len(nearestCreatArr)+0.5)-1, 0)
    sameSpecies = genDistSqr<=specieRad
    t2 = time.time()
    creatSpec = np.ndarray((len(livingCreatures), 2), dtype=int)
    creatSpec[:,0] = creatureNoList
    creatSpec[:,1] = 0
    #merges clusters
    argsToBeAnalysed = set(np.arange(len(livingCreatures))) #creature args yet to merged
    curSpec = 0
    while len(argsToBeAnalysed) > 0: #one iteration for each species
        curSpec += 1
        newToBeAnalysed = set([argsToBeAnalysed.pop()])
        while len(newToBeAnalysed) > 0:
            for nextVal in newToBeAnalysed: #just for getting a value from set
                toBeAnalysedNext = argsToBeAnalysed.intersection(set(np.argwhere(sameSpecies[nextVal]).flatten()))
                argsToBeAnalysed = argsToBeAnalysed.difference(toBeAnalysedNext)
                newToBeAnalysed = newToBeAnalysed.union(toBeAnalysedNext)
                creatSpec[nextVal][1] = curSpec
                newToBeAnalysed.remove(nextVal)
                break
    print 'total',time.time()-t0,'newTripleFor',time.time()-t2,'len liv creat',len(livingCreatures)
    return creatSpec

def genList(livingCreatures, creat1, creat2):
    if (creat1 - creat2) > 0:
        return genDistSqrCalc(livingCreatures[creat1][4:], livingCreatures[creat2][4:])
    return 0

def genDistSqrCalc(gen1, gen2):
    return np.sum((gen1-gen2)**2)

def nsmall(arr, n, axis):
    return np.partition(arr, n, axis)[n]

#def addToPlot(subplot, appendX, appendY):
#    plt.figure(1)
#    plt.subplot(subplot)
#    plt.se