import pygame #import everything pygame-related
from pygame.locals import *
import random #load rng for determining battle stuff

import dialog #load dialog manager
import settings #and game settings
import transition
import pokemon
import animation
import data

class Battle: #class to manage a battle
	def __init__(self, game): #initialize ourselves
		self.g = game.g #store parameters
		self.game = game
		self.player = game.player
		self.g.update_func = self.update #store update function
		self.g.battle = self #store ourselves in globals
		#create a surface to render on
		self.surf = pygame.Surface((settings.screen_x, settings.screen_y))
		self.transition = None #currently runnining transition
		self.task_list = [] #list of things to do
		self.curr_task = None #current task function
	def start_battle(self): #start any type of battle
		self.dlog = dialog.Dialog(self.g, "battle") #initialize a dialog to draw with
		self.choice_dlog = dialog.ChoiceDialog(self.g, "battle") #create a choice dialog
		self.transition = transition.BattleOpen() #start transitioning to a battle
	def start_wild(self, type, level): #start a wild battle
		self.wild = True #this is a wild battle
		self.start_battle() #prepare battle
		self.enemy_mon = pokemon.get_data(type).generate(level) #create a new wild pokemon
		self.enemy_mon_anim = animation.PartAnimationSet(self.g, self.enemy_mon.data.anim_front) #load its animation
		self.enemy_mon_anim.set_animation("demo")
		#initialize task list
		self.task_list = [self.wait_transition, #wait for transition to complete
			self.show_wild_mon, #show the wild pokemon appearing
			self.wait_dialog, #wait for the dialog text to finish
			self.command_loop] #start command loop
		self.next_task() #kick off task list
	def start_trainer(self, trainer): #start a trainer battle
		self.wild = False #this is not a wild battle
		self.start_battle() #prepare battle
		#generate encounter text
		s = "You encountered "+trainer.class_name+" "+trainer.trainer_name+"{br}with the following pok{ae}mon:{wait}{br}"
		for mon in trainer.party:
			s += "A level "+str(mon[1])+" "+mon[0]+"{wait}{br}"
		s += "That's it!{wait}"
		#self.dlog.draw_text(s)
		self.task_list = [self.done, self.dummy]
		self.next_task()
	def show_wild_mon(self): #show wild pokemon info
		self.dlog.draw_text("{clear}A wild "+self.enemy_mon.show_name+" appeared!{wait}{clear}")
		self.next_task()
	def wait_transition(self): #task that waits for a transition to complete
		if self.transition is None: #if there is no transition
			self.next_task() #go to next task
	def wait_dialog(self): #task that waits for a dialog to complete
		if self.dlog.drawing == False and self.choice_dlog.drawing == False: #if the dialog is not drawing
			self.next_task() #go to next task
	def command_loop(self): #command loop start task
		self.task_list = [self.show_options,
			self.select_option, #select whether to fight, run, etc
			self.command_loop] #call ourselves again
		self.next_task() #start the next task
	def show_options(self):
		self.choice_dlog.show_choices(["Um...", "Er...", "Uh...", "RUN!!"]) #show choices
		self.choice_result = None #clear choice result
		self.dlog.draw_text("What will whoever do?")
		self.next_task()
	def select_option(self): #select a battle option
		if self.choice_result is None: return #don't do anything if the result is still none
		if self.choice_result < 3: #if the option is not run
			self.dlog.draw_text("Nothing happens!{wait}") #show message
			self.task_list = [self.wait_dialog, self.command_loop]
			self.next_task()
		else:
			self.dlog.draw_text("Got away safely!{wait}")
			self.task_list = [self.wait_dialog, self.done, self.dummy]
			self.next_task()
		self.choice_result = None
	def next_task(self): #go to the next task
		self.curr_task = self.task_list[0] #set current task
		self.task_list = self.task_list[1:] #remove it from task list
	def done(self): #called when battle is done
		self.g.battle = None #remove ourselves from globals
		self.g.update_func = self.game.update #restore game update function
		self.game.transition(transition.FadeIn(25)) #start a fade in
		self.next_task()
	def dummy(self): #dummy task that halts, used for exiting
		pass
	def update(self): #update ourselves
		self.surf.fill((255, 255, 255)) #clear our surface
		self.curr_task() #call current task
		self.enemy_mon_anim.update(self.surf, 30, 30)
		self.dlog.update(self.surf, (0, 144), True) #update dialog
		if self.choice_dlog.drawing == True: #if the choice dialog needs to be updated
			self.choice_result = self.choice_dlog.update(self.surf, (settings.screen_x-self.choice_dlog.dlog_width-4, settings.screen_y-self.choice_dlog.dlog_height-4))
		if self.transition is not None: #if there is a transition to render
			if self.transition.update(self.surf): #update and check if transition is done
				self.transition = None #clear transition if it is done
		return self.surf #return surface to render