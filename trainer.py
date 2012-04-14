#class for trainer management
import pygame #import everything pygame-related
from pygame.locals import *

import objects
import data
import battle
import transition

class TrainerObject(objects.NPC):
	def __init__(self, game, element):
		self.g = game.g
		objects.NPC.__init__(self, game, element) #initialize our parent
		self.vision = int(data.get_xml_prop(element, "vision")) #load properties
		self.reward = int(data.get_xml_prop(element, "reward"))
		self.class_name = data.get_xml_prop(element, "class")
		self.trainer_name = data.get_xml_prop(element, "name")
		self.pre_script = data.get_node(element, "pre_script")
		self.post_script = data.get_node(element, "post_script")
		#get whether we have been fought or not
		self.fought = self.g.save.get_prop(self.id, "fought", False)
		self.moving = True
		self.seen = False #set if we've seen somebody
		#load party data
		party = []
		for node in data.get_node(element, "party").childNodes: #loop through pokemon
			if node.localName == "pokemon": #if it's a pokemon
				t = [node.getAttribute("type"), node.getAttribute("level")] #generate data
				party.append(t) #and save it
		self.party = party
	def start_battle(self):
		#begin battle
		t = battle.Battle(self.game) #create new battle
		t.start_wild("zubat", 6)
		self.fought = True #we've been fought now
	def move_done(self):
		self.moving = False #we're not moving any more
		self.interacting = True #we should be interacting now
		#set proper animation
		self.animator.set_animation("stand_"+objects.get_direction_name(self.move_manager.curr_movement[0]))
		self.stored_anim = self.animator.curr_animation
		self.script_manager.start_script(self.pre_script) #start script running
	def interacting_stopped(self):
		if self.seen: #if we have seen somebody and interaction stopped
			self.game.transition(transition.WavyScreen(), self.start_battle) #do transition
	def do_seen(self, dir, dist): #somebody has been seen
		self.seen = True #we've seen somebody
		self.pos = [((self.tile_pos[0]-1)*16)+8, (self.tile_pos[1]-1)*16]
		self.move_manager.move_to(dir, dist, 2, False) #move to player
		self.game.stopped = True #stop player from moving
	def update(self): #update ourselves
		if self.fought and self.seen: #if we've been fought and we saw somebody
			self.seen = False #we're not seeing people any more
			self.game.stopped = False #player doesn't need to be held any more
			self.interacting = True
			self.script_manager.start_script(self.post_script) #start post-battle script
		if not self.interacting: #if we aren't interacting
			if self.game.dialog_drawing: return #return if a dialog is being drawn
			if self.moving:
				r = self.move_manager.update() #update our movement
				if r is True: #if movement has finished
					self.move_done() #handle it
			self.rect = pygame.Rect(self.pos, (32, 32)) #update sprite rect
		else: #if we are
			self.script_manager.update() #update script
			self.interacting = self.script_manager.running #set whether we're interacting
			if not self.interacting: #if we've stopped needing to
				self.animator.curr_animation = self.stored_anim #restore stored animation
				self.interacting_stopped() #do callback
		self.animator.update() #update our animation
		if self.seen or self.fought: return #don't try to find people if we've seen somebody already
		player_pos = self.game.player.tile_pos[:] #get position of player
		curr_dir = self.move_manager.curr_movement[0] #and the direction we're facing
		if curr_dir < 2: #facing up or down
			if self.tile_pos[0] != player_pos[0]: return #if X is different, we can't be interacting
			if curr_dir == 1: #facing down
				if self.tile_pos[1] > player_pos[1]: return #we can't be interacting if the player is below us
				dist = player_pos[1]-self.tile_pos[1] #get distance between us and player
				if dist > self.vision: return #return if we can't see them
				self.do_seen(1, dist-1) #do move
			elif curr_dir == 0: #facing up
				if self.tile_pos[1] < player_pos[1]: return #we can't be interacting if the player is above us
				dist = self.tile_pos[1]-player_pos[1] #get distance between us and player
				if dist > self.vision: return #return if we can't see them
				self.do_seen(0, dist-1)
		else: #facing left or right
			if self.tile_pos[1] != player_pos[1]: return #if Y is different, we can't be interacting
			if curr_dir == 3: #facing right
				if self.tile_pos[0] > player_pos[0]: return #we can't be interacting if the player is below us
				dist = player_pos[0]-self.tile_pos[0] #get distance between us and player
				if dist > self.vision: return #return if we can't see them
				self.do_seen(3, dist-1)
			elif curr_dir == 2: #facing left
				if self.tile_pos[0] < player_pos[0]: return #we can't be interacting if the player is above us
				dist = self.tile_pos[0]-player_pos[0] #get distance between us and player
				if dist > self.vision: return #return if we can't see them
				self.do_seen(2, dist-1)
	def save(self): #save our data
		self.g.save.set_prop(self.id, "fought", self.fought) #save whether we've been fought