import pygame #import everything pygame-related
from pygame.locals import *

import game #load game engine

class TitleScreen: #class for the title screen
	def __init__(self, g):
		self.g = g #store globals
	def start_game(self): #start the game running
		self.g.title_screen = None #remove ourselves from the globals
		self.g.game = game.Game(self.g) #initialize a new game
		self.g.game.start() #tell it to start running
		self.g.update_func = self.g.game.update #store new update function
	def update(self): #update ourselves
		self.start_game() #for now, just start the game when we're updated
		return pygame.Surface((1, 1)) #return bogus surface