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
		self.wait = 0 #mark whether we're waiting, 0=none, 1=dlog, 2=move
		self.callstack = [] #callstack for command execution
		self.vars = {} #dictionary of variables for the current script
		#load persistent vars
		self.persistent_vars = self.obj.game.g.save.get_prop(self.obj.id, "script_vars", {})
	def get_var(self, var): #parse a variable string and return its value
		try: #try to parse it as a number
			return int(var)
		except:
			pass
		try: #try to parse it as a variable
			var_type = var[0] #get parts
			name = var[1:]
			if var_type == ".": #if it's a script local variable
				return self.vars[name] #return its value
			elif var_type == "#" #if it's script persistent
				return self.persistent_vars[name]
		except:
			return 0 #return variable default
	def set_var(self, var, val): #parse a variable string then set it
		try:
			var_type = var[0] #get type
			name = var[1:] #and name
			if var_type == ".": #if it's script local
				self.vars[name] = val
			elif var_type == "#": #if it's script persistent
				self.persistent_vars[name] = val
		except:
			pass
	def get_object(self, name): #get a certain object
		if name == "" or name == "self": #if it's a blank name or refers to self
			return self.obj #return the object we're bound to
		elif name == "none": #if it's none
			return None
		else:
			return self.obj.game.objects[name] #return the 
	def dialog_cb(self, result): #callback for dialog completion
		self.vars["dlog_result"] = result #store result in variables
	def script_stop(self): #called to stop the script
		#save persistent variables
		self.obj.game.g.save.set_prop(self.obj.id, "script_vars", self.persistent_vars)
		self.running = False #we're not running any more
	def cmd_dialog(self, cmd): #handle command
		self.wait = 1 #we're waiting for a dialog
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
		obj = self.get_object(cmd.getAttribute("what"))
		obj.visible = to #set visibility
		obj.game.set_obj_pos(obj, None) #remove object from collisions
		if to: #if it's being made visible
			obj.game.set_obj_pos(obj, obj.tile_pos) #set its position
	def cmd_set_camera(self, cmd): #handle set camera command
		#set what the camera follows
		self.obj.game.camera_follow = self.get_object(cmd.getAttribute("follow"))
	def cmd_set_move(self, cmd): #handle set movement command
		self.get_object(cmd.getAttribute("what")).move_manager.load_move_dom(cmd, False) #set the movement
	def cmd_wait_move(self, cmd): #handle movement wait command
		self.move_obj = self.get_object(cmd.getAttribute("for")).move_manager #set movement wait object
		self.wait = 2 #set movement wait
	def cmd_set_pos(self, cmd): #handle set position command
		obj = self.get_object(cmd.getAttribute("what")) #get the object to set
		t = cmd.getAttribute("to").split(",") #get new position
		obj.tile_pos = [int(t[0].strip()), int(t[1].strip())] #set it
		#update pixel position
		obj.pos = [((obj.tile_pos[0]-1)*16)+8, (obj.tile_pos[1]-1)*16]
		obj.rect = pygame.Rect(obj.pos, (32, 32))
		obj.game.set_obj_pos(obj, None) #remove object from collisions
		if obj.visible: #if it's visible
			obj.game.set_obj_pos(obj, obj.tile_pos) #set new position
	def cmd_set_var(self, cmd): #handle set variable command
		what = cmd.getAttribute("what") #get what variable to set
		to = cmd.getAttribute("to") #get what to set it to
		self.set_var(what, self.get_var(to)) #perform set
	def next_cmd(self): #process the next command
		if not self.running: return True #return if we aren't running
		#return if we're waiting for a dialog and one is being shown
		if self.wait == 1 and self.obj.game.dialog_drawing: return True
		#wait if we're waiting for movement
		if self.wait == 2 and self.move_obj.moving: return True
		self.wait = 0 #clear wait
		if self.curr_command == None: #if we're at the end of this part of the script
			while self.curr_command == None: #loop until we have a command
				if len(self.callstack) == 0: #if there is nothing in the callstack
					self.script_stop() #stop the script
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
		elif self.curr_command.localName == "set_move": #handle movement set
			self.cmd_set_move(self.curr_command)
		elif self.curr_command.localName == "wait_move": #handle movement wait
			self.cmd_wait_move(self.curr_command)
		elif self.curr_command.localName == "stop": #handle stopping the script
			self.script_stop() #stop the script
			return True
		elif self.curr_command.localName == "set_pos": #handle setting an object's position
			self.cmd_set_pos(self.curr_command)
		elif self.curr_command.localName == "set_var": #handle setting a variable
			self.cmd_set_var(self.curr_command)
		self.curr_command = self.curr_command.nextSibling #go to next command
	def update(self): #update script state
		if not self.running: return #return if we aren't running
		r = None #return value of next_cmd
		while r != True: #while we haven't had a reason to stop
			r = self.next_cmd() #run the next command