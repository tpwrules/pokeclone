import pygame #import all of pygame
from pygame.locals import *
import base64 #libraries for decoding maps
import zlib
import struct

import settings #load settings
import tileset #and tileset manager
import data

#class for a map tile layer
class MapTileLayer:
	def __init__(self, g, map, layer_node):
		self.g = g #store globals
		self.map = map
		self.tilemap = [] #all tiles on this layer
		self.image = pygame.Surface((map.map_width*16, map.map_height*16), SRCALPHA) #make a surface to draw on
		self.image.convert_alpha() #convert it to blit faster
		if layer_node.getAttribute("name") == "Collisions": #if this is the collisions layer
			self.collisions = True #mark it as such
			self.map.collision_map = self #store ourselves
		else: #if it isn't
			self.collisions = False #mark it as such
		#now, load the tilemap
		data_ = layer_node.getElementsByTagName("data")[0] #get the data element
		data = "".join([node.data for node in data_.childNodes]) #load data string
		data = zlib.decompress(base64.b64decode(data)) #decompress it
		s = struct.Struct("<"+"I"*self.map.map_width) #struct for decoding a row
		for row in xrange(self.map.map_height): #loop through all the rows
			row_data = s.unpack(data[:self.map.map_width*4]) #unpack one row of data
			data = data[self.map.map_width*4:] #delete it from the data array
			self.tilemap.append([x for x in row_data]) #add it to the tilemap, converted to a list
		self.dirty = True #mark ourselves as dirty so we render next frame
		self.anims = [] #list of tile anims
		if not self.collisions: #if we're not a collision map
			return #we can return now
		#otherwise, we have to make all the tiles start at 0
		tile_offset = None #variable to hold the tile number offset
		x, y = 0, 0
		for row in self.tilemap: #loop through tilemap
			x = 0
			for tile in row:
				if tile == 0: #if this tile is already zero
					x += 1
					continue #ignore it
				if tile_offset == None: #if we haven't found a tile offset yet
					#we need to find the tileset that belongs to this map
					prev = None #store previous tileset
					for tileset in self.map.tilesets: #loop through available tilesets
						if tile < tileset[0]: #if this tile is before this tileset
							break #stop looking
						prev = tileset #otherwise, store the current tileset
					tile_offset = prev[0]-1 #store tile offset
				self.tilemap[y][x] -= tile_offset #subtract tile offset from current tile
				x += 1
			y += 1
	#function to render the tilemap
	def render(self):
		self.dirty = False #we've been rendered
		if self.collisions: #if this is a collisions surface
			return #we don't have to worry about rendering
		i = self.image
		i.fill((0, 0, 0, 0)) #clear the image
		x, y = 0, 0 #set current position
		old_tile = None #store the previous tile
		self.tile_anims = [] #clear list of tile anims
		for row in self.tilemap: #loop through tilemap rows
			x = 0 #clear X
			for tile in row: #loop through tiles in the current row
				if tile == 0: #if the tile is a blank one
					x += 1 #go to next tile
					continue #and don't render anything
				if tile != old_tile: #if the tile isn't the same as the one before
					#we have to find the tileset that goes with this tile
					prev = None #store previously looked at tileset
					for tileset in self.map.tilesets: #loop through tilesets
						if tile < tileset[0]: #if this tile comes before this tileset
							break #stop looking
						#otherwise, store the current tileset
						prev = tileset
					old_tile = tile #update old tile
				t = ((tile-prev[0])%prev[1].tiles_x, (tile-prev[0])/prev[1].tiles_x)
				if t in prev[2]: #if this tile is animated
					self.tile_anims.append([(x*16, y*16), -1, 1, prev[2][t], prev[1]]) #append anim list
				prev[1].blit_tile(i, (x*16, y*16), tile-prev[0]) #draw tile
				x += 1 #go to next tile
			y += 1 #go to next row
	#funtion to update the current image
	def update(self, camera, surf):
		if self.collisions: return
		if self.dirty: self.render() #if we're dirty, re-render ourselves
		#render tileset animations
		for i in xrange(len(self.tile_anims)):
			self.tile_anims[i][2] -= 1 #decrement frame count
			if self.tile_anims[i][2] != 0: #if it hasn't gone to zero
				continue #go to next tile
			self.tile_anims[i][1] += 1 #if it has, update tile number
			if len(self.tile_anims[i][3]) == self.tile_anims[i][1]: #if we're at the end of the tiles
				self.tile_anims[i][1] = 0 #reset tile number
			self.tile_anims[i][2] = self.tile_anims[i][3][self.tile_anims[i][1]][1] #set time
			t = self.tile_anims[i]
			if camera.colliderect((t[0], (17, 17))): #if the camera can see this tile
				t[4].blit_tile(self.image, t[0], t[3][t[1]][0][0], t[3][t[1]][0][1]) #draw the new tile
		return self.image #just return the current image
		
#class for an object layer
class MapObjectLayer:
	def __init__(self, g, map, layer_node):
		self.g = g #store globals
		self.map = map
		self.objects = [] #list of objects on this layer
		self.map.obj_layer = self #store ourselves in the map
	def add_object(self, obj): #add an object to the render list
		self.objects.append(obj)
	def update(self, camera, surf):
		sprites = [] #list to hold sprites to draw
		for sprite in self.objects: #loop through object list
			sprite.update() #update this sprite
			if not sprite.visible: continue #if this sprite shouldn't be drawn, ignore it
			#add sprite to sprites list
			sprites.append((sprite.rect.y, sprite))
		sprites.sort() #sort the sprite list by y position
		for sprite in sprites: #loop through sprites in sprite list
			sprite[1].draw(surf) #tell sprite to draw itself

#class to manage a map
class Map:
	def __init__(self, g, map_file):
		global tileset_anims
		self.g = g #store globals
		self.map_file = map_file #and the file we were passed in
		map_dom = data.load_xml(map_file) #load and parse the map XML
		map_dom = map_dom.documentElement #get the document element of the map
		self.map_width = int(map_dom.getAttribute("width")) #load dimensions
		self.map_height = int(map_dom.getAttribute("height"))
		self.pix_width = self.map_width * 16 #calculate pixel dimensions
		self.pix_height = self.map_height * 16
		self.properties = {} #dictionary to store map properties
		self.obj_layer = None #the object layer in the map
		
		self.tilesets = [] #list of tilesets in the map
		self.layers = [] #list of layers in the map
		
		child = map_dom.firstChild #get the first child of the map so we can process them
		while child is not None: #loop through the children
			if child.localName == "tileset": #if it's a tileset
				image_tag = child.getElementsByTagName("image")[0] #get image associated with it
				image_path = image_tag.getAttribute("source") #get path of image
				image_path = image_path.replace("../", "") #fix it up
				trans = image_tag.getAttribute("trans") #get transparent color
				if trans is not "": #if one actually exists
					trans = (int(trans[:2], 16), int(trans[2:4], 16), int(trans[4:], 16)) #parse it
				else: #if it doesn't
					trans = None #set it to None
				firstgid = int(child.getAttribute("firstgid")) #get id of tileset start
				t = tileset.Tileset(image_path, 16, 16, trans) #load the tileset
				try:
					anim = tileset_anims[image_path] #attempt to get tileset animations for this image
				except:
					anim = {}
				self.tilesets.append([firstgid, t, anim]) #and save it to the list
			elif child.localName == "layer": #if it's a layer
				self.layers.append(MapTileLayer(self.g, self, child)) #process it
			elif child.localName == "objectgroup": #if it's an object layer
				self.layers.append(MapObjectLayer(self.g, self, child)) #process it
			elif child.localName == "properties": #if it's the properties list
				curr_prop = child.firstChild #get the first property
				while curr_prop is not None: #loop through properties
					if curr_prop.localName == "property": #if it's a property
						self.properties[curr_prop.getAttribute("name")] = \
							curr_prop.getAttribute("value") #load a property
					curr_prop = curr_prop.nextSibling #go to next property
			child = child.nextSibling #get the next child to process it
		self.image = pygame.Surface((self.map_width*16, self.map_height*16)) #create a new surface to render on
		self.image.convert() #convert it to blit faster
	def add_object(self, obj): #add an object to the object layer
		self.obj_layer.add_object(obj) #tell our object layer to add the object
	#function to update the map
	def update(self, camera=None):
		if camera is None:
			camera = pygame.Rect(0, 0, self.map_width*16, self.map_height*16)
		#render all the layers
		self.image.fill((0, 0, 0)) #clear out the image
		for layer in self.layers: #loop through all of our layers
			surf = layer.update(camera, self.image) #tell them to update themselves
			if surf is not None: #if a surface to draw was returned
				self.image.blit(surf, camera.topleft, camera) #draw the result
		return self.image #return updated image

def load_data(): #load tileset animation data
	global tileset_anims
	tileset_anims = {}
	dom = data.load_xml("tilesets/tileset_anim.xml").documentElement #load dom data
	for tileset in dom.getElementsByTagName("tileset"): #loop through tilesets
		anims = {}
		for cycle in tileset.getElementsByTagName("cycle"):
			anim_list = []
			node = cycle.firstChild #loop through nodes of the cycle to get tiles
			while node != None:
				if node.localName == "tile":
					#get position
					pos = tuple(int(x.strip()) for x in node.getAttribute("pos").split(","))
					anim_list.append([pos, int(node.getAttribute("time"))])
				node = node.nextSibling #go to next sibling
			anims[anim_list[0][0]] = anim_list #set animation
		tileset_anims[tileset.getAttribute("file")] = anims #set animations
	print tileset_anims