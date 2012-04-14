import pygame #load pygame
from pygame.locals import *
import math

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
			
#wave the screen out
class WavyScreen:
	def __init__(self):
		self.running = True #we're currently running
		self.amplitude = 1.0 #store initial settings
		self.degrees = 0.1
		self.frames = 40
		self.fade = 255.0
	def update(self, surf):
		if not self.running: return True #return if we're not running
		#loop through all the rows in the screen and shift them individually
		for y in xrange(0, settings.screen_y):
			surf.set_clip((0, y, settings.screen_x, 1)) #set clipping rect for this row
			delta = math.sin(self.degrees)*self.amplitude #calculate scroll value
			surf.scroll(int(delta), 0) #scroll surface
			self.degrees += 0.1 #increment degrees
			if delta < 0: #if the screen was scrolled to the left
				surf.fill((0, 0, 0), (settings.screen_x+delta, y, settings.screen_x, 1)) #fill scrolled off area
			else: #if screen was scrolled right
				surf.fill((0, 0, 0), (0, y, delta, 1)) #fill scrolled off area
		surf.set_clip(None) #clear clipping rect
		self.amplitude += 0.7 #increment amplitude for next frame
		self.frames -= 1 #and decrement frames
		if self.frames < 15: #if we're supposed to fade
			surf.fill((max(int(self.fade), 0), )*4, special_flags=BLEND_RGBA_MULT) #draw it
			self.fade -= 255/15 #decrement fade color
		if self.frames <= 0:
			surf.fill((0, 0, 0))
		if self.frames == -15: #if we've run out of frames
			self.running = False #we're not running
			return True #say we're done