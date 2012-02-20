import pygame #import all of pygame
from pygame.locals import *
from xml.dom.minidom import parse #import XML parser for loading animations

import settings #load settings
import tileset #and the tileset manager

#class to hold one animation
class Animation:
	def __init__(self, anim_group, anim_dom):
		self.anim_group = anim_group #store parameters
		self.frames = [] #list of frames of this animation
		self.curr_anim_frame = 0 #current frame of the animation
		self.frames_left = 0 #frames left of the current animation frame
		if anim_dom.getAttribute("loop") == "true": #if this animation loops
			self.loop = True #say so
		else: #if it doesn't
			self.loop = False #say that
		#now, load the animation
		child = anim_dom.firstChild #get the first frame
		while child is not None: #loop while there are more frames
			if child.localName != "frame": #if it's not a frame
				child = child.nextSibling
				continue #don't process it
			sheet = child.getAttribute("sheet") #get the sheet to load from
			pos = child.getAttribute("pos").split(",") #get position within sheet
			wait = int(child.getAttribute("wait")) #get delay until next frame
			pos_x = int(pos[0].strip()) #parse out position within sheet
			pos_y = int(pos[1].strip())
			image = self.anim_group.sheets[sheet].get_tile(pos_x, pos_y) #get tile of this frame
			self.frames.append([image, wait]) #add it to the list of frames
			child = child.nextSibling #get next frame
	#start the animation again
	def start(self):
		self.curr_anim_frame = 0 #set current frame to the first
		self.anim_group.sprite.image = self.frames[0][0] #set image
		self.frames_left = self.frames[0][1] #load delay
	#update the animation
	def update(self):
		self.frames_left -= 1 #one frame has passed
		if self.frames_left == 0: #if there aren't any frames left
			self.curr_anim_frame += 1 #go to next animation frame
			if self.curr_anim_frame == len(self.frames): #if there aren't any left
				if self.loop: #if we're supposed to loop
					self.curr_anim_frame = 0 #go back to first frame
				else: #otherwise
					self.anim_group.curr_animation = self.anim_group.old_animation #go back to the old animation
					self.anim_group.curr_animation.start() #and start it up
					return
			self.anim_group.sprite.image = self.frames[self.curr_anim_frame][0] #set image
			self.frames_left = self.frames[self.curr_anim_frame][1] #load delay
	
#group of animations
class AnimationGroup:
	def __init__(self, g, sprite, anim_file):
		self.g = g #store parameters
		self.sprite = sprite
		
		self.animations = {} #dictionary of the different animations
		self.sheets = {} #dictionary of the different sheets
		self.curr_animation = None #pointer to the current animation
		self.old_animation = None #pointer to the old animation, used for looping
		
		#load the animations from the file provided
		anim_dom = parse(anim_file).documentElement
		#load all of the animation sheets
		for sheet in anim_dom.getElementsByTagName("sheet"):
			width = int(sheet.getAttribute("tilewidth")) #get size of tiles
			height = int(sheet.getAttribute("tileheight"))
			image = sheet.getAttribute("from") #get path to image
			id = sheet.getAttribute("id") #and image ID
			self.sheets[id] = tileset.Tileset(image, width, height) #create the tileset
		
		#load all of the animations
		for anim in anim_dom.getElementsByTagName("animation"):
			id = anim.getAttribute("id") #get id of the animation
			self.animations[id] = Animation(self, anim) #create the animation
	#start an animation playing
	def set_animation(self, anim_id):
		self.old_animation = self.curr_animation #store current animation
		self.curr_animation = self.animations[anim_id] #load new one
		self.curr_animation.start() #start it going
	#update the animation
	def update(self):
		self.curr_animation.update() #update the current animation