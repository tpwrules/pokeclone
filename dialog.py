import pygame #load all of pygame
from pygame.locals import *

import font #import font manager
import settings #and settings
import tileset #import tileset manager

#dialog definitions
dialogs = {"standard": {"file":"data/dialog.png", "choice_file":"data/dialog_choice_tiles.png", "text_rect":pygame.Rect(11,8,232,32), "font":"data/fonts/battle_font.xml"},\
"notify": {"file":"data/selfdialog.png", "choice_file":"data/self_dialog_choice_tiles.png", "text_rect":pygame.Rect(8,8,240,32), "font":"data/fonts/battle_font.xml"}}

#dialog we can use to ask a choice
class ChoiceDialog:
	def __init__(self, g, type, dlog=None):
		self.g = g #store parameters
		if dlog is not None: #if a dialog has been provided
			#copy its parameters
			self.type = dlog.type
			self.choice_tiles = dlog.choice_tiles
			self.dlog_font = dlog.dlog_font
			self.dlog = dialogs[self.type]
		else: #otherwise, if none was given
			dlog = dialogs[type] #get type
			self.choice_tiles = tileset.Tileset(dlog["choice_file"], 8, 8) #load choice tileset
			self.dlog_font = font.Font(dlog["font"]) #load font
			self.dlog = dlog
			self.type = type
		self.choices = [] #list of choices
		self.drawing = False #whether we're currently showing choices
		self.curr_choice = None #index of the currently selected choice
		self.cursor_tile = pygame.Surface((8, 8), SRCALPHA) #surface to hold cursor tile
	def show_choices(self, choices): #draw a list of choices
		dlog_width = -1 #maximum choice width
		#calculate width of dialog box
		for choice in choices: #loop through choices provided:
			width = self.dlog_font.get_width(choice)+10 #get its width
			if width > dlog_width: #if it's greater than the current maximum
				dlog_width = width #update maximum
		dlog_height = 16 + (self.dlog_font.height*len(choices)) #calculate height of dialog
		dlog_width += 16 #add border size to width
		#turn height and width into multiples of eight
		if dlog_height % 8 > 0: dlog_height += (8-(dlog_height%8))
		if dlog_width % 8 > 0: dlog_width += (8-(dlog_width%8))
		self.dlog_height = dlog_height #store dimensions
		self.dlog_width = dlog_width
		self.dlog_surf = pygame.Surface((dlog_width, dlog_height), SRCALPHA) #create surface for the textbox
		#now draw dialog background
		tile_buf = pygame.Surface((8, 8), SRCALPHA) #create a surface to hold a tile
		#draw four corners
		self.choice_tiles.get_tile(0, 0, tile_buf) #get top left corner
		self.dlog_surf.blit(tile_buf, (0, 0)) #draw it
		tile_buf.fill((0, 0, 0, 0), special_flags=BLEND_RGBA_MIN) #clear tile buffer
		self.choice_tiles.get_tile(2, 0, tile_buf) #get top right corner
		self.dlog_surf.blit(tile_buf, (dlog_width-8, 0)) #draw it
		tile_buf.fill((0, 0, 0, 0), special_flags=BLEND_RGBA_MIN) #clear tile buffer
		self.choice_tiles.get_tile(0, 2, tile_buf) #get bottom left corner
		self.dlog_surf.blit(tile_buf, (0, dlog_height-8)) #draw it
		tile_buf.fill((0, 0, 0, 0), special_flags=BLEND_RGBA_MIN) #clear tile buffer
		self.choice_tiles.get_tile(2, 2, tile_buf) #get bottom right corner
		self.dlog_surf.blit(tile_buf, (dlog_width-8, dlog_height-8)) #draw it
		tile_buf.fill((0, 0, 0, 0), special_flags=BLEND_RGBA_MIN) #clear tile buffer
		#now, draw top and bottom edges
		self.choice_tiles.get_tile(1, 0, tile_buf) #get top edge tile
		self.cursor_tile.fill((0, 0, 0, 0), special_flags=BLEND_RGBA_MIN) #clear tile buffer
		self.choice_tiles.get_tile(1, 2, self.cursor_tile) #get bottom edge tile
		for x in xrange(8, dlog_width-8, 8): #loop through tile positions
			self.dlog_surf.blit(tile_buf, (x, 0)) #draw top edge tile
			self.dlog_surf.blit(self.cursor_tile, (x, dlog_height-8)) #draw bottom edge tile
		#draw left and right edges
		tile_buf.fill((0, 0, 0, 0), special_flags=BLEND_RGBA_MIN) #clear tile buffer
		self.choice_tiles.get_tile(0, 1, tile_buf) #get left edge tile
		self.cursor_tile.fill((0, 0, 0, 0), special_flags=BLEND_RGBA_MIN) #clear tile buffer
		self.choice_tiles.get_tile(2, 1, self.cursor_tile) #get right edge tile
		for y in xrange(8, dlog_height-8, 8): #loop through tile positions
			self.dlog_surf.blit(tile_buf, (0, y)) #draw left edge tile
			self.dlog_surf.blit(self.cursor_tile, (dlog_width-8, y)) #draw right edge tile
		#now, fill in dialog middle
		tile_buf.fill((0, 0, 0, 0), special_flags=BLEND_RGBA_MIN) #clear tile buffer
		self.choice_tiles.get_tile(1, 1, tile_buf) #get center tile
		for y in xrange(8, dlog_height-8, 8): #loop through rows
			for x in xrange(8, dlog_width-8, 8): #and tiles
				self.dlog_surf.blit(tile_buf, (x, y)) #fill one tile
		#load cursor tile
		self.cursor_tile.fill((0, 0, 0, 0), special_flags=BLEND_RGBA_MIN) #clear tile buffer
		self.choice_tiles.get_tile(0, 3, self.cursor_tile) #load it
		#now, draw options
		y = 8 #current y position of drawing
		for choice in choices: #loop through choices
			self.dlog_font.render(choice, self.dlog_surf, (18, y)) #render one
			y += self.dlog_font.height #go to next line
		self.choices = choices #store choices
		self.drawing = True #we're currently showing something
		self.curr_choice = 0 #zero current choice
		

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
		self.choice_tiles = tileset.Tileset(dlog["choice_file"], 8, 8) #load choice tileset
		self.dlog_rect = dlog["text_rect"] #get text rect
		self.dlog_font = font.Font(dlog["font"]) #load font we're going to use for drawing
		self.waiting = False #whether we're waiting for the player to press action
		self.text = [] #list of characters to draw
		self.text_surf = pygame.Surface(self.dlog_rect.size) #create a surface to draw text on
		self.text_surf.set_colorkey((127, 182, 203)) #set a colorkey for it
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