import pygame #import everything pygame-related
from pygame.locals import *
import os.path as path

import game #load game engine
import dialog #and dialog manager
import font #and font manager
import settings #and game settings

class TitleScreen: #class for the title screen
	def __init__(self, g):
		self.g = g #store globals
		self.font = font.Font("data/fonts/dialog_font.xml") #load font for drawing press start
		self.msg_width = self.font.get_width("Press Start!") #get width of message so we can center it
		self.dlog = dialog.ChoiceDialog(self.g, "standard") #initialize new dialog for choices
		#initialize new surface to draw stuff on
		self.surf = pygame.Surface((settings.screen_x, settings.screen_y))
		self.title_pic = pygame.image.load("data/titlescreen.png") #load title picture
		self.title_pic.convert() #convert it for faster drawing
		self.update_func = self.main_update #store update function
		self.frames = 0 #number of frames for showing start message
	def start_game(self): #start the game running
		self.g.title_screen = None #remove ourselves from the globals
		self.g.game = game.Game(self.g) #initialize a new game
		self.g.game.start() #tell it to start running
		self.g.update_func = self.g.game.update #store new update function
	def main_update(self): #update showing the picture
		self.surf.blit(self.title_pic, (0, 0)) #draw title screen picture
		if self.frames <= 20: #if half a second hasn't passed yet
			#draw press start
			self.font.render("Press Start!", self.surf, ((settings.screen_x-self.msg_width)/2, 130))
		elif self.frames == 40: #if a full second has passed
			self.frames = 0 #reset counter
		self.frames += 1 #update frame counter
		if self.g.curr_keys[settings.key_accept]: #if accept key has been pressed
			self.update_func = self.choice_update #switch update funcion
			self.start_choices() #start choice updates
	def start_choices(self): #show load choice screen
		if path.exists("test.pokesav"): #if save file exists
			self.save_exists = True #mark it
		else:
			self.save_exists = False
		choices = ["New Game"]
		if self.save_exists: #if a save file exists
			choices.insert(0, "Load Game") #give option to load it
		self.dlog.show_choices(choices) #show choices
	def choice_update(self): #show load choices
		self.surf.fill((255, 255, 255)) #show white background
		choice = self.dlog.update(self.surf, (1, 1)) #draw choice dialog
		if choice is not None: #if the user chose something
			self.handle_choice(choice) #handle the choice
	def handle_choice(self, choice):
		if self.save_exists == False: #if no save exists
			choice += 1 #bump up choice number to account for missing option
		if choice == 0: #if load was pressed
			self.g.save.load("test.pokesav") #load savegame
		elif choice == 1: #if new was pressed
			self.g.save.new() #start a new savegame
		self.start_game() #start the game running
	def update(self): #update ourselves
		self.update_func() #call specified update function
		return self.surf #return our surface