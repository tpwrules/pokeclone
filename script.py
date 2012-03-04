import pygame #import everything pygame-related
from pygame.locals import *

import settings #load settings manager

#class for object scripts
class Script:
	def __init__(self, obj): #initialize ourselves
		self.obj = obj #store object
		self.running = False #we aren't running
	def start_script(self, s): #start a script running
		self.running = True #we're running
		self.curr_script = s #store script
		self.curr_command = s.firstChild #and first command
		self.dlog_wait = False #mark whether we're waiting for a dialog
	def cmd_dialog(self, cmd): #handle command
		self.dlog_wait = True #we're waiting for a dialog
		text_list = [] #list of text nodes
		for n in cmd.childNodes: #loop through text
			if n.nodeType == n.TEXT_NODE: #if it's a text node
				text_list.append(n.data) #add it to text list
		self.obj.game.show_dlog("".join(text_list)) #show the dialog
	def update(self): #update script state
		if not self.running: return #return if we aren't running
		#if we're waiting for a dialog and one is being drawn
		if self.dlog_wait and self.obj.game.dialog_drawing: return #then return
		if self.curr_command == None: #if we're at the end of the script
			self.running = False #stop running
			return #and return
		if self.curr_command.localName == "dialog": #if it's a dialog command
			self.cmd_dialog(self.curr_command) #handle it
		self.curr_command = self.curr_command.nextSibling #go to next command