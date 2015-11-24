import math, numpy as np, numpy.linalg as la

__module__ = ''' This is to classify resource objects in environment
             Check readme.txt for more info
             '''

# RESOURCE MOTHER CLASS________________________________________________________
class Resource(object):
    ''' Resource Object to be implemented in virtual environment '''
    def __init__(self, environment, E=0., pos=np.array([0,0]), growRate=1., maxE=20.):
        self.__E = E
        self.__pos = pos
        self.__growRate = growRate
        self.__maxE = maxE

    def eaten(self, consumer):
        #transfer energy to consumer
        energyIncrease = min(consumer.gen()['MouthSize'], self.E())
        consumer.setEnergy(consumer.physChar()['energy'] + energyIncrease)
        self.__E -= energyIncrease

    def __repr__(self):
        return "Res: E=%s"%("%.1f" % self.E())

    def __str__(self):
        return "pos=%s"%(self.__pos)

    # Returns current resource position
    def pos(self):
        return self.__pos

    def E(self):
        return self.__E

    def growRate(self):
        return self.__growRate

    def maxE(self):
        return self.__maxE

    def grow(self):
        #self.__E = min(self.E() + self.growRate(), self.maxE())
        self.__E = min((((self.E()**3.)*(math.exp(-(((self.E()/7.)-1.)**2.)/500.)))*self.growRate() + 0.5), self.maxE())

class Food(Resource):
    ''' Food Resource to be eaten by creature for energy'''
    def __init__(self, environment, E=0., pos=np.array([0,0]), growRate=0.):
        super(Food, self).__init__(environment=environment, E=E, pos=pos, growRate=growRate)

class Prey(Resource):
    ''' Prey Resource converts creature data to resource eaten by predator'''
    def __init__(self, environment, E=0., pos=np.array([0,0]), creatureNo=0):
        Resource.__init__(self, environment, E, pos)
        self.__creatureNo = creatureNo