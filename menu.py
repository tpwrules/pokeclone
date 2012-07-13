import pygame #import everything pygame-related
from pygame.locals import *

import dialog #load dialog manager
import settings #and game settings
import font

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
		self.choices = ["Pok{ae}mon", "Save", "Title Screen", "Cancel"] #store currently shown choices
		self.choice_dlog.show_choices(self.choices) #start choice dialog showing
		self.update_func = self.main_update #store our update function
	def main_update(self, surf): #display main selection
		self.menu = None
		choice = self.choice_dlog.update(surf, (0, 0)) #draw selection
		if choice is None: #if a choice hasn't been picked yet
			return #don't do anything
		if self.choices[choice] == "Cancel": #if cancel was pressed
			self.game.menu_showing = False #menu isn't showing anymore
		elif self.choices[choice] == "Title Screen": #if title screen was pressed
			self.start_title_screen() #start showing info
		elif self.choices[choice] == "Save": #if save was pressed
			self.start_save() #start showing info
		elif self.choices[choice] == "Pok{ae}mon": #if pokemon was pressed
			self.start_pokemon() #start showing info
	def start_title_screen(self): #start showing title screen questions
		#show question
		self.dlog.draw_text("Would you like to return to the title screen?{choices}Yes{endchoice}No{endchoice}{endchoices}")
		self.update_func = self.title_screen_update #store our update function
	def title_screen_update(self, surf): #update for title screen
		choice = self.dlog.update(surf, (0, 1)) #draw dialog
		if choice == 0: #if yes has been pressed
			self.g.reset() #do a reset
		elif choice == 1: #if no was pressed
			self.game.menu_showing = False #menu shouldn't be showing any more
	def start_save(self): #start showing save questions
		self.saved = False #we haven't saved yet
		#show question
		self.dlog.draw_text("Would you like to save?{choices}Yes{endchoice}No{endchoice}{endchoices}")
		self.update_func = self.save_update #store our update function
	def save_update(self, surf): #update save data
		choice = self.dlog.update(surf, (0, 1)) #draw dialog
		if choice is True and self.saved is True: #if dialog ended and we've saved
			self.game.menu_showing = False #menu shouldn't be showing any more
		elif choice is True and self.saved is False: #dialog ended and we haven't saved
			self.game.save() #cue to start saving
			self.dlog.draw_text("Game has been saved!{wait}") #show game saved message
			self.saved = True #we've saved
		elif choice == 0: #if the user said to save
			self.dlog.draw_text("Saving...") #show saving message
		elif choice == 1: #if the user said not to save
			self.game.menu_showing = False #menu shouldn't be showing any more
	def start_pokemon(self):
		self.menu = PokemonMenu(self) #create pokemon menu
		self.update_func = self.menu.update #start its update function
	def update(self, surf): #update ourselves
		self.update_func(surf) #call current update function

class PokemonMenu: #menu for displaying pokemon
	def __init__(self, menu):
		self.game = menu.game #store parameters
		self.g = menu.g
		self.menu = menu
		#initialize stuff
		self.font = font.Font("fonts/dialog_font.xml") #create font for drawing
	def finish(self):
		self.menu.show() #re-show the menu
	def update(self, surf): #update ourselves
		surf.fill((255, 255, 255)) #clear surface
		ypos = 10
		for mon in self.game.player.pokemon: #loop through player's pokemon
			self.font.render(mon.show_name, surf, (10, ypos)) #show the pokemon's name
			ypos += self.font.height
			self.font.render("HP: "+str(mon.hp)+"/"+str(mon.stats[0])+" Lv: "+str(mon.level), surf, (10, ypos))
			ypos += self.font.height+4
		if self.g.curr_keys[settings.key_accept]: #if accept has been pressed
			self.finish() #we're done