import pygame #import everything pygame-related
from pygame.locals import *

import settings #load settings manager
import data

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
		self.vars = {} #dictionary of variables for the current script
	def get_var(self, var): #parse a variable string and return its value
		try: #try to parse it as a variable
			type = var[0] #get parts
			name = var[1:]
			if type == ".": #if it's a local variable
				return self.vars[name] #return its value
		except:
			pass
		try: #try to parse it as a number
			return int(var)
		except:
			pass
		return None #we couldn't parse it
	def get_object(self, name): #get a certain object
		if name == "" or name == "self": #if it's a blank name or refers to self
			return self.obj #return the object we're bound to
		elif name == "none": #if it's none
			return None
		else:
			return self.obj.game.objects[name] #return the 
	def dialog_cb(self, result): #callback for dialog completion
		self.vars["dlog_result"] = result #store result in variables
	def cmd_dialog(self, cmd): #handle command
		self.dlog_wait = True #we're waiting for a dialog
		self.obj.game.show_dlog(data.get_node_text(cmd), self.get_object(cmd.getAttribute("talker")), callback=self.dialog_cb) #show the dialog
	def cmd_if(self, cmd): #handle if command
		#get parameters
		left = self.get_var(cmd.getAttribute("left"))
		op = cmd.getAttribute("op")
		right = self.get_var(cmd.getAttribute("right"))
		comparison = False #result of the comparison
		if op == "=": #if we're comparing equality
			comparison = True if left == right else False #do comparison
		if comparison: #if the comparison was true
			next = cmd.getElementsByTagName("then")[0] #get the then element
			self.callstack.append(self.curr_command.nextSibling) #save next command
			self.curr_command = next.firstChild #store first then command
		else: #if the comparison failed
			next = cmd.getElementsByTagName("else") #get an else element
			if len(next) == 0: #if there is none
				self.curr_command = self.curr_command.nextSibling #go to next command
				return
			self.callstack.append(self.curr_command.nextSibling) #save next command
			self.curr_command = next[0].firstChild #store first command of else
	def cmd_set_visible(self, cmd): #handle set visible command
		to = cmd.getAttribute("to").lower() #calculate new visibility
		if to == "true":
			to = True
		else:
			to = False
		self.get_object(cmd.getAttribute("what")).visible = to #set visibility
	def cmd_set_camera(self, cmd): #handle set camera command
		#set what the camera follows
		self.obj.game.camera_follow = self.get_object(cmd.getAttribute("follow"))
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
		elif self.curr_command.localName == "if": #if it's an if
			self.cmd_if(self.curr_command) #handle it
			return #skip going to next command
		elif self.curr_command.localName == "set_visible": #change an object's visibility
			self.cmd_set_visible(self.curr_command)
		elif self.curr_command.localName == "set_camera": #change what the camera follows
			self.cmd_set_camera(self.curr_command)
		self.curr_command = self.curr_command.nextSibling #go to next command
	def update(self): #update script state
		if not self.running: return #return if we aren't running
		r = None #return value of next_cmd
		while r != True: #while we haven't had a reason to stop
			r = self.next_cmd() #run the next command