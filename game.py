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
		self.camera_pos = [368, 336] #set default camera position
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
	def get_tile_type(self, tile_x, tile_y): #get the type of tile at the given position
		try: #try to get the tile
			return self.map.collision_map.tilemap[tile_y][tile_x]
		except: #if we can't
			return -1 #say so
	def update(self): #update the engine for this frame
		#center camera on player
		pos = self.objects["player"].pos #get position of payer
		self.camera_pos = (pos[0]-(settings.screen_x/2)+16, pos[1]-(settings.screen_y/2)+16)
		map_image = self.map.update() #update the map
		self.surf.fill((0, 0, 0)) #clear surface for black background
		self.surf.blit(map_image, (0, 0), pygame.Rect(self.camera_pos, \
			(settings.screen_x, settings.screen_y))) #blit it
		return self.surf #return the rendered surface