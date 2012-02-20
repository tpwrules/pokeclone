import pygame #import all of pygame
from pygame.locals import *

import settings #load settings
import map #and map manager

class Game: #class for our game engine
	def __init__(self, g):
		self.g = g #store global variables
		self.surf = pygame.Surface((settings.screen_x, settings.screen_y)) #create a new surface to display on
		self.surf.convert() #convert it to the display format for faster blitting
		self.surf.fill((255, 255, 255)) #fill it white for now
	def start(self):
		self.map = map.Map(self.g, "data/maps/oasis.tmx") #load map 
	def update(self): #update the engine for this frame
		map_image = self.map.update() #get map image
		self.surf.blit(map_image, (0, 0)) #blit it
		return self.surf #return the rendered surface