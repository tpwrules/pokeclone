import pygame #import all of pygame
from pygame.locals import *
from xml.dom.minidom import parse #import XML parser for loading animations
import math #import math library for part animation calculation

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

class PartAnimationPart: #class for one part in the layout
	def __init__(self, set_, g, dom): #create a part based on an element
		self.g = g #store given parameters
		self.set = set_

		self.id = dom.getAttribute("id") #get id of this part
		set_.parts[self.id] = self #store ourselves
		self.pos = [int(x.strip()) for x in dom.getAttribute("pos").split(",")] #and position
		try: #load rotation
			self.rot = int(dom.getAttribute("rotation"))
		except:
			self.rot = 0
		try: #load scale
			t = float(dom.getAttribute("scale"))
		except:
			t = 1.0
		self.xscale, self.yscale = t, t
		try:
			self.xscale = float(dom.getAttribute("xscale"))
		except:
			pass
		try:
			self.yscale = float(dom.getAttribute("yscale"))
		except:
			pass
		self.image = set_.part_images[dom.getAttribute("from")][0] #load our image
		self.center = set_.part_images[dom.getAttribute("from")][1] #and store center
	def render(self, surf, x, y, xs, ys, rot, center): #render ourselves
		img = self.image #get starting surface
		#we need to rotate our coordinates to be in the correct position
		pos = [(self.pos[0]-center[0]+self.center[0]), (self.pos[1]-center[1]+self.center[1])]
		npos = [0,0]
		npos[0] = ((math.cos(math.radians(-rot))*pos[0]) - (math.sin(math.radians(-rot))*pos[1]))+center[0]-self.center[0]
		npos[1] = ((math.sin(math.radians(-rot))*pos[0]) + (math.cos(math.radians(-rot))*pos[1]))+center[1]-self.center[1]
		pos = npos[:]
		if xs*self.xscale != 1.0 or ys*self.yscale != 1.0: #if we need to scale
			old = (img.get_width(), img.get_height())
			size = (int(img.get_width()*xs*self.xscale), int(img.get_height()*ys*self.yscale)) #calculate new size
			img = pygame.transform.scale(img, size) #do the scale
			pos = (pos[0]-((img.get_width()-old[0])/2), pos[1]-((img.get_height()-old[1])/2))
		if rot+self.rot != 0: #if we need to rotate
			old = (img.get_width(), img.get_height())
			img = pygame.transform.rotate(img, rot+self.rot) #do so
			pos = (pos[0]-((img.get_width()-old[0])/2), pos[1]-((img.get_height()-old[1])/2))
		surf.blit(img, (x+pos[0], y+pos[1])) #draw transformed image

class PartAnimationGroup: #class for a layout group in a part animation
	def __init__(self, set_, g, dom): #create a group based on a dom
		self.g = g #store given parameters
		self.set = set_

		self.id = dom.getAttribute("id") #get id of this group
		set_.parts[self.id] = self #store ourselves
		self.pos = [int(x.strip()) for x in dom.getAttribute("pos").split(",")] #and position
		try: #load rotation
			self.rot = int(dom.getAttribute("rotation"))
		except:
			self.rot = 0
		try: #load scale
			t = float(dom.getAttribute("scale"))
		except:
			t = 1.0
		self.xscale, self.yscale = t, t
		try:
			self.xscale = float(dom.getAttribute("xscale"))
		except:
			pass
		try:
			self.yscale = float(dom.getAttribute("yscale"))
		except:
			pass
		#load children
		node = dom.firstChild
		self.children = []
		while node is not None:
			if node.localName == "group": #create new group if necessary
				self.children.append(PartAnimationGroup(set_, g, node))
			elif node.localName == "part": #or part
				self.children.append(PartAnimationPart(set_, g, node))
			node = node.nextSibling
		#calculate average center
		center = [0, 0]
		numcenters = 0
		for child in self.children:
			center[0] += child.center[0]+child.pos[0]
			center[1] += child.center[1]+child.pos[1]
			numcenters += 1
		center[0] /= numcenters
		center[1] /= numcenters
		self.center = center
	def render(self, surf, x, y, xs, ys, rot, center): #render ourselves
		pos = [(self.pos[0]-center[0]+self.center[0]), (self.pos[1]-center[1]+self.center[1])]
		npos = [0,0]
		npos[0] = ((math.cos(math.radians(-rot))*pos[0]) - (math.sin(math.radians(-rot))*pos[1]))+center[0]-self.center[0]
		npos[1] = ((math.sin(math.radians(-rot))*pos[0]) + (math.cos(math.radians(-rot))*pos[1]))+center[1]-self.center[1]
		pos = npos[:]
		for child in self.children: #render each child
			child.render(surf, x+pos[0], y+pos[1], xs*self.xscale, ys*self.yscale, rot+self.rot, self.center)

#set of part animations from one file
class PartAnimationSet:
	def __init__(self, g, anim_file):
		self.g = g #store given parameters

		images = {} #dictionary of images loaded
		self.part_images = {} #dictionary of part images defined
		self.parts = {} #dictionary of different parts defined
		self.layout = None #the part layout

		#load data from given file
		anim_dom = parse(anim_file).documentElement
		#load all given images
		for image in anim_dom.getElementsByTagName("image"):
			f = image.getAttribute("from") #get source file so we can load it
			id = image.getAttribute("id") #and image id
			surf = pygame.image.load(f) #load given image
			surf.convert_alpha() #convert it for faster rendering
			images[id] = surf #store it
		#define all the part images
		for part_image in anim_dom.getElementsByTagName("part_image"):
			image = images[part_image.getAttribute("from")] #get image used
			#get source coordinate
			coord = [int(x.strip()) for x in part_image.getAttribute("coord").split(",")]
			if part_image.getAttribute("center") == "": #if no center was defined
				surf = pygame.Surface((coord[2], coord[3]), SRCALPHA) #create a surface for the image
				surf.blit(image, (0, 0), coord) #draw image onto new surface normally
			else: #if one was defined, we need to shift the image around
				#get center coordinate
				center = [int(x.strip()) for x in part_image.getAttribute("center").split(",")]
				#calculate the difference in current center and wanted center
				center_diff = ((coord[2]/2)-center[0], (coord[3]/2)-center[1])
				#calculate new size of surface
				size = (coord[2]+abs(center_diff[0]), coord[3]+abs(center_diff[1]))
				#calculate blitting position
				pos = (max(0, center_diff[0]), max(0, center_diff[1]))
				surf = pygame.Surface(size, SRCALPHA) #create new surface
				surf.blit(image, pos, coord) #blit proper section of image
			center = (surf.get_width()/2, surf.get_height()/2) #calculate new center
			self.part_images[part_image.getAttribute("id")] = (surf, center) #store created image
		self.layout = PartAnimationGroup(self, g, anim_dom.getElementsByTagName("layout")[0]) #create layout
	def render(self, surf, x, y):
		self.layout.render(surf, x, y, 1, 1, 0, self.layout.center)
			