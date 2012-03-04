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
		
def get_direction_num(direction): #return a number for each direction name
	if direction == "up":
		return 0
	elif direction == "down":
		return 1
	elif direction == "left":
		return 2
	elif direction == "right":
		return 3

#class to manage object movement
class MovementManager:
	def __init__(self, obj): #initialize the manager
		self.obj = obj #store object
		self.curr_movement = [] #current movement directions
		self.store_movement = [] #stored movement directions, used for resuming
		self.move_list = [] #list of movements
		self.running = False #whether we're currently supposed to be auto moving
		self.repeat = False #whether we are going to repeat the movement list
		self.move_index = 0 #current movement index
		self.resume = False #whether we're going to resume the movement list
		self.moving = False #whether we're moving at all
	def load_move_dom(self, dom): #load a movement list from xml
		move_list = [] #list of movements
		child = dom.firstChild #get first movement
		default_speed = int(dom.getAttribute("speed")) #get default speed
		while child is not None: #loop through movement list
			if child.localName == "move": #if it's a movement command
				#get movement speed
				speed = int(child.getAttribute("speed")) if child.getAttribute("speed") != "" else default_speed
				dist = int(child.getAttribute("dist")) #get movement distance
				dir = get_direction_num(child.getAttribute("dir")) #get direction
				move_list.append([dir, dist, speed]) #add it to movement list
			elif child.localName == "wait": #if it's a wait command
				frames = int(child.getAttribute("frames")) #get number of frames to wait
				dir = get_direction_num(child.getAttribute("dir")) #get direction
				move_list.append([dir, frames, -1]) #add it to movement list
		self.load_move_list(move_list) #set movement list we generated
	def load_move_list(self, move_list, repeat=True): #load a movement list
		self.running = True #we're running now
		self.repeat = repeat #set repeat
		self.move_list = move_list #set movement list
		self.move_index = -1 #set move index to starting
		self.resume = False #clear other variables
		self.moving = True
		self._next_movement() #go to next movement command
	def _next_movement(self): #go to next movement
		self.move_index += 1 #increment move index
		if self.move_index == len(self.move_list): #if we're at the end of the movement list
			if self.repeat: #if we're supposed to repeat
				self.move_index = 0 #zero movement index
			else: #if we're not supposed to repeat
				self.moving = False #stop doing things
				self.running = False
				self.obj.animator.set_animation("stand_"+get_movement_name(self.move_list[-1][0])) #set stand animation
				return
		self.curr_movement = self.move_list[self.move_index][:] #load move list
		self._start_move() #start moving
	def _start_move(self): #start movement
		dir, dist, speed = self.curr_movement #load current movement
		self.moving = True #start moving
		#calculate movement deltas
		if dir == 0: #moving up
			delta = (0, -speed)
			pix_pos = 15
		elif dir == 1: #down
			delta = (0, speed)
			pix_pos = 0
		elif dir == 2: #left
			delta = (-speed, 0)
			pix_pos = 15
		elif dir == 3: #right
			delta = (speed, 0)
			pix_pos = 0
		#set movement animation
		if speed < 0: #if it's just a wait command
			self.obj.animator.set_animation("stand_"+get_movement_name(dir)) #set stand animation
		else: #otherwise, 
			self.obj.animator.set_animation("walk_"+get_movement_name(dir)) #set walk animation
		self.pix_pos = pix_pos #number of pixels we've moved within the tile
		self.delta = delta #store delta
	def move_to(self, dir, dist, speed, resume=True): #set a movement
		self.resume = resume #set whether we're supposed to resume or not
		self.store_movement = self.curr_movement[:] #back up movement
		self.store_delta = self.delta #and delta
		self.store_pix_pos = self.pix_pos #and pixel position
		self.curr_movement = [dir, dist, speed] #store current movement
		self.running = False #we're not supposed to be automatically moving any more
		self._start_move() #start moving
	def update(self): #update movement
		if not self.moving: #if we're not doing anything
			return #don't do anything
		dir, dist, speed = self.curr_movement #load current movement
		if speed < 0: #if this is a wait command
			self.curr_movement[1] -= 1 #decrement a frame
			if self.curr_movement[1] == 0: #if we're finished waiting
				self._next_movement() #go to next move command
				return #and stop doing things
		self.obj.pos[0] += self.delta[0] #move object according to speed
		self.obj.pos[1] += self.delta[1]
		self.pix_pos += speed #add speed to pixel position
		if self.pix_pox > 15: #if we've gone a whole tile
			self.curr_movement[1] -= 1 #remove one from distance
			self.pix_pos -= 16 #remove a tile's worth of pixels
			#calculate new tile position
			if dir == 0:
				self.obj.tile_pos[1] -= 1
			elif dir == 1:
				self.obj.tile_pos[1] += 1
			elif dir == 2:
				self.obj.tile_pos[0] -= 1
			elif dir == 3:
				self.obj.tile_pos[0] += 1
		if self.curr_movement[1] == 0: #if we're finished moving
			#snap object's position to tile
			self.obj.pos[0] -= self.obj.pos[0] % 16
			self.obj.pos[1] -= self.obj.pos[1] % 16
			if self.running: #if we're supposed to be automatically running
				self._next_movement() #go to the next movement
			elif self.resume: #otherwise, if we're supposed to resume auto movement
				self.running = True #start auto movement
				self.resume = False #stop worrying about resuming
				self.curr_movement = self.store_movement[:] #restore backed up stuff
				self.delta = self.store_delta
				self.pix_pos = self.store_pix_pos

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