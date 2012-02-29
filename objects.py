import pygame #load all of pygame
from pygame.locals import *

import settings #load settings
import animation #load animation manager

#warp point object
class Warp:
	def __init__(self, game, element, properties):
		self.g = game.g #store parameters
		self.game = game
		self.properties = properties
		#get tile we're monitoring
		t = self.properties["tile_pos"].split(",")
		self.tile_x = int(t[0].strip())
		self.tile_y = int(t[1].strip())
		game.add_warp((self.tile_x, self.tile_y), self.properties) #add the warp
	def update(self): #we don't need to do any updates
		pass
		
#dictionary to hold which classes go with which objects
obj_types = {"warp": Warp } #warp object