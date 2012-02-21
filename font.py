import pygame #import all of pygame
from pygame.locals import *
from xml.dom.minidom import parse #import XML parser for loading animations

import settings #load settings

#class for managing a font
class Font:
	def __init__(self, file):
		self.letters = {} #dictionary of letters
		
		font_dom = parse(file).documentElement #load and parse font
		image_file = font_dom.getAttribute("image") #get font bitmap file name
		self.image = pygame.image.load(image_file) #load font bitmap
		self.image.convert_alpha() #convert it to draw faster
		self.height = int(font_dom.getAttribute("height")) #get height of characters
		self.id = font_dom.getAttribute("id") #get font ID
		
		#load all the letters
		for letter in font_dom.getElementsByTagName("letter"):
			name = letter.getAttribute("name") #get name of letter
			width = int(letter.getAttribute("size")) #get width of letter
			coords = letter.getAttribute("coord").split(",") #get coordinate of letter
			#make a rect of the letter bitmap
			rect = pygame.Rect(int(coords[0].strip()), int(coords[1].strip()), \
				width, self.height)
			self.letters[name] = rect #store the letter
	#build a list of letter rects from a string
	def get_letters(self, str):
		letter_rects = []
		code = None
		for letter in str: #loop through all the letters in the string
			if letter == "{" and code is None: #if it's the start of a code
				code = "" #clear out the code
				continue #go to next letter
			if letter == "}" and code is not None: #if it's the end of a code
				letter_rects.append(self.letters[code]) #save rect
				code = None #clear code
				continue #go to next letter
			if code is not None: #if we're in a code
				code += letter #add a letter to the code
			else: #if we're not
				letter_rects.append(self.letters[letter]) #add the letter rect
		return letter_rects #return result
	#get the width of a string
	def get_width(self, str):
		rects = self.get_letters(str) #get the list of rectangles
		total = 0 #total width
		for letter in rects: #loop through all the rects
			total += letter.width #add the widths together
		return total #return the total width
	#render a string
	def render(self, str, dest, where):
		rects = self.get_letters(str) #get the letter rects
		x = 0 #current X position
		for letter in rects: #loop through them
			#render a letter
			dest.blit(self.image, (where[0]+x, where[1]), letter)
			x += letter.width #go to the position of the next letter
		return x #return the width of the rendered string