from OpenGL.GL import *
from OpenGL.GLU import *

import pygame #import all of pygame
from pygame.locals import *
import math #import math library for part animation calculation

import data

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
		try:
			self.show = int(dom.getAttribute("show")) != 0
		except:
			self.show = True
		#back up loaded data
		self.orig_pos = self.pos[:]
		self.orig_rot = self.rot
		self.orig_xscale = self.xscale
		self.orig_yscale = self.yscale
		self.image = set_.part_images[dom.getAttribute("from")][0] #load our image
		self.orig_image = self.image
		self.center = set_.part_images[dom.getAttribute("from")][1] #and store center
		self.orig_center = self.center
		self.offset = set_.part_images[dom.getAttribute("from")][2] #and move offset
		self.orig_offset = self.offset[:]
		self.size = set_.part_images[dom.getAttribute("from")][3]
		self.orig_size = self.size
		self.orig_show = self.show
	def render(self): #render ourselves
		if not self.show: return #return if we're not being shown
		glBindTexture(GL_TEXTURE_2D, self.image)

		glTranslatef(self.pos[0]+self.center[0]-self.offset[0], self.pos[1]+self.center[1]-self.offset[1], 0)
		glScalef(self.xscale, self.yscale, 1)
		glRotatef(self.rot, 0, 0, 1)
		glTranslatef(-self.center[0], -self.center[1], 0)

		glBegin(GL_QUADS)
		glTexCoord2f(0.0, 0.0)
		glVertex2f(0, self.size[1])
		glTexCoord2f(1.0, 0.0)
		glVertex2f(self.size[0], self.size[1])
		glTexCoord2f(1.0, 1.0)
		glVertex2f(self.size[0], 0)
		glTexCoord2f(0.0, 1.0)
		glVertex2f(0, 0)
		glEnd()
	def reset(self): #reset our state
		self.pos = self.orig_pos[:]
		self.rot = self.orig_rot
		self.xscale = self.orig_xscale
		self.yscale = self.orig_yscale
		self.image = self.orig_image
		self.center = self.orig_center
		self.offset = self.orig_offset[:]
		self.show = self.orig_show
		self.size = self.orig_size

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
		try:
			self.show = int(dom.getAttribute("show")) != 0
		except:
			self.show = True
		#back up loaded data
		self.orig_pos = self.pos[:]
		self.orig_rot = self.rot
		self.orig_xscale = self.xscale
		self.orig_yscale = self.yscale
		self.orig_show = self.show
		#load children
		node = dom.firstChild
		self.children = []
		while node is not None:
			if node.localName == "group": #create new group if necessary
				self.children.append(PartAnimationGroup(set_, g, node))
			elif node.localName == "part": #or part
				self.children.append(PartAnimationPart(set_, g, node))
			node = node.nextSibling
		if dom.getAttribute("center") == "": #if no center is defined
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
		else:
			#load the center
			self.center = [int(x.strip()) for x in dom.getAttribute("center").split(",")]
	def render(self): #render ourselves
		if not self.show: return #return if we're not being shown
		glTranslatef(self.pos[0]+self.center[0], self.pos[1]+self.center[1], 0)
		glScalef(self.xscale, self.yscale, 1)
		glRotatef(self.rot, 0, 0, 1)
		glTranslatef(-self.center[0], -self.center[1], 0)
		for child in self.children:
			glPushMatrix()
			child.render()
			glPopMatrix()
	def reset(self): #reset our state
		self.pos = self.orig_pos[:]
		self.rot = self.orig_rot
		self.xscale = self.orig_xscale
		self.yscale = self.orig_yscale
		self.show = self.orig_show
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
						delta = [float(x.strip()) for x in curr_cmd.getAttribute("delta").split(",")]
						cmds.append([2, curr_cmd.getAttribute("id"), delta])
					elif curr_cmd.localName == "set": #if it's a set command
						#add to command list
						cmds.append([3, curr_cmd.getAttribute("id"), curr_cmd.getAttribute("to")])
					elif curr_cmd.localName == "scale": #if it's a scale command
						x, y = None, None #initialize scale values
						try: #load scale
							x = float(curr_cmd.getAttribute("scale"))
						except:
							pass
						y = x
						try:
							x = float(curr_cmd.getAttribute("xscale"))
						except:
							pass
						try:
							y = float(curr_cmd.getAttribute("yscale"))
						except:
							pass
						if x != None: #if there was an xscale
							#add it to list
							cmds.append([4, curr_cmd.getAttribute("id"), x])
						if y != None: #if there was a yscale
							#add it to list
							cmds.append([5, curr_cmd.getAttribute("id"), x])
					elif curr_cmd.localName == "show": #if it's a show command
						try:
							show = int(curr_cmd.getAttribute("show")) != 0 #attempt to mark false
						except:
							show = True #default is true
						cmds.append([6, curr_cmd.getAttribute("id"), show]) #add command to list
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
				self.set.parts[cmd[1]].offset = img[2]
				self.set.parts[cmd[1]].size = img[3]
			elif cmd[0] == 4: #if this is an xscale command
				#calculate step
				step = (cmd[2]-self.set.parts[cmd[1]].xscale)/self.wait
				self.tweens.append([4, cmd[1], step, cmd[2]]) #add to list
			elif cmd[0] == 5: #yscale command
				#calculate step
				step = (cmd[2]-self.set.parts[cmd[1]].yscale)/self.wait
				self.tweens.append([5, cmd[1], step, cmd[2]]) #add to list
			elif cmd[0] == 6: #if it's a show command
				self.set.parts[cmd[1]].show = cmd[2] #set show
	def _update_tween(self, tween): #update a tween
		if tween[0] == 1: #if it's a rotation tween
			self.set.parts[tween[1]].rot += tween[2] #update rotation
		elif tween[0] == 2: #if this is a movement tween
			tween[3][0] += tween[2][0] #update stored position
			tween[3][1] += tween[2][1]
			pos = [int(x) for x in tween[3]] #convert to integer
			self.set.parts[tween[1]].pos = pos #store position in object
		elif tween[0] == 4: #if this is an xscale command
			self.set.parts[tween[1]].xscale += tween[2] #update scale
		elif tween[0] == 5: #yscale command
			self.set.parts[tween[1]].yscale += tween[2] #update scale
	def _finish_tween(self, tween): #finish up a tween command
		if tween[0] == 1: #if it's a rotation tween
			self.set.parts[tween[1]].rot = tween[3] #set end position
		elif tween[0] == 2: #if this is a movement tween
			self.set.parts[tween[1]].pos = tween[4][:] #set final position
		elif tween[0] == 4: #xscale command
			self.set.parts[tween[1]].xscale = tween[3] #set final scale
		elif tween[0] == 5: #yscale command
			self.set.parts[tween[1]].yscale = tween[3] #set final scale
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

		texnum = 0

		#load data from given file
		anim_dom = data.load_xml(anim_file).documentElement
		#load all given images
		for image in anim_dom.getElementsByTagName("image"):
			f = image.getAttribute("from") #get source file so we can load it
			id = image.getAttribute("id") #and image id
			surf = data.load_image(f) #load given image
			surf.convert_alpha() #convert it for faster rendering
			images[id] = surf #store it
		#define all the part images
		for part_image in anim_dom.getElementsByTagName("part_image"):
			image = images[part_image.getAttribute("from")] #get image used
			#get source coordinate
			coord = [int(x.strip()) for x in part_image.getAttribute("coord").split(",")]
			surf = pygame.Surface((coord[2], coord[3]), SRCALPHA)
			surf.blit(image, (0, 0), coord)
			surfdata = pygame.image.tostring(surf, "RGBA", True)
			glBindTexture(GL_TEXTURE_2D, texnum)
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, coord[2], coord[3], 0, GL_RGBA, GL_UNSIGNED_BYTE, surfdata)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
			if part_image.getAttribute("origin") != "": #if an origin was defined
				#get origin coord
				origin = [int(x.strip()) for x in part_image.getAttribute("origin").split(",")]
			else:
				origin = [0, 0]
			center = (surf.get_width()/2, surf.get_height()/2) #calculate new center
			self.part_images[part_image.getAttribute("id")] = (texnum, center, origin, (coord[2], coord[3])) #store created image
			texnum += 1
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
	def update(self):
		if self.curr_animation is not None: #if there's a current animation
			self.curr_animation.update() #update current animation
	def render(self, x, y):
		#render out layout
		glPopMatrix()
		glPushMatrix()
		glTranslatef(x, y, 0)
		self.layout.render()
		glPopMatrix()
		glPushMatrix()
			