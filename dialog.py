import pygame #load all of pygame
from pygame.locals import *

import font #import font manager
import settings #and settings

#dialog definitions
dialogs = {"standard": {"file":"data/dialog.png", "text_rect":pygame.Rect(15,9,200,20), "font":"data/fonts/battle_font.xml"}}

#dialog we can use to draw text
class Dialog:
	def __init__(self, g, type):
		global dialogs
		self.type = type #store parameters
		self.g = g
		dlog = dialogs[type] #get attributes of dialog
		self.dlog = dlog #store it
		self.image = pygame.image.load(dlog["file"]) #load image file
		self.image.convert() #convert it so it will draw faster
		self.dlog_rect = dlog["text_rect"] #get text rect
		self.dlog_font = font.Font(dlog["font"]) #load font we're going to use for drawing
		self.waiting = False #we're not waiting for anything
		self.text = [] #list of characters to draw
	def draw_text(self, str): #draw a string
		command = None #temporary text command
		self.text = [] #clear list of characters to draw
		self.next_pos = self.dlog_rect.topleft #position for next letter to be drawn
		for chr in str: #loop through characters in given string
			if chr == "{" and command is None: #if we've encountered a command start
				command = "{" #start command
			elif chr == "}" and command is not None: #if we've encountered a command end
				command += "}" #end command
				self.text.append(command) #add it to the list of letters
				command = None #clear command
			else:
				if command is not None: #if we're in a command
					command += chr #add the current character to it
				else: #otherwise
					self.text.append(chr) #add the current character to the list of characters