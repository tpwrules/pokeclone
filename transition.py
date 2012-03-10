import pygame #load pygame
from pygame.locals import *

import settings

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
			
#shift the screen to the left
class ScreenShift:
	def __init__(self, speed):
		self.speed = speed #store fade speed
		self.moved = 0 #store amount moved
		self.running = True #we're currently running
	def update(self, surf):
		if not self.running: return True #return and say we're done if we're not running
		self.moved += self.speed #increment amount moved
		surf.scroll(-self.moved, 0) #scroll the surface
		#clear the area where the screen was
		surf.fill((0, 0, 0), (settings.screen_x-self.moved, 0, settings.screen_x, settings.screen_y))
		if self.moved > settings.screen_x: #if we're done moving
			self.running = False #we're not running
			return True #say we're done