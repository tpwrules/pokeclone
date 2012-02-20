import pygame #import all of pygame
from pygame.locals import *

import settings #load settings
import map #and map manager
import objects #and objects

class Game: #class for our game engine
	def __init__(self, g):
		self.g = g #store global variables
		self.surf = pygame.Surface((settings.screen_x, settings.screen_y)) #create a new surface to display on
		self.surf.convert() #convert it to the display format for faster blitting
		self.camera_pos = [0, 0] #set default camera position
		self.objects = {} #list of objects on the map
	def start(self):
		self.map = map.Map(self.g, "data/maps/oasis.tmx") #load map
	def add_object(self, obj_node): #add an object
		properties = {} #dictionary of the object's properties
		for property in obj_node.getElementsByTagName("property"): #get properties
			properties[property.getAttribute("name")] = property.getAttribute("value") #get a property
		type = obj_node.getAttribute("type") #get type of object
		obj = objects.obj_types[type](self, obj_node, properties) #load the object
		self.objects[properties["id"]] = obj #store it
		return obj #and return it
	def update(self): #update the engine for this frame
		#allow user to control camera
		if self.g.keys[settings.key_up]: #if up is pressed
			self.camera_pos[1] -= 1 #move up
		elif self.g.keys[settings.key_down]: #if down is pressed
			self.camera_pos[1] += 1 #move down
		if self.g.keys[settings.key_left]: #if left is pressed
			self.camera_pos[0] -= 1 #move left
		elif self.g.keys[settings.key_right]: #if right is pressed
			self.camera_pos[0] += 1 #move right
		map_image = self.map.update() #update the map
		self.surf.fill((0, 0, 0)) #clear surface for black background
		self.surf.blit(map_image, (0, 0), pygame.Rect(self.camera_pos, \
			(settings.screen_x, settings.screen_y))) #blit it
		return self.surf #return the rendered surface