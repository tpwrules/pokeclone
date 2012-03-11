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
		self.callstack = [] #callstack for command execution
	def get_text(self, node): #get text from an element
		nodes = [] #list of found text nodes
		for n in node.childNodes: #loop through text
			if n.nodeType == n.TEXT_NODE: #if it's a text node
				nodes.append(n.data) #add it to the list of text
		return "".join(nodes) #return combined string
	def cmd_dialog(self, cmd): #handle command
		self.dlog_wait = True #we're waiting for a dialog
		self.obj.game.show_dlog(self.get_text(cmd), self.obj) #show the dialog
	def next_cmd(self): #process the next command
		if not self.running: return True #return if we aren't running
		#return if we're waiting for a dialog and one is being shown
		if self.dlog_wait and self.obj.game.dialog_drawing: return True
		if self.curr_command == None: #if we're at the end of this part of the script
			while self.curr_command == None: #loop until we have a command
				if len(self.callstack) == 0: #if there is nothing in the callstack
					self.running = False #we're not running any more
					return True
				self.curr_command = self.callstack.pop() #get another command from the callstack
		if self.curr_command.localName == "dialog": #if it's a dialog command
			self.cmd_dialog(self.curr_command) #handle it
		self.curr_command = self.curr_command.nextSibling #go to next command
	def update(self): #update script state
		if not self.running: return #return if we aren't running
		r = None #return value of next_cmd
		while r != True: #while we haven't had a reason to stop
			r = self.next_cmd() #run the next command