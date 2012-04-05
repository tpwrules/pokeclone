import pygame #import everything pygame-related
from pygame.locals import *

import dialog #load dialog manager
import settings #and game settings

class Menu: #class to manage the in-game menus
	def __init__(self, game):
		self.game = game #store given parameters
		self.g = game.g
		#initialize dialogs
		self.choice_dlog = dialog.ChoiceDialog(self.g, "standard")
		self.dlog = dialog.Dialog(self.g, "standard")
		self.start_main_update() #start displaying main selection
		self.show = self.start_main_update #set function to show ourselves
	def start_main_update(self): #start displaying main selection
		self.choices = ["Save", "Title Screen", "Cancel"] #store currently shown choices
		self.choice_dlog.show_choices(self.choices) #start choice dialog showing
		self.update_func = self.main_update #store our update function
	def main_update(self, surf): #display main selection
		choice = self.choice_dlog.update(surf, (0, 0)) #draw selection
		if choice is None: #if a choice hasn't been picked yet
			return #don't do anything
		
	def update(self, surf): #update ourselves
		self.update_func(surf) #call current update function