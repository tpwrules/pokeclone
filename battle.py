import pygame #import everything pygame-related
from pygame.locals import *
import random #load rng for determining battle stuff

import dialog #load dialog manager
import settings #and game settings
import transition

class Battle: #class to manage a battle
	def __init__(self, game): #initialize ourselves
		self.g = game.g #store parameters
		self.game = game
		self.player = game.player
		self.g.update_func = self.update #store update function
		self.g.battle = self #store ourselves in globals
		#create a surface to render on
		self.surf = pygame.Surface((settings.screen_x, settings.screen_y))
	def start_wild(self, type, level): #start a wild battle
		self.wild = True #this is a wild battle
		self.dlog = dialog.Dialog(self.g, "standard") #initialize a new dialog to draw with temporarily
		#say what the encounter was
		self.dlog.draw_text("You encountered a {br}"+type+" at level "+str(level)+"!{wait}")
	def done(self): #called when battle is done
		self.g.battle = None #remove ourselves from globals
		self.g.update_func = self.game.update #restore game update function
		self.game.transition(transition.FadeIn(25)) #start a fade in
	def update(self): #update ourselves
		self.surf.fill((255, 255, 255)) #clear our surface
		r = self.dlog.update(self.surf, (0, 1)) #update dialog
		if r is True: #if it finished
			self.done() #battle is finished
		return self.surf #return surface to render