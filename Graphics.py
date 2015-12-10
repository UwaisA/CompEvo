import pygame
import os
from pytmx import *
from pytmx.util_pygame import load_pygame
from pygame.locals import *
from Creature import Creature
import numpy as np
import time

class Graphics(object):
    BLACK = [0, 0, 0]
    WHITE = [255, 255, 255]
    RED = [255, 0, 0]
    BLUE = [0, 0, 255]
    # tw = 64 # Tile width can get from tmx
    # th = 32 # Tile height """"""""
    
    def __init__(self, mapFile = "Outdoors1.tmx"):
        pygame.init()
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.clock = pygame.time.Clock()
        self.mapFile = mapFile #This is the filename of the map to be used for the display of this simulation
        mydir = os.path.dirname(os.path.realpath(__file__))
        subdir = 'Maps'
        mapfilepath = os.path.join(mydir, subdir, self.mapFile)
        self.tmxdata = TiledMap(mapfilepath)
        self.tw = int(self.tmxdata.get_tile_properties(0,0,0)['width'])
        self.th = int(self.tmxdata.get_tile_properties(0,0,0)['height']/2.)
        self.gridWidth = int(self.tmxdata.properties['Width'])
        self.gridHeight = int(self.tmxdata.properties['Width'])
        self.SIZE = [self.gridWidth*self.tw, self.gridHeight*self.th]
        self.RESIZE = [1600,800]
        self.screen = pygame.display.set_mode(self.RESIZE, HWSURFACE|DOUBLEBUF|RESIZABLE)
        pygame.display.set_caption("Creature Simulation")
        pygame.event.set_allowed(QUIT)
        self.screen.fill(self.WHITE)
        self.gameMap = load_pygame(mapfilepath)
        #pygame.transform.scale(self.screen,(1600,800))

    def TransformMap(self, pos):
        new_pos_x = int((self.SIZE[0]/2 + (self.tw/2) * (pos[0] - pos[1] - 1))*(self.RESIZE[0]/float(self.SIZE[0])))
        new_pos_y = int(((self.th/2) * (pos[1] + pos[0] - 1))*(self.RESIZE[1]/float(self.SIZE[1])))
        return np.array([new_pos_x, new_pos_y])

    def TransformResourcePos(self, pos):
        new_pos_x = int((self.SIZE[0]/2 + (self.tw/2) * (pos[0] - pos[1]) - 1)*(self.RESIZE[0]/float(self.SIZE[0])))
        new_pos_y = int(((self.th/2) * (pos[1] + pos[0]) + 1)*(self.RESIZE[1]/float(self.SIZE[1])))
        return np.array([new_pos_x, new_pos_y])

    def TransformPos(self, pos):
        new_pos_x = int((self.SIZE[0]/2 + (pos[0] - pos[1]))*(self.RESIZE[0]/float(self.SIZE[0])))
        new_pos_y = int(((pos[0] + pos[1])/2)*(self.RESIZE[1]/float(self.SIZE[1])))
        return np.array([new_pos_x, new_pos_y])

    def DisplayMap(self, livingCreatures, resources):
        # mydir = os.path.dirname(os.path.realpath(__file__))
        # subdir = 'Maps'
        # mapfilepath = os.path.join(mydir, subdir, mapFile)
        # gameMap = load_pygame(mapfilepath)
                
        for y in xrange(self.gridHeight):
            for x in xrange(self.gridWidth):
                image = self.gameMap.get_tile_image(x,y,0)
                trans_pos = self.TransformMap(np.array([x, y]))
                self.screen.blit(image, (trans_pos[0], trans_pos[1]))
                
        for x,y in np.ndindex((len(resources[0]), len(resources[0][0]))):
            if resources[2][x][y] > 0:
                trans_pos = self.TransformResourcePos(np.array([x,y]))
                colour = [self.RED[0]*resources[0][x][y]/float(resources[2][x][y]), self.RED[1], self.RED[2]]
                pygame.draw.polygon(self.screen, colour, [(trans_pos[0], trans_pos[1]+int(self.th/16.)), (trans_pos[0]+int(self.tw*7./16.), trans_pos[1]+int(self.th/2.)), (trans_pos[0], trans_pos[1]+int(self.th*15./16.)), (trans_pos[0]-int(self.tw*7./16.), trans_pos[1]+int(self.tw/4.))], 2)
        
        for creature in livingCreatures.values():
            trans_pos = self.TransformPos(np.array([creature.pos()[0], creature.pos()[1]]))
            eOverRT = creature.physChar()['energy']/creature.gen()['ReprThresh']
            colour = np.clip([int(255*eOverRT),int(255*eOverRT),255], 0, 255)
            pygame.draw.circle(self.screen, colour, (trans_pos[0], trans_pos[1]), 2)
        
        print 'Map Updated'
        pygame.display.flip()
        self.clock.tick(15)

    def DisplaySavedMap(self, worldHistory, resourcesGRMaxE):
        # mydir = os.path.dirname(os.path.realpath(__file__))
        # subdir = 'Maps'
        # mapfilepath = os.path.join(mydir, subdir, mapFile)
        # gameMap = load_pygame(mapfilepath)
        # self.tmxdata = TiledMap(mapfilepath)
        
        timeLength = len(worldHistory)
        TransPosArray = np.zeros((self.gridWidth, self.gridHeight, 2))
        PolygonPosArray = np.zeros((self.gridWidth, self.gridHeight, 4, 2))
        PolygonColourArray = np.zeros((self.gridWidth, self.gridHeight, timeLength, 3))
        TileBlitSize = (int(self.tw*(self.RESIZE[0]/float(self.SIZE[0]))), int(self.tw*(self.RESIZE[1]/float(self.SIZE[1]))))
        tIDsArray = np.ndarray((self.gridWidth, self.gridHeight), dtype=int)
        images = {}
        for b in xrange(self.gridHeight):
            for a in xrange(self.gridWidth):
                x, y = self.gridWidth-a-1, self.gridHeight-b-1
                TransPosArray[x][y] = self.TransformMap(np.array([x, y]))
                if resourcesGRMaxE[0][x][y] > 0:
                    tempTransPos = self.TransformResourcePos(np.array([x,y]))
                    PolygonPosArray[x][y] = [(tempTransPos[0], tempTransPos[1]+int((self.th/16.)*(self.RESIZE[1]/float(self.SIZE[1])))), (tempTransPos[0]+int((self.tw*7./16.)*(self.RESIZE[0]/float(self.SIZE[0]))), tempTransPos[1]+int((self.th/2.)*(self.RESIZE[1]/float(self.SIZE[1])))), (tempTransPos[0], tempTransPos[1]+int((self.th*15./16.)*(self.RESIZE[1]/float(self.SIZE[1])))), (tempTransPos[0]-int((self.tw*7./16.)*(self.RESIZE[0]/float(self.SIZE[0]))), tempTransPos[1]+int((self.tw/4.)*(self.RESIZE[1]/float(self.SIZE[1]))))]
                    for timeStep in xrange(timeLength):
                        PolygonColourArray[x][y][timeStep] = [self.RED[0]*worldHistory[timeStep][2][x][y]/float(resourcesGRMaxE[1][x][y]), self.RED[1], self.RED[2]]
                tID = int(self.tmxdata.get_tile_properties(x,y,0)['tID'])
                tIDsArray[x][y] = tID
                if not images.has_key(tID):
                    images[tID] = pygame.transform.scale(self.gameMap.get_tile_image(x,y,0), TileBlitSize)
            print 'Loading map surface locations, approximately %d%% complete' % int(b*(100./self.gridHeight))

        creatPropertyArray = [None]*timeLength
        lastRatio = 0
        for creatArrStep in xrange(timeLength):
            creatures = worldHistory[creatArrStep][0]
            tempCreatPropertyArray = np.zeros([len(creatures), 2, 3])
            for i in xrange(len(creatures)):
                tempCreatTransPos = self.TransformPos(np.array([int(creatures[i][1]), int(creatures[i][2])]))
                tempCreatPropertyArray[i][0] = np.array([tempCreatTransPos[0], tempCreatTransPos[1], 0])
                col = int(255*(creatures[i][3]/creatures[i][5]))
                tempCreatPropertyArray[i][1] = np.clip([col, col, 255], 0, 255)
            creatPropertyArray[creatArrStep] = tempCreatPropertyArray.astype(int)
            if creatArrStep*100/timeLength >= lastRatio+1:
                print 'Loading creature locations, approximately %d%% complete' % int(creatArrStep*(100./timeLength))
                lastRatio = np.copy(creatArrStep*100/timeLength)

        raw_input('Press Enter to display simulation.....')

        step = 0
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    pygame.quit()
                    return

            t0 = time.time()
            self.screen.fill(self.WHITE)
            resources = worldHistory[step][2]
            for a,b in np.ndindex((resources.shape[0], resources.shape[1])):
                # t0a = time.time()
                x, y = self.gridWidth-a-1, self.gridHeight-b-1
                # t0ai = time.time()
                image = images[tIDsArray[x][y]] #pre-scaled at load time
                # t0aii = time.time()
                self.screen.blit(image, (TransPosArray[x][y][0], TransPosArray[x][y][1]))
                # t1a = time.time()
                if resourcesGRMaxE[0][x][y] > 0:
                    # t1ai = time.time()
                    pygame.draw.aalines(self.screen, PolygonColourArray[x][y][step], True, PolygonPosArray[x][y], 1)
                    # pygame.draw.polygon(self.screen, colour, PolygonPosArray[x][y], 1)
                # t2a = time.time()
                # if (a+b)%500 == 0:
                #     print 'Map time = %s, Resource time = %s' % (t1a-t0a, t2a-t1a)
                #     print 'xy time = %s, image time = %s, blit time = %s' % (t0ai-t0a, t0aii-t0ai, t1a-t0aii)
                #     if resourcesGRMaxE[0][x][y] > 0:
                #         print 'colour time = %s, draw time = %s' % (t1ai-t1a, t2a-t1ai)
            t1 = time.time()

            creatureProps = creatPropertyArray[step]
            for i in xrange(len(worldHistory[step][0])):
                pygame.draw.circle(self.screen, creatureProps[i][1], (creatureProps[i][0][0], creatureProps[i][0][1]), 2)
            t2 = time.time()
            pygame.display.flip()
            self.clock.tick(15)
            if step == timeLength - 1:
                done = True
                pygame.quit()
            step += 1
            print 'Frame time = %s, for1 = %s, for2 = %s' % (time.time()-t0, t1-t0, t2-t1)












