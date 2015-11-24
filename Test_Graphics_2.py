import pygame
import os
from pytmx import *
from pytmx.util_pygame import load_pygame
from pygame.locals import *
from Creature import Creature
import numpy as np

class TestGraphics(object):
    SIZE = [1600, 800]
    BLACK = [0, 0, 0]
    WHITE = [255, 255, 255]
    RED = [255, 0, 0]
    BLUE = [0, 0, 255]
    tw = 64 # Tile width can get from tmx
    th = 32 # Tile height """"""""
    
    def __init__(self):
        pygame.init()
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.screen = pygame.display.set_mode(self.SIZE)
        pygame.display.set_caption("Creature Simulation")
        pygame.event.set_allowed(QUIT)
        self.screen.fill(self.WHITE)
        self.clock = pygame.time.Clock()

    def TransformMap(self, pos):
        new_pos_x = self.SIZE[0]/2 + (self.tw/2) * (pos[0] - pos[1] - 1)
        new_pos_y = (self.th/2) * (pos[1] + pos[0] - 1)
        return np.array([new_pos_x, new_pos_y])

    def TransformResourcePos(self, pos):
        new_pos_x = self.SIZE[0]/2 + (self.tw/2) * (pos[0] - pos[1]) - 1
        new_pos_y = (self.th/2) * (pos[1] + pos[0]) + 1
        return np.array([new_pos_x, new_pos_y])

    def TransformPos(self, pos):
        new_pos_x = self.SIZE[0]/2 + (pos[0] - pos[1])
        new_pos_y = (pos[0] + pos[1])/2
        return np.array([new_pos_x, new_pos_y])

    def DisplayMap(self, livingCreatures, resources, mapFile="isometric_grass_and_water2.tmx"):
        mydir = os.path.dirname(os.path.realpath(__file__))
        subdir = 'Maps'
        mapfilepath = os.path.join(mydir, subdir, mapFile)
        gameMap = load_pygame(mapfilepath)
        images = []
        
        for y in xrange(25):
            for x in xrange(25):
                image = gameMap.get_tile_image(x,y,0)
                images.append(image)
                
        for y in xrange(25):
            for x in xrange(25):
                trans_pos = self.TransformMap(np.array([x, y]))
                self.screen.blit(images[y*25 + x],(trans_pos[0], trans_pos[1]))
                
        for x,y in np.ndindex((len(resources[0]), len(resources[0][0]))):
            if resources[2][x][y] > 0:
                trans_pos = self.TransformResourcePos(np.array([x,y]))
                colour = [self.RED[0]*resources[0][x][y]/float(resources[2][x][y]), self.RED[1], self.RED[2]]
                pygame.draw.polygon(self.screen, colour, [(trans_pos[0], trans_pos[1]+2), (trans_pos[0]+28, trans_pos[1]+16), (trans_pos[0], trans_pos[1]+30), (trans_pos[0]-28, trans_pos[1]+16)], 2)
        
        for creature in livingCreatures.values():
            trans_pos = self.TransformPos(np.array([creature.pos()[0], creature.pos()[1]]))
            colour = np.clip([int(255*(creature.physChar()['energy']/creature.gen()['ReprThresh'])),
                    int(255*(creature.physChar()['energy']/creature.gen()['ReprThresh'])), 255], 0, 255)
            pygame.draw.circle(self.screen, colour, (trans_pos[0], trans_pos[1]), 2)
        
        print 'Map Updated'
        
        pygame.display.flip()
        self.clock.tick(15)

    def DisplaySavedMap(self, worldHistory, resourcesGRMaxE, mapFile="isometric_grass_and_water2.tmx"):
        mydir = os.path.dirname(os.path.realpath(__file__))
        subdir = 'Maps'
        mapfilepath = os.path.join(mydir, subdir, mapFile)
        gameMap = load_pygame(mapfilepath)
        images = []
        tmxdata = TiledMap(mapfilepath)
        
        for y in xrange(25):
            for x in xrange(25):
                image = gameMap.get_tile_image(x,y,0)
                images.append(image)
        
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    
            for step in xrange(len(worldHistory)):
                i = 0
                self.screen.fill(self.WHITE)
                for y in xrange(25):
                    for x in xrange(25):
                        trans_pos = self.TransformMap(np.array([x, y]))
                        self.screen.blit(images[i],(trans_pos[0], trans_pos[1]))
                        i += 1
                
                resources = worldHistory[step][2]
                for x,y in np.ndindex((resources.shape[0], resources.shape[1])):
                    if resourcesGRMaxE[0][x][y] > 0:
                        trans_pos = self.TransformResourcePos(np.array([x,y]))
                        colour = [self.RED[0]*resources[x][y]/float(resourcesGRMaxE[1][x][y]), self.RED[1], self.RED[2]]
                        pygame.draw.polygon(self.screen, colour, [(trans_pos[0], trans_pos[1]+2), (trans_pos[0]+28, trans_pos[1]+16), (trans_pos[0], trans_pos[1]+30), (trans_pos[0]-28, trans_pos[1]+16)], 2)
                #for resource in worldHistory[step][2].values():
                #    trans_pos = self.TransformResourcePos(np.array([resource.pos()[0], resource.pos()[1]]))
                #    colour = [self.RED[0]*(resource.E()/resource.maxE()),self.RED[1],self.RED[2]]
                #    #pygame.draw.rect(self.screen, colour, (trans_pos[0]-10, trans_pos[1]+6, 20, 20), 2)
                #    pygame.draw.polygon(self.screen, colour, [(trans_pos[0], trans_pos[1]+2), (trans_pos[0]+28, trans_pos[1]+16), (trans_pos[0], trans_pos[1]+30), (trans_pos[0]-28, trans_pos[1]+16)], 2)

                creatures = worldHistory[step][0]
                for i in xrange(len(creatures)):
                    trans_pos = self.TransformPos(np.array([int(creatures[i][1]), int(creatures[i][2])]))
                    colour = np.clip([int(255*(creatures[i][3]/creatures[i][5])),
                                int(255*(creatures[i][3]/creatures[i][5])), 255], 0, 255)
                    pygame.draw.circle(self.screen, colour, (trans_pos[0], trans_pos[1]), 2)
            
                pygame.display.flip()
                self.clock.tick(15)
            done = True