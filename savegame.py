import cPickle as pickle #load libraries for writing out save files
import zlib

import settings #import game settings so they can be saved

class SaveGame: #class to manage a savegame
	def __init__(self, g): #initialize ourselves
		self.g = g #store globals
		self.obj_props = {} #dictionary for object properties
		self.game_props = {} #dictionary for game state properties (for less ID conflicts)
	def new(self): #create a new save file
		self.obj_props = {} #empty dictionaries
		self.game_props = {}
	def load(self, filename): #load savegame data
		data = open(filename, "rb").read() #read in save data
		data = zlib.decompress(data) #decompress it
		data = pickle.loads(data) #depickle data
		self.obj_props = data[0] #get object properties
		self.game_props = data[1] #and game properties
	def save(self, filename): #write savegame data
		f = open(filename, "wb") #open file to write out data
		data = pickle.dumps([self.obj_props, self.game_props]) #pickle object data
		data = zlib.compress(data, 9) #compress pickled data
		f.write(data) #write out data
		f.close() #and close written file
	def set_prop(self, id, prop, value): #set an object property
		if id not in self.obj_props: #if this id hasn't been used yet
			self.obj_props[id] = {} #initialize it
		self.obj_props[id][prop] = value #store value
	def get_prop(self, id, prop, default=None): #get an object property
		try:
			return self.obj_props[id][prop] #attempt to get value
		except: #if it couldn't be done
			return default #return default instead
	def set_game_prop(self, id, prop, value): #set a game property
		if id not in self.game_props: #if this id hasn't been seen yet
			self.game_props[id] = {} #initialize it
		self.game_props[id][prop] = value #store value
	def get_game_prop(self, id, prop, default=None): #get a game property
		try:
			return self.game_props[id][prop] #attempt to get value
		except:
			return default #return default if it didn't exist