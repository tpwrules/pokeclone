import pygame #load pygame
from pygame.locals import *

#fade from transparent to black
class FadeOut:
	def __init__(self, speed):
		self.speed = speed #store fade speed
		self.color = 255 #store current fade color
		self.running = True #we're currently running
	def update(self, surf):
		if not self.running: return True #return and say we're done if we're not running
		self.color -= self.speed #fade closer to black
		if self.color < 0: self.color = 0 #if we've gone negative, set to zero
		surf.fill((self.color,)*4, special_flags=BLEND_RGBA_MULT) #draw the fade
		if self.color == 0: #if we've finished fading
			self.running = False #we're not running any more
			return True #say we're done
			
#fade from black to transparent
class FadeIn:
	def __init__(self, speed):
		self.speed = speed #store fade speed
		self.color = 0 #store current fade color
		self.running = True #we're currently running
	def update(self, surf):
		if not self.running: return True #return and say we're done if we're not running
		self.color += self.speed #fade closer to transparent
		if self.color > 255: self.color = 255 #if we've gone past the highest color, limit it
		surf.fill((self.color,)*4, special_flags=BLEND_RGBA_MULT) #draw the fade
		if self.color == 255: #if we've finished fading
			self.running = False #we're not running any more
			return True #say we're done