import pygame #load all of pygame
from pygame.locals import *

import settings #load settings
import animation #load animation manager

#class for the player object
class Player(pygame.sprite.Sprite):
	def __init__(self, game, element, properties):
		pygame.sprite.Sprite.__init__(self) #init the sprite class
		self.g = game.g #store parameters
		self.game = game
		self.properties = properties
		#load animations
		self.animator = animation.AnimationGroup(self.g, self, "data/objects/player/player_animation.xml")
		self.animator.set_animation("walk_down") #set current animation
		self.animator.update() #let it update once
		self.size = (32, 32) #set sprite size
		self.pos = [int(element.getAttribute("x")), int(element.getAttribute("y"))] #set sprite position
		self.rect = pygame.Rect(self.pos, self.size) #turn it into a rect
	#update the player
	def update(self):
		self.animator.update() #update our animation
		
		
#dictionary to hold which classes go with which objects
obj_types = {"Player": Player} #player object