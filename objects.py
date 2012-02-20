import pygame #load all of pygame
from pygame.locals import *

import settings #load settings
import animation #load animation manager

#utility functions
def get_direction_name(direction): #return a name for each direction
	if direction == 0:
		return "up"
	elif direction == 1:
		return "down"
	elif direction == 2:
		return "left"
	elif direction == 3:
		return "right"
#class for the player object
class Player(pygame.sprite.Sprite):
	def __init__(self, game, element, properties):
		pygame.sprite.Sprite.__init__(self) #init the sprite class
		self.g = game.g #store parameters
		self.game = game
		self.properties = properties
		#load animations
		self.animator = animation.AnimationGroup(self.g, self, "data/objects/player/player_animation.xml")
		self.animator.set_animation("stand_down") #set current animation
		self.animator.update() #let it update once
		self.collidepoint = (16, 23) #set where to check for collisions
		self.size = (32, 32) #set sprite size
		self.pos = [int(element.getAttribute("x")), int(element.getAttribute("y"))] #set sprite position
		self.tile_pos = (self.pos[0]/16, (self.pos[1]/16)+1) #set position within tilemap
		self.rect = pygame.Rect(self.pos, self.size) #turn it into a rect
		self.move_direction = (0, 0) #we aren't moving in a particular direction
		self.direction = 1 #we're facing down
		self.moving = False #we aren't moving at all
		self.move_frames = 0 #amount of movement frames left
	#move the player
	def move(self, direction):
		same = direction == self.direction #true if we aren't changing direction
		self.direction = direction #set current direction
		self.move_frames = 8 #always 8 frames of movement
		if direction == 0: #move up
			if self.game.get_tile_type(self.tile_pos[0], self.tile_pos[1]-1) != 0: #if it's a solid tile
				pass #don't move
			else: #otherwise
				self.move_direction = (0, -2) #set movement
				self.moving = True #and we're moving
				self.tile_pos = (self.tile_pos[0], self.tile_pos[1]-1) #update tile position
		elif direction == 1:
			if self.game.get_tile_type(self.tile_pos[0], self.tile_pos[1]+1) != 0: #if it's a solid tile
				pass #don't move
			else: #otherwise
				self.move_direction = (0, 2) #set movement
				self.moving = True #and we're moving
				self.tile_pos = (self.tile_pos[0], self.tile_pos[1]+1) #update tile position
		elif direction == 2:
			if self.game.get_tile_type(self.tile_pos[0]-1, self.tile_pos[1]) != 0: #if it's a solid tile
				pass #don't move
			else: #otherwise
				self.move_direction = (-2, 0) #set movement
				self.moving = True #and we're moving
				self.tile_pos = (self.tile_pos[0]-1, self.tile_pos[1]) #update tile position
		elif direction == 3:
			if self.game.get_tile_type(self.tile_pos[0]+1, self.tile_pos[1]) != 0: #if it's a solid tile
				pass #don't move
			else: #otherwise
				self.move_direction = (2, 0) #set movement
				self.moving = True #and we're moving
				self.tile_pos = (self.tile_pos[0]+1, self.tile_pos[1]) #update tile position
		if not same: #if we changed direction
			self.animator.set_animation("walk_"+get_direction_name(direction)) #update our animation
	#update the player
	def update(self):
		if self.moving == True: #if we're currently moving
			self.pos[0] += self.move_direction[0] #move
			self.pos[1] += self.move_direction[1]
			self.rect = pygame.Rect(self.pos, self.size) #update draw rect
			self.move_frames -= 1 #decrement amount of movement frames
			if self.move_frames == 0: #if we aren't moving any more
				self.moving = False #say so
			else: #if we are
				self.animator.update() #update animation
				return #don't do anything else
		if self.g.keys[settings.key_up]: #if up is pressed
			self.move(0) #move up
		elif self.g.keys[settings.key_down]: #same for other keys
			self.move(1)
		elif self.g.keys[settings.key_left]:
			self.move(2)
		elif self.g.keys[settings.key_right]:
			self.move(3)
		if self.moving == False: #if we're not moving
			self.animator.set_animation("stand_"+get_direction_name(self.direction)) #set our animation accordingly
		self.animator.update() #update our animation	
		
#dictionary to hold which classes go with which objects
obj_types = {"Player": Player} #player object