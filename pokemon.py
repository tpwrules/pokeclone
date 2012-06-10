import random

import data #load data handling functions
import poke_types #load type information

class Container:
	pass

#note on stat ordering:
#ordered HP, attack, defense, speed, sp. attack, sp. defense always

class PokemonData: #class for holding data on a pokemon
	def __init__(self, dom=None): #initialize ourselves based on a given dom
		if dom is not None:
			self.load_data(dom)
	def load_data(self, dom): #load data from a dom
		self.dom = dom
		self.data = Container()
		d = self.data
		g = data.get_xml_prop
		d.name = g(dom, "name") #load various root properties
		d.show_name = g(dom, "show_name")
		d.anim = g(dom, "anim")
		d.species = g(dom, "species")
		d.exp_growth = g(dom, "exp")
		d.number = int(g(dom, "num"))
		d.catch_rate = int(g(dom, "catch"))
		d.gender_ratio = int(g(dom, "gender"))
		#load type data
		d.type = [x for x in g(dom, "type").split("|")]
		#load pokedex data
		t = data.get_node(dom, "pokedex")
		d.pokedex = Container()
		d = d.pokedex
		d.height = int(g(t, "height"))
		d.weight = float(g(t, "weight"))
		d.description = g(t, "desc")
		d.color = g(t, "color")
		d.number = int(g(t, "num"))
		#load ability data
		self.data.ability = Container()
		self.data.ability.normal = []
		self.data.ability.hidden = []
		t = data.get_node(dom, "ability").getElementsByTagName("normal")
		for ability in t:
			self.data.ability.normal.append(data.get_node_text(ability))
		t = data.get_node(dom, "ability").getElementsByTagName("hidden")
		for ability in t:
			self.data.ability.hidden.append(data.get_node_text(ability))
		self.data.breeding = Container()
		d = self.data.breeding #load breeding data
		d.group = g(dom, "group")
		d.cycles = int(g(dom, "cycles"))
		self.data.base = Container() #base yield data load
		d = self.data.base
		t = data.get_node(dom, "base")
		d.exp = int(g(t, "exp"))
		d.ev = []
		d.stats = []
		for ev in g(t, "ev").split("|"):
			d.ev.append(int(ev))
		for stat in g(t, "stats").split("|"):
			d.stats.append(int(stat))
		#DOES NOT LOAD EVOLUTION DATA!!!
		self.data.learnset = Container()
		d = self.data.learnset
		t = data.get_node(dom, "learnset")
		d.level = []
		for level in data.get_node(dom, "level").getElementsByTagName("move"):
			d.level.append((int(level.getAttribute("level")), data.get_node_text(level)))
		d.tm = []
		d.hm = []
		for tm in g(t, "tm").split("|"):
			d.tm.append(int(tm))
		for hm in g(t, "hm").split("|"):
			d.hm.append(int(hm))
	def generate(self, level): #generate a wild pokemon from this data at a specific level
		return Pokemon(self.data, level)
	def calc_exp(self, level): #calculate the needed experience for a given level
		#formulas taken from bulbapedia
		if level <= 1: #if it's the first level
			return 0 #always have 0 exp
		level = float(level) #convert level to float for accurate calculations
		cubed = level*level*level #common to all formulas
		growth = self.data.exp_growth #get growth type
		r = 0 #return value for experience
		if growth == "erratic":
			#erratic has four different formulas based on level
			if level <= 50:
				r = (cubed*(100-level))/50
			elif level <= 68:
				r = (cubed*(150-level))/100
			elif level <= 98:
				r = (cubed*((1911-(10*level))/3))/500
			elif level <= 100:
				r = (cubed*(160-level))/100
		elif growth == "fast":
			r = (4*cubed)/5
		elif growth == "medfast":
			r = cubed
		elif growth == "medslow":
			r = ((6*cubed)/5) - (15*level*level) + (100*level) - 140
		elif growth == "slow":
			r = (5*cubed)/4
		elif growth == "fluctuating":
			if level <= 15:
				r = cubed*((((level+1)/3)+24)/50)
			elif level <= 36:
				r = cubed*((level+14)/50)
			elif level <= 100:
				r = cubed*(((level/2)+32)/50)
		return int(r) #return experience required

class Pokemon(PokemonData): #class to hold one pokemon
	def __init__(self, data=None, level=None): #initialize ourselves
		if data is not None: #if data was given
			self.data = data #store it
			self.generate(level) #and generate a new wild pokemon
	def generate(self, level): #generate a new wild pokemon
		self.name = self.data.name #store the name of ourselves
		self.level = level #store given level
		self.curr_exp = self.calc_exp(level) #store the experience we start with
		self.moves = [] #clear move data
		#wild pokemon always know the four most recent moves they learn by level
		possible_moves = sorted(self.data.learnset.level)[::-1] #sort moves reversed by level
		for move in possible_moves: #for each move this pokemon could know
			if move[0] <= level: #if it's able to be learned at this level
				if move[1] in self.moves: continue #don't add it if we already have
				self.moves.append(move[1]) #add it to moves
			if len(self.moves) == 4: #if we found four moves
				break #stop looking
		self.iv = [random.randrange(0, 32) for x in xrange(6)] #generate individual values
		self.ev = [0]*6 #and clear evolution values
		self.stats = [self.calc_stat(x) for x in xrange(6)] #generate pokemon stats
		#generate abilities
		self.ability = self.data.ability.normal[random.randrange(0, len(self.data.ability.normal))]
		self.hidden_ability = self.data.ability.hidden[random.randrange(0, len(self.data.ability.hidden))]
		#generate gender
		#gender is -1 for ungendered, 0 for male, and 1 for female
		if self.data.gender_ratio == -1: #if it's ungendered
			self.gender = -1 #say so
		else:
			if random.randrange(0, 100) < self.data.gender_ratio: #if it's going to be a male
				self.gender = 0 #mark it
			else:
				self.gender = 1 #mark female
	def calc_stat(self, stat):
		#formulas taken from bulbapedia
		if stat == 0: #if stat is HP, that uses its own calculation
			t = self.iv[0]+(2*self.data.base.stats[0])+(self.ev[0]/4.0)+100
			r = ((t*self.level)/100.0)+10
		else: #other stats use a different formula
			t = self.iv[stat]+(2*self.data.base.stats[stat])+(self.ev[stat]/4.0)
			r = (((t*self.level)/100.0)+5)*1.0
		return int(r) #return calculated stat

pokemon_data = {} #dict for holding data on each pokemon
nature_data = {} #dict for holding data on each nature

def load_data(): #load all pokemon data
	global pokemon_data, nature_data
	pokemon_data = {} #ensure data list is cleared
	pokemen = data.load_xml("pokemon_data.xml").documentElement # get list of pokemon
	for pokemon in pokemen.getElementsByTagName("pokemon"): #loop through all pokemon
		name = pokemon.getAttribute("name") #get name of pokemon
		poke_data = data.load_xml(data.get_node_text(pokemon)).documentElement #load data file
		pokemon_data[name] = PokemonData(poke_data) #load and parse data
	nature_data = {} #clear out nature data
	natures = data.load_xml("nature.xml").documentElement #get nature data
	for nature in natures.getElementsByTagName("nature"): #loop through nature data
		t = Container()
		t.name = nature.getAttribute("name") #set name of nature
		num = int(nature.getAttribute("num")) #get number of nature
		t.help = int(nature.getAttribute("help")) #get which stat this nature helps
		t.hinder = int(nature.getAttribute("hinder")) #get which stat this nature hinders
		t.num = num
		nature_data[num] = t #store nature data

def get_data(pokemon): #get data for a specific pokemon
	global pokemon_data
	return pokemon_data[pokemon] #return the data