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
	def __init__(self, game):
		pygame.sprite.Sprite.__init__(self) #init the sprite class
		self.g = game.g #store parameters
		self.game = game
		#load animations
		self.animator = animation.AnimationGroup(self.g, self, "data/objects/player/player_animation.xml")
		self.animator.set_animation("stand_down") #set current animation
		self.animator.update() #let it update once
		self.collidepoint = (16, 23) #set where to check for collisions
		self.size = (32, 32) #set sprite size
		self.pos = [248, 256]
		self.tile_pos = ((self.pos[0]/16)+1, (self.pos[1]/16)+1) #set position within tilemap
		self.rect = pygame.Rect(self.pos, self.size) #turn it into a rect
		self.move_direction = (0, 0) #we aren't moving in a particular direction
		self.direction = 1 #we're facing down
		self.moving = False #we aren't moving at all
		self.was_moving = False
		self.move_frames = 0 #amount of movement frames left
	#move the player
	def move(self, direction):
		same = (direction == self.direction) #true if we aren't changing direction
		self.direction = direction #set current direction
		self.move_frames = 4 #always 8 frames of movement
		if direction == 0: #move up
			if self.collide((self.tile_pos[0], self.tile_pos[1]-1)): #if it's a solid tile
				pass #don't move
			else: #otherwise
				self.move_direction = (0, -4) #set movement
				self.moving = True #and we're moving
				self.tile_pos = (self.tile_pos[0], self.tile_pos[1]-1) #update tile position
		elif direction == 1:
			if self.collide((self.tile_pos[0], self.tile_pos[1]+1)): #if it's a solid tile
				pass #don't move
			else: #otherwise
				self.move_direction = (0, 4) #set movement
				self.moving = True #and we're moving
				self.tile_pos = (self.tile_pos[0], self.tile_pos[1]+1) #update tile position
		elif direction == 2:
			if self.collide((self.tile_pos[0]-1, self.tile_pos[1])): #if it's a solid tile
				pass #don't move
			else: #otherwise
				self.move_direction = (-4, 0) #set movement
				self.moving = True #and we're moving
				self.tile_pos = (self.tile_pos[0]-1, self.tile_pos[1]) #update tile position
		elif direction == 3:
			if self.collide((self.tile_pos[0]+1, self.tile_pos[1])): #if it's a solid tile
				pass #don't move
			else: #otherwise
				self.move_direction = (4, 0) #set movement
				self.moving = True #and we're moving
				self.tile_pos = (self.tile_pos[0]+1, self.tile_pos[1]) #update tile position
		self.game.set_obj_pos(self, self.tile_pos) #set our position
		if not same or not self.was_moving: #if we need to update our animation
			self.animator.set_animation("walk_"+get_direction_name(direction)) #update our animation
		self.was_moving = self.moving
	#have the player interact with an object
	def interact(self):
		t = None #tuple of tile position
		#set direction tuple according to direction
		if self.direction == 0: #if we're facing up
			t = (0, -1)
		elif self.direction == 1:
			t = (0, 1)
		elif self.direction == 2:
			t = (-1, 0)
		elif self.direction == 3:
			t = (1, 0)
		self.game.interact((self.tile_pos[0]+t[0], self.tile_pos[1]+t[1]), self.direction) #interact with an object
	def collide(self, tile_pos): #check for collisions
		return self.game.collide(tile_pos)
	#update the player
	def update(self):
		if self.moving == True: #if we're currently moving
			self.pos[0] += self.move_direction[0] #move
			self.pos[1] += self.move_direction[1]
			self.rect = pygame.Rect(self.pos, self.size) #update draw rect
			self.move_frames -= 1 #decrement amount of movement frames
			if self.move_frames == 0: #if we aren't moving any more
				self.moving = False #say so
				if self.tile_pos in self.game.warps: #if we're standing on a warp
					self.game.prepare_warp(self.tile_pos) #warp
					return #and just return
			else: #if we are
				self.animator.update() #update animation
				return #don't do anything else
		if self.game.dialog_drawing: #if a dialog is currently being shown
			return #don't do anything
		if self.g.keys[settings.key_up]: #if up is pressed
			self.move(0) #move up
		elif self.g.keys[settings.key_down]: #same for other keys
			self.move(1)
		elif self.g.keys[settings.key_left]:
			self.move(2)
		elif self.g.keys[settings.key_right]:
			self.move(3)
		if self.moving == False: #if we're not moving
			self.was_moving = False #clear was moving flag
			self.animator.set_animation("stand_"+get_direction_name(self.direction)) #set our animation accordingly
			if self.g.curr_keys[settings.key_accept]: #if the accept key is pressed
				self.interact() #try to interact with something
		self.animator.update() #update our animation