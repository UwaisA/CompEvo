import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import time
from scipy.cluster.hierarchy import dendrogram, linkage

'''
func must take in step then *funcargs as params
'''
def plotForSteps(func, fig, subplot, maxSteps, funcName="func Name", colour='ro-', stepInterval=1, *funcargs):
    xRes = np.arange(0, maxSteps, stepInterval)
    yRes = np.zeros(len(xRes))
    for i, xi in enumerate(xRes):
        yRes[i] = func(xi, *funcargs)
    plot(fig, subplot, xRes, yRes, colour=colour, xlabel="Step number", ylabel=funcName, title=funcName+" vs Time")

#draws a line graph using the parameters passed to it
def plot(fig, subplot, x, y, colour = 'ro-', xlabel = "x", ylabel = "y", title = "Title"):
    plt.figure(fig)
    plt.subplot(subplot)
    plt.plot(x, y, colour)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

def plotScatter(fig, subplot, x, y, colour=None, xlabel="x", ylabel="y", title="Title"):
    plt.figure(fig)
    plt.subplot(subplot)
    if colour==None:
        plt.scatter(x,y)
    else:
        plt.scatter(x, y, c=colour, cmap='hsv')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

def plotScatter3D(fig, subplot, x, y, z=None, colour=None, xlabel="x", ylabel="y", zlabel="z", title="Title"):
    fig = plt.figure(fig)
    ax = fig.add_subplot(subplot, projection='3d')
    if colour==None:
        ax.scatter(x, y, z)
    else:
        ax.scatter(x, y, z, c=colour, cmap='hsv')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    ax.set_title(title)

'''
func must take in Creature numpy representation and return x, y value for plot
'''
def plotForCreatures(func, fig, subplot, livingCreatures, xlabel='x', ylabel='y', zlabel='z', title='', useDendro=False, plotDendro=False, withAnomCorr=True):
    dims = len(func(livingCreatures[0]))
    creatSpec = findSpecies(livingCreatures, useDendro, plotDendro, withAnomCorr)
    if np.max(creatSpec[:,1])==0:
        colors = np.array(creatSpec[:,1])
    else:
        colors = (np.array(creatSpec[:,1]))/float(np.max(creatSpec[:,1]))
    if dims == 3:
        dataToPlot = np.array(map(func, livingCreatures))
        plotScatter3D(fig, subplot, dataToPlot[:,0], dataToPlot[:,1], dataToPlot[:,2], xlabel=xlabel, ylabel=ylabel, zlabel=zlabel, title=title, colour=colors)
    elif dims == 2:
        dataToPlot = np.array(map(func, livingCreatures))
        plotScatter(fig, subplot, dataToPlot[:,0], dataToPlot[:,1], xlabel=xlabel, ylabel=ylabel, title=title, colour=colors)


'''
livingCreatures should be formatted as a numpy array as it is stored in worldHist
'''
def findSpecies(livingCreatures, useDendro=False, plotDendro=False, withAnomCorr=True):
    creatureNoList = livingCreatures[:,0]
    creatGens = np.array([livingCreatures[:,4:]])
    xCreat = np.repeat(creatGens, (len(creatGens[0])), axis=0)
    yCreat = xCreat.transpose((1,0,2))
    genDist = np.sqrt(np.sum((xCreat-yCreat)**2, axis=2))
    nearestCreatArr = nsmall(genDist, 1, 0)
    specieRad = nsmall(nearestCreatArr, int(0.99*len(nearestCreatArr)+0.5)-1, 0)
    sameSpecies = genDist<=specieRad
    creatSpec = np.ndarray((len(livingCreatures), 2), dtype=int)
    creatSpec[:,0] = creatureNoList
    creatSpec[:,1] = 0
    #merges clusters
    argsToBeAnalysed = set(np.arange(len(livingCreatures))) #creature args yet to merged
    curSpec = 0
    while len(argsToBeAnalysed) > 0: #one iteration for each species
        newToBeAnalysed = set([argsToBeAnalysed.pop()])
        while len(newToBeAnalysed) > 0:
            for nextVal in newToBeAnalysed: #just for getting a value from set
                toBeAnalysedNext = argsToBeAnalysed.intersection(set(np.argwhere(sameSpecies[nextVal]).flatten()))
                argsToBeAnalysed = argsToBeAnalysed.difference(toBeAnalysedNext)
                newToBeAnalysed = newToBeAnalysed.union(toBeAnalysedNext)
                creatSpec[nextVal][1] = curSpec
                newToBeAnalysed.remove(nextVal)
                break
        curSpec += 1
    species = len(set(creatSpec[:,1]))
    if useDendro:
        creatSpec[:,1] = dendro(genDist, species, plotDendro)
    #print creatSpec
    #specCreats = {}
    if withAnomCorr:
        specPops = {}
        for creat in creatSpec:
            #specCreats[creat[1]] = specCreats.get(creat[1], []) + [creat[0]]
            specPops[creat[1]] = specPops.get(creat[1], 0)+1
        #anomaly fixing
        invalidSpecs = set()
        for spec in specPops.keys():
            if specPops[spec] < 0.01*len(creatSpec):
                invalidSpecs.add(spec)
        invalidCreats = np.argwhere(np.in1d(creatSpec[:,1], list(invalidSpecs))).flatten()
        for invalid in invalidCreats:
            for i in xrange(1, len(creatSpec)): #  xrange(1,...) to avoid self-selection
                argNearbyCreat = np.argwhere(genDist[invalid]==nsmall(genDist[invalid], i, 0)).flat[0]
                if not argNearbyCreat in invalidCreats:
                    creatSpec[invalid][1] = creatSpec[argNearbyCreat][1]
                    break
        #species list gap removal
        specsDict = {}
        specNo = 0
        for i in xrange(len(creatSpec[:,1])):
            if not specsDict.has_key(creatSpec[i][1]):
                specsDict[creatSpec[i][1]] = specNo
                specNo += 1
            creatSpec[i][1] = specsDict[creatSpec[i][1]]
    species = np.max(creatSpec[:,1])+1
    print 'creatures:',len(livingCreatures), 'species:', species
    #print specPops
    return creatSpec

def dendro(genDist, species, plotDendro):
    '''
    Returns second column of creatSpec
    '''
    if plotDendro:
        plt.figure()
    linkArr = linkage(genDist)
    dend = dendrogram(linkArr, p=species, truncate_mode='lastp', count_sort=True, no_plot=True)
    dendFull = dendrogram(linkArr, count_sort=True, no_plot=(not plotDendro))
    specCreats1 = []
    for i in dend['ivl']:
        if i.count('(') == 0:
            specCreats1.append([int(i)])
        else:
            specCreats1.append(dendFull['ivl'][sum(map(len,specCreats1)):sum(map(len,specCreats1))+int(i[1:-1])])
    
    creatSpec = np.ndarray((len(genDist)), dtype=int)
    for specNo, specMembers in enumerate(specCreats1):
        for specMember in specMembers:
            creatSpec[int(specMember)] = specNo
    return creatSpec

def nsmall(arr, n, axis):
    return np.partition(arr, n, axis)[n]

#def addToPlot(subplot, appendX, appendY):
#    plt.figure(1)
#    plt.subplot(subplot)
#    plt.se