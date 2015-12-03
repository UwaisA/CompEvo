import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import time

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
    genDist = np.zeros((len(livingCreatures), len(livingCreatures)))
    it = np.nditer(genDist, flags=['multi_index'], op_flags=['writeonly'])
    creatureNoList = livingCreatures[:,0]
    while not it.finished:
        if (it.multi_index[1] - it.multi_index[0]) > 0:
            it[0] = genDistCalc(livingCreatures[it.multi_index[0]][4:],
                                livingCreatures[it.multi_index[1]][4:])
        it.iternext()
    genDist += genDist.T
    nearestCreatArr = nsmall(genDist, 1, 0)
    specieRad = nsmall(nearestCreatArr, int(0.99*len(nearestCreatArr)+0.5)-1, 0)
    sameSpecies = genDist<=specieRad
    for row in sameSpecies:
        connectedList = np.argwhere(row).flatten()
        for i in connectedList:
            for j in connectedList:
                sameSpecies[i][j] = True
    creatSpec = np.zeros((len(livingCreatures), 2), dtype=int)
    creatSpec[:,0] = np.arange(len(livingCreatures))
    creatSpec[:,1] = 0
    while np.min(creatSpec[:,1]) == 0:
        curSpec = np.max(creatSpec[:,1])+1
        creatSpec[:,1] += curSpec*sameSpecies[np.argmin(creatSpec[:,1])]
    creatSpec[:,0] = creatureNoList
    return creatSpec

def genDistCalc(gen1, gen2):
    return (sum((gen1-gen2)**2))**0.5

def nsmall(arr, n, axis):
    return np.partition(arr, n, axis)[n]

#def addToPlot(subplot, appendX, appendY):
#    plt.figure(1)
#    plt.subplot(subplot)
#    plt.se