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

#sign object
class Sign:
	def __init__(self, game, element, properties):
		self.game = game #store parameters
		self.text = properties["text"] #store text to show
		#get our tile position
		t = properties["tile_pos"].split(",")
		self.tile_pos = (int(t[0].strip()), int(t[1].strip())) #store position
		game.set_obj_pos(self, self.tile_pos) #set our position
	def interact(self, pos): #handle the player interacting with us
		self.game.show_dlog(self.text) #show our text
	def update(self):
		pass #we don't need to do any updates
		
#dictionary to hold which classes go with which objects
obj_types = {"warp": Warp, #warp object \
"sign":Sign} #a sign object