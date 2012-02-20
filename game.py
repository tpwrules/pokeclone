import pygame #import all of pygame
from pygame.locals import *
import settings

class Game: #class for our game engine
	def __init__(self, g):
		self.g = g #store global variables
		self.surf = pygame.Surface((settings.screen_x, settings.screen_y)) #create a new surface to display on
		self.surf.convert() #convert it to the display format for faster blitting
		self.surf.fill((255, 255, 255)) #fill it white for now
	def start(self):
		pass
	def update(self): #update the engine for this frame
		return self.surf #return the rendered surface