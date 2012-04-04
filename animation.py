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
			self.rot = float(dom.getAttribute("rotation"))
		except:
			self.rot = 0.0
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
		#back up loaded data
		self.orig_pos = self.pos
		self.orig_rot = self.rot
		self.orig_xscale = self.xscale
		self.orig_yscale = self.yscale
		self.image = set_.part_images[dom.getAttribute("from")][0] #load our image
		self.orig_image = self.image
		self.center = set_.part_images[dom.getAttribute("from")][1] #and store center
		self.orig_center = self.center
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
	def reset(self): #reset our state
		self.pos = self.orig_pos
		self.rot = self.orig_rot
		self.xscale = self.orig_xscale
		self.yscale = self.orig_yscale
		self.image = self.orig_image
		self.center = self.orig_center

class PartAnimationGroup: #class for a layout group in a part animation
	def __init__(self, set_, g, dom): #create a group based on a dom
		self.g = g #store given parameters
		self.set = set_

		self.id = dom.getAttribute("id") #get id of this group
		set_.parts[self.id] = self #store ourselves
		self.pos = [int(x.strip()) for x in dom.getAttribute("pos").split(",")] #and position
		try: #load rotation
			self.rot = float(dom.getAttribute("rotation"))
		except:
			self.rot = 0.0
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
		#back up loaded data
		self.orig_pos = self.pos
		self.orig_rot = self.rot
		self.orig_xscale = self.xscale
		self.orig_yscale = self.yscale
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
	def reset(self): #reset our state
		self.pos = self.orig_pos
		self.rot = self.orig_rot
		self.xscale = self.orig_xscale
		self.yscale = self.orig_yscale
		#reset state of all our children
		for child in self.children:
			child.reset()

class PartAnimation: #class for one animation
	def __init__(self, set_, dom): #initialize ourselves
		self.set = set_ #store given parameters

		self.frame_list = [] #list of frames in this animation
		self.wait = 0 #wait until next frame
		self.curr_frame = 0 #index of current frame
		self.tweens = [] #list of different tweens to do this frame

		self.loopreset = dom.getAttribute("loopreset") != ""

		curr_frame = dom.firstChild #load frames
		while curr_frame is not None:
			if curr_frame.localName == "frame": #if this is a frame
				delay = int(curr_frame.getAttribute("time")) #load delay
				cmds = [] #load command list
				curr_cmd = curr_frame.firstChild
				while curr_cmd is not None:
					if curr_cmd.localName == "rotate": #if this is a rotate command
						#add it to command list
						cmds.append([1, curr_cmd.getAttribute("id"), int(curr_cmd.getAttribute("degrees"))])
					elif curr_cmd.localName == "move": #if it's a move command
						#get delta
						delta = [int(x.strip()) for x in curr_cmd.getAttribute("delta").split(",")]
						cmds.append([2, curr_cmd.getAttribute("id"), delta])
					elif curr_cmd.localName == "set": #if it's a set command
						#add to command list
						cmds.append([3, curr_cmd.getAttribute("id"), curr_cmd.getAttribute("to")])
					curr_cmd = curr_cmd.nextSibling #go to next command
				self.frame_list.append([delay, cmds]) #add loaded data
			curr_frame = curr_frame.nextSibling #go to next frame
	def start(self): #start animation running
		self.curr_frame = -1 #reset variables
		self.wait = 0
		self.tweens = []
		self.update() #update once
	def _process_frame(self, frame): #process tweens for a frame
		self.tweens = [] #clear tween list
		self.wait = frame[0] #initialize proper wait
		for cmd in frame[1]: #loop through each command
			part_id = cmd[1] #get id of specified part
			if cmd[0] == 1: #if it's a rotation command
				#calculate step for each frame
				step = (cmd[2]*1.0)/self.wait
				self.tweens.append([cmd[0], cmd[1], step, cmd[2]+self.set.parts[part_id].rot]) #add it to list
			elif cmd[0] == 2: #if this is a movement command
				t = [float(x) for x in self.set.parts[part_id].pos] #store current position
				step = [cmd[2][0]/self.wait, cmd[2][1]/self.wait] #calculate step
				#calculate final position
				final = [cmd[2][0]+int(t[0]), cmd[2][1]+int(t[1])]
				self.tweens.append([2, cmd[1], step, t, final])
			elif cmd[0] == 3: #if this is a set command
				img = self.set.part_images[cmd[2]] #load new image
				self.set.parts[cmd[1]].image = img[0] #set data
				self.set.parts[cmd[1]].center = img[1]
	def _update_tween(self, tween): #update a tween
		if tween[0] == 1: #if it's a rotation tween
			self.set.parts[tween[1]].rot += tween[2] #update rotation
		elif tween[0] == 2: #if this is a movement tween
			tween[3][0] += tween[2][0] #update stored position
			tween[3][1] += tween[2][1]
			pos = [int(x) for x in tween[3]] #convert to integer
			self.set.parts[tween[1]].pos = pos #store position in object
	def _finish_tween(self, tween): #finish up a tween command
		if tween[0] == 1: #if it's a rotation tween
			self.set.parts[tween[1]].rot = tween[3] #set end position
		elif tween[0] == 2: #if this is a movement tween
			self.set.parts[tween[1]].pos = tween[4][:] #set final position
	def update(self): #update animation
		if self.wait == 0: #if this is the end of this frame
			for tween in self.tweens: #go through tweens
				self._finish_tween(tween) #finish each one
			self.curr_frame += 1 #go to next frames
			if self.curr_frame == len(self.frame_list): #if we're off the end of the list
				self.curr_frame = 0 #go back to first one
				#reset layout if requested
				if self.loopreset: self.set.layout.reset()
			self._process_frame(self.frame_list[self.curr_frame]) #process data for next frame
		for tween in self.tweens: #go through tweens
			self._update_tween(tween) #update each of them
		self.wait -= 1 #one frame has passed		

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
		self.curr_animation = None #clear list of animations
		self.animations = {}
		for anim in anim_dom.getElementsByTagName("anim"): #load list of animations
			#initialize and store an animation
			self.animations[anim.getAttribute("id")] = PartAnimation(self, anim)
	def set_animation(self, anim): #start a specific animation
		self.layout.reset() #reset position of everything
		self.curr_animation = self.animations[anim] #set animation
		self.curr_animation.start() #start animation running
	def update(self, surf, x, y):
		if self.curr_animation is not None: #if there's a current animation
			self.curr_animation.update() #update current animation
		#render out layout
		self.layout.render(surf, x, y, 1, 1, 0, self.layout.center)
			