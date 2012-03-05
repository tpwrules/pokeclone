import pygame #load all of pygame
from pygame.locals import *

import font #import font manager
import settings #and settings

#dialog definitions
dialogs = {"standard": {"file":"data/dialog.png", "text_rect":pygame.Rect(11,8,232,32), "font":"data/fonts/battle_font.xml"},\
"notify": {"file":"data/selfdialog.png", "text_rect":pygame.Rect(8,8,240,32), "font":"data/fonts/battle_font.xml"}}

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
		self.waiting = False #whether we're waiting for the player ot press action
		self.text = [] #list of characters to draw
		self.text_surf = pygame.Surface(self.dlog_rect.size) #create a surface to draw text on
		self.text_surf.set_colorkey((127, 182, 203)	) #set a colorkey for it
		self.text_surf.fill((127, 182, 203)) #fill it with the colorkey value
		self.text_surf.convert() #convert it to blit faster
		self.drawing = False #whether we're currently drawing the dialog box
	def draw_text(self, str): #draw a string
		if str == "": #if it's an empty string
			self.drawing = False #stop drawing
			return #don't render it
		command = None #temporary text command
		self.text = [] #clear list of characters to draw
		self.next_pos = [0, 0] #position for next letter to be drawn
		for char in str: #loop through characters in given string
			if char == "{" and command is None: #if we've encountered a command start
				command = "{" #start command
			elif char == "}" and command is not None: #if we've encountered a command end
				command += "}" #end command
				self.text.insert(0, command) #add it to the list of letters
				command = None #clear command
			else:
				if command is not None: #if we're in a command
					command += char #add the current character to it
				else: #otherwise
					self.text.insert(0, char) #add the current character to the list of characters
		self.text_surf.fill((127, 182, 203)) #clear the text surface
		self.drawing = True #and we're currently drawing!
	def _next_line(self): #go to the next line
		self.next_pos[1] += self.dlog_font.height #increment height
		if self.next_pos[1] >= (self.dlog_rect.height-self.dlog_font.height): #if we're past the drawing edge
			self.next_pos[1] -= self.dlog_font.height #subtract height
			self.text_surf.scroll(0, -self.dlog_font.height) #scroll the text surface
			#clear out new line
			self.text_surf.fill((127, 182, 203), ((0, self.next_pos[1]), self.dlog_rect.size))
		self.next_pos[0] = 0 #clear x coord
	def _next_char(self): #draw the next character
		if not self.drawing: #if we're not drawing anything
			return True #say so
		#if we're waiting for the accept key to be pressed and it hasn't yet
		if self.waiting and not self.g.curr_keys[settings.key_accept]:
			return #don't do anything
		self.waiting = False #if we've ended up here, we're not waiting any more
		if len(self.text) == 0: #if we don't have any more characters to draw
			self.drawing = False #we're not drawing any more
			return True #we've finished drawing
		letter = self.text.pop() #get a letter
		#test for special commands
		if letter == "{br}": #if we've hit a line break command
			self._next_line() #go to next line
		elif letter == "{wait}": #if we've hit a wait command
			self.waiting = True #mark that we're waiting
		elif letter == "{clear}": #if we've hit a clear screen command
			self.next_pos = [0, 0] #reset next position
			self.text_surf.fill((127, 182, 203)) #clear text
		else: #if we've hit anything else
			width = self.dlog_font.get_width(letter) #get the letter's width
			if self.next_pos[0]+width >= self.dlog_rect.width: #if we've exceeded width
				self._next_line() #go to next line
			self.dlog_font.render(letter, self.text_surf, self.next_pos) #render letter
			self.next_pos[0] += width #add width to current position
	def update(self, surf, surf_pos): #update the dialog box, returns true when done
		if not self.drawing: #if we're not drawing anything
			return True #say so
		r = self._next_char() #draw one character
		r = r or self._next_char() #and another
		if r == True: #if we've finished drawing
			return True #say so
		#draw the current dialog box
		surf.blit(self.image, surf_pos) #draw dialog box image
		surf.blit(self.text_surf, (surf_pos[0]+self.dlog_rect.left, surf_pos[1]+self.dlog_rect.top)) #and text surface