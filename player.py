import pygame #load all of pygame
from pygame.locals import *

import settings #load settings
import animation #load animation manager
import dialog #load dialog manager
import random
import transition
import objects #used for the render things

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
class Player(objects.RenderedNPC):
	def __init__(self, game):
		objects.RenderedNPC.__init__(self) #init NPC renderer
		self.g = game.g #store parameters
		self.game = game
		#load animations
		self.animator = animation.AnimationGroup(self.g, self, "data/objects/player/player_animation.xml")
		self.collidepoint = (16, 23) #set where to check for collisions
		self.size = (32, 32) #set sprite size
		self.tile_pos = self.g.save.get_prop("player", "pos", [15, 16]) #load current position
		self.pos = [((self.tile_pos[0]-1)*16)+8, (self.tile_pos[1]-1)*16] #set position in pixels
		self.rect = pygame.Rect(self.pos, self.size) #turn it into a rect
		self.move_direction = (0, 0) #we aren't moving in a particular direction
		self.direction = self.g.save.get_prop("player", "direction", 1) #load direction
		self.animator.set_animation("stand_"+get_direction_name(self.direction)) #set proper direction
		self.animator.update() #let it update
		self.moving = False #we aren't moving at all
		self.was_moving = False
		self.move_frames = 0 #amount of movement frames left
		self.in_water = False #whether we're currently walking in water
		self.notify_dlog = dialog.Dialog(self.g, "notify") #initialize a notify dialog
		self.visible = True #and we should be showing ourselves
	#move the player
	def move(self, direction, force=False):
		same = (direction == self.direction) #true if we aren't changing direction
		self.direction = direction #set current direction
		#decide our speed
		if self.g.keys[settings.key_cancel]: #if cancel key is pressed
			speed = 4 #we're moving at 4 pixels/frame
			self.move_frames = 4
		else: #if it isn't pressed
			speed = 2 #we're moving at 2 pixels/frame
			self.move_frames = 8
		if direction == 0: #move up
			if self.collide((self.tile_pos[0], self.tile_pos[1]-1)) and not force: #if it's a solid tile
				pass #don't move
			else: #otherwise
				self.move_direction = (0, -speed) #set movement
				self.moving = True #and we're moving
				self.tile_pos = (self.tile_pos[0], self.tile_pos[1]-1) #update tile position
		elif direction == 1:
			if self.collide((self.tile_pos[0], self.tile_pos[1]+1)) and not force: #if it's a solid tile
				pass #don't move
			else: #otherwise
				self.move_direction = (0, speed) #set movement
				self.moving = True #and we're moving
				self.tile_pos = (self.tile_pos[0], self.tile_pos[1]+1) #update tile position
		elif direction == 2:
			if self.collide((self.tile_pos[0]-1, self.tile_pos[1])) and not force: #if it's a solid tile
				pass #don't move
			else: #otherwise
				self.move_direction = (-speed, 0) #set movement
				self.moving = True #and we're moving
				self.tile_pos = (self.tile_pos[0]-1, self.tile_pos[1]) #update tile position
		elif direction == 3:
			if self.collide((self.tile_pos[0]+1, self.tile_pos[1])) and not force: #if it's a solid tile
				pass #don't move
			else: #otherwise
				self.move_direction = (speed, 0) #set movement
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
		tile_type = self.game.get_tile_type(dest_pos[0], dest_pos[1], True) #get type of tile we're interacting with
		if tile_type == settings.TILE_WATER and not self.in_water: #if it's a water tile and we're not in water
			self.game.show_dlog("Would you like to SURF?{choices}YES{endchoice}NO{endchoice}{endchoices}", dlog=self.notify_dlog, callback=self.surf_cb) #ask if the user wants to surf
		elif tile_type == settings.TILE_NORMAL and self.in_water: #if it's a normal tile and we're in water
			self.game.show_dlog("Red took off his JESUS BOOTS.{wait}", dlog=self.notify_dlog) #show take off message
			self.move(self.direction, True) #move out of water
			self.in_water = False #we're not in water any more
	def surf_cb(self, result): #callback for surf dialog
		if result == 0: #if they said yes
			self.game.show_dlog("Red put on his JESUS BOOTS!{wait}", dlog=self.notify_dlog) #show message
			self.move(self.direction, True) #start movement
			self.in_water = True #we're in water now
		else:
			#if they say no, don't surf
			self.game.show_dlog("Excellent. The land is better anyways.{wait}", dlog=self.notify_dlog)
	def collide(self, tile_pos): #check for collisions
		tile_type = self.game.get_tile_type(tile_pos[0], tile_pos[1], True) #get type of tile
		if self.in_water: #if we're in water
			return tile_type not in [settings.TILE_WATER] #return collisions
		else: #if we're on land
			return tile_type not in [settings.TILE_NORMAL, settings.TILE_GRASS, settings.TILE_DOUBLEGRASS]
	def step(self): #handle stepping on a tile
		if self.tile_pos in self.game.warps: #if we're standing on a warp
			self.game.prepare_warp(self.tile_pos) #do the warp
			return True #something happened
		tile_type = self.game.get_tile_type(self.tile_pos[0], self.tile_pos[1], True) #get the tile we're standing on
		if tile_type in [settings.TILE_GRASS, settings.TILE_DOUBLEGRASS]: #if there's the potential for a battle
			return self.game.try_battle() #try to start one
	#update the player
	def update(self):
		if self.moving == True: #if we're currently moving
			self.pos[0] += self.move_direction[0] #move
			self.pos[1] += self.move_direction[1]
			self.rect = pygame.Rect(self.pos, self.size) #update draw rect
			self.move_frames -= 1 #decrement amount of movement frames
			if self.move_frames == 0: #if we aren't moving any more
				self.moving = False #say so
				r = self.step() #handle stepping on a new tile
				if r is True: #if something special happened
					return #stop doing things
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
	def save(self): #save our data
		self.g.save.set_prop("player", "pos", self.tile_pos[:]) #store our position
		self.g.save.set_prop("player", "direction", self.direction) #and direction