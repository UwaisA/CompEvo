import numpy as np
import matplotlib.pyplot as plt


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

'''
func must take in Creature numpy representation and return x, y value for plot
'''
def plotForCreatures(func, livingCreatures, subplot, xlabel='x', ylabel='y', title='x vs y'):
    xRes = np.ndarray(len(livingCreatures))
    yRes = np.ndarray(len(livingCreatures))
    for i in xrange(len(livingCreatures)):
        xRes[i], yRes[i] = func(livingCreatures[i])
    plot(subplot, xRes, yRes, colour='bo', xlabel=xlabel, ylabel=ylabel, title=title)
#def addToPlot(subplot, appendX, appendY):
#    plt.figure(1)
#    plt.subplot(subplot)
#    plt.se