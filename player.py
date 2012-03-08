import pygame #load all of pygame
from pygame.locals import *

import settings #load settings
import animation #load animation manager
import dialog #load dialog manager

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
		self.in_water = False #whether we're currently walking in water
	#move the player
	def move(self, direction, force=False):
		same = (direction == self.direction) #true if we aren't changing direction
		self.direction = direction #set current direction
		self.move_frames = 4 #always 8 frames of movement
		if direction == 0: #move up
			if self.collide((self.tile_pos[0], self.tile_pos[1]-1)) and not force: #if it's a solid tile
				pass #don't move
			else: #otherwise
				self.move_direction = (0, -4) #set movement
				self.moving = True #and we're moving
				self.tile_pos = (self.tile_pos[0], self.tile_pos[1]-1) #update tile position
		elif direction == 1:
			if self.collide((self.tile_pos[0], self.tile_pos[1]+1)) and not force: #if it's a solid tile
				pass #don't move
			else: #otherwise
				self.move_direction = (0, 4) #set movement
				self.moving = True #and we're moving
				self.tile_pos = (self.tile_pos[0], self.tile_pos[1]+1) #update tile position
		elif direction == 2:
			if self.collide((self.tile_pos[0]-1, self.tile_pos[1])) and not force: #if it's a solid tile
				pass #don't move
			else: #otherwise
				self.move_direction = (-4, 0) #set movement
				self.moving = True #and we're moving
				self.tile_pos = (self.tile_pos[0]-1, self.tile_pos[1]) #update tile position
		elif direction == 3:
			if self.collide((self.tile_pos[0]+1, self.tile_pos[1])) and not force: #if it's a solid tile
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
		dest_pos = (self.tile_pos[0]+t[0], self.tile_pos[1]+t[1]) #calculate the position of what we're interacting with
		if dest_pos in self.game.pos2obj: #if there's an object at this position
			self.game.interact(dest_pos, self.direction) #interact with an object
			return
		tile_type = self.game.get_tile_type(dest_pos[0], dest_pos[1]) #get type of tile we're interacting with
		dlog = dialog.Dialog(self.g, "notify") #make a notify dialog
		if tile_type == settings.TILE_WATER and not self.in_water: #if it's a water tile and we're not in water
			self.game.show_dlog("Would you like to SURF?{choices}YES{endchoice}NO{endchoice}{endchoices}", dlog=dlog, callback=self.surf_cb) #ask if the user wants to surf
		elif tile_type == settings.TILE_NORMAL and self.in_water: #if it's a normal tile and we're in water
			self.game.show_dlog("Red took off his JESUS BOOTS.{wait}", dlog=dlog) #show take off message
			self.move(self.direction, True) #move out of water
			self.in_water = False #we're not in water any more
	def surf_cb(self, result): #callback for surf dialog
		dlog = dialog.Dialog(self.g, "notify") #make a notify dialog
		if result == 0: #if they said yes
			self.game.show_dlog("Red put on his JESUS BOOTS!{wait}", dlog=dlog) #show message
			self.move(self.direction, True) #start movement
			self.in_water = True #we're in water now
		else:
			#if they say no, don't surf
			self.game.show_dlog("Excellent. The land is better anyways.{wait}", dlog=dlog)
	def collide(self, tile_pos): #check for collisions
		type = self.game.get_tile_type(tile_pos[0], tile_pos[1]) #get type of tile
		if self.in_water: #if we're in water
			return type not in [settings.TILE_WATER] #return collisions
		else: #if we're on land
			return type not in [settings.TILE_NORMAL, settings.TILE_GRASS, settings.TILE_DOUBLEGRASS]
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