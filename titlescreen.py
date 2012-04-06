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
		self.dlog = dialog.ChoiceDialog(self.g, "standard") #initialize new dialog for choices
		#initialize new surface to draw stuff on
		self.surf = pygame.Surface((settings.screen_x, settings.screen_y))
		#now we need to load all of the title pictures
		def tstr(n): #converts a number to a string with a leading zero
			s = str(n)
			return s if len(s) == 2 else "0"+s
		self.title_pics = [] #list of pictures
		for x in xrange(39): #load 39 frames
			#load one frame
			pic = pygame.image.load("data/titlescreen/titlescreen"+tstr(x)+".png")
			pic.convert() #convert picture for faster drawing
			self.title_pics.append(pic) #add it to picture list
		self.update_func = self.main_update #store update function
		self.check_environment() #make sure the environment is up to snuff
		self.start_main() #start main function
	def check_environment(self): #make sure environment is up to snuff
		expected = (1,9,1) #expected version to compare with
		real = pygame.version.vernum #given version
		incorrect = True
		if real[0] >= expected[0]: #check first number
			if real[1] >= expected[1]: #and second
				incorrect = False #correct version
		real = pygame.version.ver #given version
		incorrect = False
		for num in zip(real, expected): #check version tuples
			if num[0] > num[1]: #if real number is > expected, automatic win
				break
			elif num[0] < num[1]: #otherwise, if real is < expected, automatic fail
				incorrect = True
				break
		if incorrect: #if version number is incorrect
			try: #attempt to show pretty error
				self.dlog = dialog.Dialog(self.g, "standard") #load standard dialog
				#show error
				self.dlog.draw_text("Error! Your pygame version isn't up to snuff  and the game won't be able to run.{wait}")
				self.environ_error() #run function once to check for issues
				self.update_func = self.environ_error #set new update function
			except Exception as e: #if that couldn't be done
				print "-----ENVIRONMENT ERROR-----"
				print "Pygame is not up to date, game will not run!"
				print "-----ENVIRONMENT ERROR-----"
				raise Exception("Pygame not up to date")
	def environ_error(self): #show environment error
		self.surf.fill((0, 0, 0)) #clear out surface
		result = self.dlog.update(self.surf, (0, 1)) #show error dialog
		if result is True: #if dialog finished
			raise Exception("Pygame not up to date") #die
	def start_game(self): #start the game running
		self.g.title_screen = None #remove ourselves from the globals
		self.g.game = game.Game(self.g) #initialize a new game
		self.g.game.start() #tell it to start running
		self.g.update_func = self.g.game.update #store new update function
	def start_main(self): #start showing main title screen
		self.switch = False #whether we should switch this frame
		self.curr_frame = 0 #current frame to display
	def main_update(self): #update showing the picture
		if self.switch is True: #if we should switch this frame
			self.curr_frame += 1 #increment picture
			if self.curr_frame == len(self.title_pics): #if we're at the end
				self.curr_frame = 0 #go back to beginning
		self.switch = not self.switch #invert switch so we switch every other frame
		self.surf.blit(self.title_pics[self.curr_frame], (0, 0)) #show current picture
		if self.g.curr_keys[settings.key_accept]: #if accept key was pressed
			self.update_func = self.choice_update #switch update functions
			self.start_choices() #and start showing choices
	def start_choices(self): #show load choice screen
		if path.exists(settings.save_name): #if save file exists
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
			self.g.save.load(settings.save_name) #load savegame
		elif choice == 1: #if new was pressed
			self.g.save.new() #start a new savegame
		self.start_game() #start the game running
	def update(self): #update ourselves
		self.update_func() #call specified update function
		return self.surf #return our surface