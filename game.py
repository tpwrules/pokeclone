import pygame #import all of pygame
from pygame.locals import *

import settings #load settings
import map #and map manager
import objects #and objects
import font #font manager

class Game: #class for our game engine
	def __init__(self, g):
		self.g = g #store global variables
		self.surf = pygame.Surface((settings.screen_x, settings.screen_y)) #create a new surface to display on
		self.surf.convert() #convert it to the display format for faster blitting
		self.camera_pos = [368, 336] #set default camera position
		self.objects = {} #list of objects on the map
		self.warps = {} #list of warps on the map
		self.warping = 0 #set when we need to do a warp
		self.warp_obj = None #warp object
		self.overlay_color = None
		self.dialog = pygame.image.load("data/dialog.png")
		self.dialog.convert()
		self.font = font.Font("data/fonts/battle_font.xml")
	def start(self):
		self.map = map.Map(self.g, "data/maps/oasis.tmx") #load map
		self.warping = 2
	def add_object(self, obj_node): #add an object
		properties = {} #dictionary of the object's properties
		for property in obj_node.getElementsByTagName("property"): #get properties
			properties[property.getAttribute("name")] = property.getAttribute("value") #get a property
		type = obj_node.getAttribute("type") #get type of object
		obj = objects.obj_types[type](self, obj_node, properties) #load the object
		self.objects[properties["id"]] = obj #store it
		return obj #and return it
	def add_warp(self, pos, obj): #add a warp object
		self.warps[pos] = obj #store the warp
	def prepare_warp(self, pos): #prepare a warp
		self.warping = True #we're about to warp
		self.warp_obj = self.warps[pos] #get the warp object
	def perform_warp(self): #actually warp
		warp_obj = self.warp_obj #get the warp objectx
		self.objects = {} #destroy map objects
		self.warps = {}
		self.map = None
		self.warping = 2 #we're in warp stage 2
		self.warp_obj = False
		map_file = "data/maps/"+warp_obj["dest_map"] #get destination of warp
		self.map = map.Map(self.g, map_file) #load the map
		new_warp = self.objects[warp_obj["dest_warp"]] #get the warp destination
		player = self.objects["player"] #get the player object
		new_pos = new_warp.properties["tile_pos"].split(",") #calculate warp destination
		new_pos = (int(new_pos[0].strip()), int(new_pos[1].strip()))
		player.tile_pos = new_pos #set player position
		player.pos = [((player.tile_pos[0]-1)*16)+8, (player.tile_pos[1]-1)*16]
		player.rect = pygame.Rect(player.pos, player.size)
		self.overlay_color = None
	def get_tile_type(self, tile_x, tile_y): #get the type of tile at the given position
		if tile_y < 0 or tile_x < 0: #if the tile is negative
			return -1 #it shouldn't exist
		try: #try to get the tile
			return self.map.collision_map.tilemap[tile_y][tile_x]
		except: #if we can't
			return -1 #say so
	def update(self): #update the engine for this frame
		if self.warping == 1: #if we should warp
			if self.overlay_color is None: #if we just started
				self.overlay_color = [255, 0 ,0, 0] #start color
			else:
				self.overlay_color[0] -= 32 #decrement color
			self.overlay_color = [self.overlay_color[0]]*3
			if self.overlay_color[0] <= 0: #if we're at full black
				self.perform_warp() #do the warp
		if self.warping == 2: #if we're fading back in
			if self.overlay_color is None: #if we just started
				self.overlay_color = [0, 0 ,0, 0] #start color
			else:
				self.overlay_color[0] += 32 #increment color
			self.overlay_color = [self.overlay_color[0]]*3
			if self.overlay_color[0] > 255: #if we're at max brightness
				self.overlay_color = None #stop fading
				self.warping = 0
		#center camera on player
		pos = self.objects["player"].pos #get position of payer
		self.camera_pos = (pos[0]-(settings.screen_x/2)+16, pos[1]-(settings.screen_y/2)+16)
		if self.warping != 1:
			self.map_image = self.map.update() #update the map
		self.surf.fill((0, 0, 0)) #clear surface for black background
		self.surf.blit(self.map_image, (0, 0), pygame.Rect(self.camera_pos, \
			(settings.screen_x, settings.screen_y))) #blit it
		if self.overlay_color is not None: #if there's a color to render over the surface
			self.surf.fill(self.overlay_color, special_flags=BLEND_RGB_MULT) #do so
		if self.g.keys[settings.key_accept]:
			self.surf.blit(self.dialog, (1, 1)) #draw dialog box
			y = 9
			s = ""
			for chr in self.font.letters:
				if len(chr) > 1 or chr == "{":
					s += ("{"+chr+"}")
				else:
					s += chr
				if self.font.get_width(s) > 200:
					self.font.render(s, self.surf, (15,y))
					y += 10
					s = ""
			self.font.render(s, self.surf, (15, y))
		self.font.render(str(self.g.clock.get_fps()).split(".")[0], self.surf, (0, 180)) #draw framerate
		return self.surf #return the rendered surface