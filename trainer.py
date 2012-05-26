#class for trainer object management
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
		#load spotted icon
		self.spotted_pic = data.load_image("trainers/spotted.png")
		self.spotted_pic.convert_alpha()
		#get whether we have been fought or not
		self.fought = self.g.save.get_prop(self.id, "fought", False)
		self.moving = True
		self.seen = False #set if we've seen somebody
		self.move_data = [0, 0, 0] #store the movement we're going to do
		self.wait_time = 0 #amount of time to display icon
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
		t.start_trainer(self)
		self.fought = True #we've been fought now
	def move_done(self):
		self.interacting = True #we should be interacting now
		#set proper animation
		self.animator.set_animation("stand_"+objects.get_direction_name(self.move_manager.curr_movement[0]))
		self.stored_anim = self.animator.curr_animation
		self.script_manager.start_script(self.pre_script) #start script running
	def run_interaction(self): #do interaction
		self.should_interact = False #we're not waiting for interaction any more
		if not self.fought: #if we haven't been fought yet
			self.seen = True #we have been seen
			self.move_manager.curr_movement[0] = self.interact_pos #set proper direction
			self.move_done() #begin battle
		else: #if we have
			objects.NPC.run_interaction(self) #interact as normal
	def interacting_stopped(self):
		if self.seen: #if we have seen somebody and interaction stopped
			self.game.transition(transition.WavyScreen(), self.start_battle) #do transition
		self.game.stopped = False #let player move
	def do_seen(self, dir, dist, tp): #somebody has been seen
		if dist < 0: return #return if we're too near the player
		self.tile_pos = tp[:]
		self.game.set_obj_pos(self, tp)
		self.seen = True #we've seen somebody
		self.wait_time = 30 #set amount of time to display icon
		self.move_data[0] = dir #store movement
		self.move_data[1] = dist
		self.move_data[2] = self.move_manager.pix_pos #store position within tile so we don't jump
		self.moving = False #stop moving for now
		#set standing animation
		self.animator.set_animation("stand_"+objects.get_direction_name(dir))
		self.game.stopped = True #stop player from moving
	def draw(self, surf): #draw ourselves
		if self.wait_time > 0: #if we're supposed to be drawing the icon
			#draw it
			surf.blit(self.spotted_pic, (self.rect.x+8, self.rect.y-12))
		objects.NPC.draw(self, surf)
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
				if r is True and self.wait_time == 0 and not self.fought: #if movement has finished
					self.move_done() #handle it
				elif self.move_manager.pix_pos == 0 and self.should_interact: #if we're currently on a tile boundary
					self.run_interaction() #start interacting
			self.rect = pygame.Rect(self.pos, (32, 32)) #update sprite rect
		else: #if we are
			self.script_manager.update() #update script
			self.interacting = self.script_manager.running #set whether we're interacting
			if not self.interacting: #if we've stopped needing to
				self.animator.curr_animation = self.stored_anim #restore stored animation
				self.interacting_stopped() #do callback
		self.animator.update() #update our animation
		if self.wait_time > 0: #if we're waiting to move
			self.wait_time -= 1 #decrement wait time
			if self.wait_time == 0: #if we're done waiting
				#start movement
				self.moving = True
				self.move_manager.move_to(self.move_data[0], self.move_data[1], 1, False)
				self.move_manager.pix_pos = self.move_data[2] #restore position
		if self.seen or self.fought: return #don't try to find people if we've seen somebody already
		player_pos = self.game.player.tile_pos[:] #get position of player
		curr_dir = self.move_manager.curr_movement[0] #and the direction we're facing
		tile_pos = self.tile_pos[:] #adjust our position
		if curr_dir == 0:
			tile_pos[1] += 1
		elif curr_dir == 1:
			tile_pos[1] -= 1
		elif curr_dir == 2:
			tile_pos[0] += 1
		elif curr_dir == 3:
			tile_pos[0] -= 1
		if curr_dir < 2: #facing up or down
			if tile_pos[0] != player_pos[0]: return #if X is different, we can't be interacting
			if curr_dir == 1: #facing down
				if tile_pos[1] > player_pos[1]: return #we can't be interacting if the player is below us
				dist = player_pos[1]-tile_pos[1] #get distance between us and player
				if dist > self.vision: return #return if we can't see them
				self.do_seen(1, dist-1, tile_pos) #do move
			elif curr_dir == 0: #facing up
				if tile_pos[1] < player_pos[1]: return #we can't be interacting if the player is above us
				dist = tile_pos[1]-player_pos[1] #get distance between us and player
				if dist > self.vision: return #return if we can't see them
				self.do_seen(0, dist-1, tile_pos)
		else: #facing left or right
			if tile_pos[1] != player_pos[1]: return #if Y is different, we can't be interacting
			if curr_dir == 3: #facing right
				if tile_pos[0] > player_pos[0]: return #we can't be interacting if the player is below us
				dist = player_pos[0]-tile_pos[0] #get distance between us and player
				if dist > self.vision: return #return if we can't see them
				self.do_seen(3, dist-1, tile_pos)
			elif curr_dir == 2: #facing left
				if tile_pos[0] < player_pos[0]: return #we can't be interacting if the player is above us
				dist = tile_pos[0]-player_pos[0] #get distance between us and player
				if dist > self.vision: return #return if we can't see them
				self.do_seen(2, dist-1, tile_pos)
	def save(self): #save our data
		self.g.save.set_prop(self.id, "fought", self.fought) #save whether we've been fought