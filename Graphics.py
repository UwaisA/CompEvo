from __future__ import print_function
import pygame
import os
from pytmx import *
from pytmx.util_pygame import load_pygame
from pygame.locals import *
import numpy as np
import time
from matplotlib import cm

class Graphics(object):
    BLACK = [0, 0, 0]
    WHITE = [255, 255, 255]
    RED = [255, 0, 0]
    BLUE = [0, 0, 255]
    
    def __init__(self, mapFile = "isometric_grass_and_water2.tmx"):
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

    def TransformMap(self, pos, multi=False):
        if multi:
            new_pos_x = (self.SIZE[0]/2 + (self.tw/2) * (pos[:,0] - pos[:,1] - 1))*(self.RESIZE[0]/float(self.SIZE[0]))
            new_pos_y = ((self.th/2) * (pos[:,1] + pos[:,0] - 1))*(self.RESIZE[1]/float(self.SIZE[1]))
            new_pos = np.ndarray(pos.shape, int)
            new_pos[:,0], new_pos[:,1] = new_pos_x, new_pos_y
            return new_pos
        else:
            new_pos_x = int((self.SIZE[0]/2 + (self.tw/2) * (pos[0] - pos[1] - 1))*(self.RESIZE[0]/float(self.SIZE[0])))
            new_pos_y = int(((self.th/2) * (pos[1] + pos[0] - 1))*(self.RESIZE[1]/float(self.SIZE[1])))
            return np.array([new_pos_x, new_pos_y])

    def TransformResourcePos(self, pos):
        new_pos_x = int((self.SIZE[0]/2 + (self.tw/2) * (pos[0] - pos[1]) - 1)*(self.RESIZE[0]/float(self.SIZE[0])))
        new_pos_y = int(((self.th/2) * (pos[1] + pos[0]) + 1)*(self.RESIZE[1]/float(self.SIZE[1])))
        return np.array([new_pos_x, new_pos_y])

    def TransformPos(self, pos, multi=False):
        if multi:
            new_pos_x = (self.SIZE[0]/2 + (pos[:,0] - pos[:,1]))*(self.RESIZE[0]/float(self.SIZE[0]))
            new_pos_y = ((pos[:,0] + pos[:,1])/2)*(self.RESIZE[1]/float(self.SIZE[1]))
            new_pos = np.ndarray(pos.shape, int)
            new_pos[:,0], new_pos[:,1] = new_pos_x, new_pos_y
            return new_pos
        else:
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
                #pygame.draw.polygon(self.screen, colour, [(trans_pos[0], trans_pos[1]+int(self.th/16.)), (trans_pos[0]+int(self.tw*7./16.), trans_pos[1]+int(self.th/2.)), (trans_pos[0], trans_pos[1]+int(self.th*15./16.)), (trans_pos[0]-int(self.tw*7./16.), trans_pos[1]+int(self.tw/4.))], 2)
                pygame.draw.aalines(self.screen, colour, True, [(trans_pos[0], trans_pos[1]+int(self.th/16.)), (trans_pos[0]+int(self.tw*7./16.), trans_pos[1]+int(self.th/2.)), (trans_pos[0], trans_pos[1]+int(self.th*15./16.)), (trans_pos[0]-int(self.tw*7./16.), trans_pos[1]+int(self.tw/4.))], 1)
        
        trans_pos = self.TransformPos(livingCreatures.allCreats()[:,1:3], multi=True)
        eOverRT = creatures.allCreats()[:,3]/creatures.allCreats()[:,5]
        colour = np.ndarray(len(eOverRT), 3)
        colour[:,2] = 255
        colour[:,0] = colour[:,1] = np.clip(255*eOverRT,0,255)
        for i, creature in enumerate(livingCreatures.allCreats()):
            pygame.draw.circle(self.screen, colour[i], (trans_pos[i][0], trans_pos[i][1]), 2)
        
        print('Map Updated')
        pygame.display.flip()
        self.clock.tick(15)

    def DisplaySavedMap(self, worldHistory, resourcesGRMaxE):
        # mydir = os.path.dirname(os.path.realpath(__file__))
        # subdir = 'Maps'
        # mapfilepath = os.path.join(mydir, subdir, mapFile)
        # gameMap = load_pygame(mapfilepath)
        # self.tmxdata = TiledMap(mapfilepath)
        
        timeLength = len(worldHistory)
        coords = np.meshgrid(np.arange(self.gridWidth), np.arange(self.gridHeight))[::-1]
        coords = np.transpose(coords, axes=(1,2,0)).reshape(self.gridWidth*self.gridHeight,2)
        TransPosArray = self.TransformMap(coords, multi=True).reshape((self.gridWidth, self.gridHeight, 2))
        PolygonPosArray = np.zeros((self.gridWidth, self.gridHeight, 4, 2))
        PolygonColourArray = np.zeros((self.gridWidth, self.gridHeight, timeLength))
        for timeStep in xrange(timeLength):
            if len(worldHistory[timeStep]) == 4:
                resourcesGRMaxE *= worldHistory[timeStep][3]
            PolygonColourArray[:,:,timeStep] = worldHistory[timeStep][2]*255./resourcesGRMaxE[1]
        PolygonColourArray = np.clip(PolygonColourArray, 0, 255).astype(int)
        tIDsArray = np.ndarray((self.gridWidth, self.gridHeight), dtype=int)
        images = {}
        sizeRat0 = self.RESIZE[0]/float(self.SIZE[0])
        sizeRat1 = self.RESIZE[1]/float(self.SIZE[1])
        TileBlitSize = (int(self.tw*sizeRat0), int(self.tw*sizeRat1))
        for b in xrange(self.gridHeight):
            for a in xrange(self.gridWidth):
                x, y = self.gridWidth-a-1, self.gridHeight-b-1
                if resourcesGRMaxE[0][x][y] > 0:
                    tempTransPos = self.TransformResourcePos(np.array([x,y]))
                    PolygonPosArray[x][y] = [(tempTransPos[0], tempTransPos[1]+int((self.th/16.)*sizeRat1)), (tempTransPos[0]+int((self.tw*7./16.)*sizeRat0), tempTransPos[1]+int((self.th/2.)*sizeRat1)), (tempTransPos[0], tempTransPos[1]+int((self.th*15./16.)*sizeRat1)), (tempTransPos[0]-int((self.tw*7./16.)*sizeRat0), tempTransPos[1]+int((self.tw/4.)*sizeRat1))]
                    
                tID = int(self.tmxdata.get_tile_properties(x,y,0)['tID'])
                tIDsArray[x][y] = tID
                if not images.has_key(tID):
                    images[tID] = pygame.transform.scale(self.gameMap.get_tile_image(x,y,0), TileBlitSize)
            print('Loading map surface locations, approximately %d%% complete' % int(b*(100./(self.gridHeight-1))), end='\r')
        print('')
        creatPropertyArray = [None]*timeLength
        lastRatio = 0
        for creatArrStep in xrange(timeLength):
            creatures = worldHistory[creatArrStep][0]
            tempCreatPropertyArray = np.zeros([len(creatures), 2, 3], int)
            tempCreatPropertyArray[:,0,0:2] = self.TransformPos(creatures[:,1:3], multi=True)
            tempCreatPropertyArray[:,1,2] = 255
            cols = np.clip(255*(creatures[:,3]/creatures[:,5]), 0, 255)
            tempCreatPropertyArray[:,1,0:2] = np.array([cols]).T
            creatPropertyArray[creatArrStep] = tempCreatPropertyArray
            if creatArrStep*100/(timeLength-1) >= lastRatio+1:
                print('Loading creature locations, approximately %d%% complete' % (creatArrStep*100/(timeLength-1)), end='\r')
                lastRatio = creatArrStep*100/(timeLength-1)
        print('')
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
                x, y = self.gridWidth-a-1, self.gridHeight-b-1
                image = images[tIDsArray[x][y]] #pre-scaled at load time
                self.screen.blit(image, TransPosArray[x][y])
                if resourcesGRMaxE[0][x][y] > 0:
                    pygame.draw.aalines(self.screen, [PolygonColourArray[x][y][step], 0, 0], True, PolygonPosArray[x][y], 1)
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
            print('Frame time = %s, for1 = %s, for2 = %s' % (time.time()-t0, t1-t0, t2-t1))

    def DisplaySavedMapFrame(self, worldFrame, resourcesGRMaxE, frameNo, colours, creatSpec):
        TileBlitSize = (int(self.tw*(self.RESIZE[0]/float(self.SIZE[0]))), int(self.tw*(self.RESIZE[1]/float(self.SIZE[1]))))
        sizeRat0 = self.RESIZE[0]/float(self.SIZE[0])
        sizeRat1 = self.RESIZE[1]/float(self.SIZE[1])
        done = False
        step = 0
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    pygame.quit()
                    return
            if step == 0:
                t0 = time.time()
                self.screen.fill(self.WHITE)
                resources = worldFrame[2]
                for a,b in np.ndindex((resources.shape[0], resources.shape[1])):
                    x, y = self.gridWidth-a-1, self.gridHeight-b-1
                    image = pygame.transform.scale(self.gameMap.get_tile_image(x,y,0), TileBlitSize) #pre-scaled at load time
                    self.screen.blit(image, self.TransformMap(np.array([x, y])))
                    if resourcesGRMaxE[0][x][y] > 0:
                        if len(worldFrame) == 4:
                            resourcesGRMaxE[1][x][y] *= worldFrame[3]
                        tempTransPos = self.TransformResourcePos(np.array([x,y]))
                        polygonPos = [(tempTransPos[0], tempTransPos[1]+int((self.th/16.)*sizeRat1)), (tempTransPos[0]+int((self.tw*7./16.)*sizeRat0), tempTransPos[1]+int((self.th/2.)*sizeRat1)), (tempTransPos[0], tempTransPos[1]+int((self.th*15./16.)*sizeRat1)), (tempTransPos[0]-int((self.tw*7./16.)*sizeRat0), tempTransPos[1]+int((self.tw/4.)*sizeRat1))]
                        polygonColour = self.RED[0]*worldFrame[2][x][y]/float(resourcesGRMaxE[1][x][y])
                        pygame.draw.aalines(self.screen, [polygonColour, 0, 0], True, polygonPos, 1)
                        #pygame.draw.polygon(self.screen, PolygonColourArray[x][y][step], PolygonPosArray[x][y], 1)
                t1 = time.time()

                for i in xrange(len(worldFrame[0])):
                    for j in xrange(len(creatSpec)):
                        if worldFrame[0][i][0] == creatSpec[j][0]:
                            creaturePos = self.TransformPos(np.array([worldFrame[0][i][1], worldFrame[0][i][2]]))
                            creatureColour = cm.gist_ncar(colours[j], bytes=True)[0:3]
                            pygame.draw.circle(self.screen, self.WHITE, creaturePos, 5)
                            pygame.draw.circle(self.screen, self.BLACK, creaturePos, 4)
                            pygame.draw.circle(self.screen, creatureColour, creaturePos, 2)
                t2 = time.time()
                
                print('Frame time = %s, for1 = %s, for2 = %s' % (time.time()-t0, t1-t0, t2-t1))
                pygame.display.flip()
            self.clock.tick(15)
            step += 1
        

