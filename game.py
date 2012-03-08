import pygame #import all of pygame
from pygame.locals import *
from xml.dom.minidom import parse #import xml parser

import settings #load settings
import map #and map manager
import objects #and objects
import font #font manager
import player #class for player
import dialog #class for dialogs

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
		self.obj2pos = {} #dictionary of objects mapped to positions
		self.pos2obj = {} #dictionary of positions mapped to objects
		self.overlay_color = None
		self.default_dialog = dialog.Dialog(self.g, "standard")
		self.dialog = None
		self.font = self.default_dialog.dlog_font
		self.dialog_drawing = False #set when the dialog is showing text
		self.dialog_result = None #hold result of a dialog
		self.dialog_callback = None #callback for dialog completion
		self.object_data = {} #dictionary of loaded object data
		self.debug = False #whether we're in debug mode or not
	def start(self):
		self.player = player.Player(self) #initialize a player object
		self.load_map("data/maps/oasis.tmx") #load map
		self.warping = 2
	def load_map(self, map_file): #load a map
		self.map = map.Map(self.g, map_file) #load the map
		objects_dom = parse(self.map.properties["object_data"]).documentElement #parse object data file
		self.object_data = {} #clear previous object data
		child = objects_dom.firstChild #get first object data element
		while child is not None: #loop through object data
			if child.localName == "object": #if it's an object element
				self.object_data[child.getAttribute("id")] = child #store it under its id
			child = child.nextSibling #go to next element
	def add_object(self, obj_node): #add an object
		properties = {} #dictionary of the object's properties
		for property in obj_node.getElementsByTagName("property"): #get properties
			properties[property.getAttribute("name")] = property.getAttribute("value") #get a property
		type = obj_node.getAttribute("type") #get type of object
		if type == "Player": #if we're trying to load a player object
			obj = self.player #return it
		else: #otherwise
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
		self.obj2pos = {}
		self.pos2obj = {}
		self.dialog_drawing = False #we aren't drawing a dialog
		map_file = "data/maps/"+warp_obj["dest_map"] #get destination of warp
		self.load_map(map_file) #load the map
		new_warp = self.objects[warp_obj["dest_warp"]] #get the warp destination
		player = self.objects["player"] #get the player object
		new_pos = new_warp.properties["tile_pos"].split(",") #calculate warp destination
		new_pos = (int(new_pos[0].strip()), int(new_pos[1].strip()))
		player.tile_pos = new_pos #set player position
		player.pos = [((player.tile_pos[0]-1)*16)+8, (player.tile_pos[1]-1)*16]
		player.rect = pygame.Rect(player.pos, player.size)
		self.overlay_color = None
	def get_tile_type(self, tile_x, tile_y, player_req=False): #get the type of tile at the given position
		if tile_y < 0 or tile_x < 0: #if the tile is negative
			return -1 #it shouldn't exist
		try: #test if there's an object in the given position
			t = self.pos2obj[(tile_x, tile_y)] #get object
			if t != self.player or not player_req: #if it's not a player or not a player is requesting it
				return -1 #say so
		except: #if there wasn't an object
			pass #don't do anything
		try: #try to get the tile
			return self.map.collision_map.tilemap[tile_y][tile_x]
		except: #if we can't
			return -1 #say so
	def collide(self, tile_pos): #test for a collision
		type = self.get_tile_type(tile_pos[0], tile_pos[1]) #get tile type
		if type != settings.TILE_NORMAL: #if it's not a normal tile
			return True #this is a collison
		return False #otherwise, we're fine
	def set_obj_pos(self, obj, pos): #set an object's position
		pos = tuple(pos[:]) #convert position to tuple
		if obj in self.obj2pos: #if the object has a postion associated with it
			del self.pos2obj[self.obj2pos[obj]] #remove it from the position dict
			del self.obj2pos[obj] #and the object dict
		self.obj2pos[obj] = pos #set object -> position mapping
		self.pos2obj[pos] = obj #set position -> object mapping
	def show_dlog(self, str, talker=None, dlog=None, callback=None): #draw a dialog
		self.dialog_drawing = True #set that we're drawing one
		if dlog is not None: #if a specific dialog has been specified
			self.dialog = dlog #set it
		else: #otherwise, if none was given
			self.dialog = self.default_dialog #use the default one
		self.dialog.draw_text(str) #and tell it to draw
		self.dialog_talking = talker #store who's talking
		self.dialog_callback = callback #store callback
		self.dialog_result = None #clear result
	def interact(self, pos, direction): #interact with an object
		if pos in self.pos2obj: #if this position has an object
			self.pos2obj[pos].interact(direction) #tell the object to interact
	def update(self): #update the engine for this frame
		if self.warping == 1: #if we should warp
			if self.overlay_color is None: #if we just started
				self.overlay_color = [255, 0, 0, 0] #start color
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
		if self.g.curr_keys[settings.key_debug]: #if the debug key is pressed
			self.debug = not self.debug #invert debug flag
		#center camera on player
		pos = self.objects["player"].pos #get position of player
		self.camera_pos = (pos[0]-(settings.screen_x/2)+16, pos[1]-(settings.screen_y/2)+16)
		if self.warping != 1:
			self.map_image = self.map.update() #update the map
		self.surf.fill((0, 0, 0)) #clear surface for black background
		if self.debug: #if we're in debug mode
			for pos in self.pos2obj: #draw object collision tiles
				self.map_image.fill((255, 0, 0), rect=pygame.Rect(((pos[0]*16, pos[1]*16), (16, 16))), special_flags=BLEND_RGB_MULT)
		self.surf.blit(self.map_image, (0, 0), pygame.Rect(self.camera_pos, \
			(settings.screen_x, settings.screen_y))) #blit it
		if self.overlay_color is not None: #if there's a color to render over the surface
			self.surf.fill(self.overlay_color, special_flags=BLEND_RGB_MULT) #do so
		if self.dialog_drawing: #if we're drawing a dialog
			result = self.dialog.update(self.surf, (0, 1)) #draw it
			if result is not None: #if we're finished
				self.dialog_drawing = False #stop drawing
				self.dialog_result = result #store result
				if self.dialog_callback: #if there's a callback
					self.dialog_callback(result) #call it with result
			elif self.dialog_talking != None: #if somebody is talking
				#draw an arrow to them
				pos = self.dialog_talking.pos
				pos = (pos[0]-self.camera_pos[0]+12, pos[1]-self.camera_pos[1]+8)
				pygame.draw.polygon(self.surf, (255, 255, 255), [[35, 46], pos, [65, 46]])
		self.font.render(str(self.g.clock.get_fps()).split(".")[0], self.surf, (0, 180)) #draw framerate
		return self.surf #return the rendered surface