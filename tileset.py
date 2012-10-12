import pygame #import all of pygame
from pygame.locals import *

import data

#class for managing a tileset
class Tileset:
    #initialize the tileset
    def __init__(self, image, tile_width, tile_height, trans=None):
        self.image = data.load_image(image) #load the image provided
        if trans is not None: #if there is a transparent pixel color
            self.image.set_alpha(None) #remove any alpha if it's there
            self.image.set_colorkey(trans) #set it as the color key
            self.image.convert() #convert it to display format for faster blitting
        else:
            self.image.convert_alpha()
        self.tile_width = tile_width #save attributes
        self.tile_height = tile_height
        self.tiles_x = self.image.get_width()/tile_width #store number of tiles
        self.tiles_y = self.image.get_height()/tile_height
    #function to get a specific tile
    def get_tile(self, x, y=None, dest=None):
        if dest is None: #if no destination surface was specified
            dest = pygame.Surface((self.tile_width, self.tile_height), SRCALPHA) #create a new one
            dest.convert_alpha() #and convert it for faster drawing
        dest.blit(self.image, (0, 0), self.get_tile_rect(x, y)) #draw the specified tile to the destination
        return dest #and return it
    #function to blit a specific tile
    def blit_tile(self, dest, dest_pos, x, y=None):
        #blit the tile
        dest.blit(self.image, dest_pos, self.get_tile_rect(x, y))
    #function to get a rect for a specific tile
    def get_tile_rect(self, x, y=None):
        if y is None: #if a y value was not specified
            y = x/self.tiles_x #calculate it
            x = x-(y*self.tiles_x) #and update x properly
        return (x*self.tile_width, y*self.tile_height, self.tile_width, self.tile_height) #generate and return rect