import data #load data handling functions
import poke_types #load type information

class Container:
	pass

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
	def clone(self): #return a clone of this data
		return PokemonData(self.dom)

pokemon_data = {} #dict for holding data on each pokemon

def load_data(): #load all pokemon data
	global pokemon_data
	pokemon_data = {} #ensure data list is cleared
	pokemen = data.load_xml("pokemon_data.xml").documentElement # get list of pokemon
	for pokemon in pokemen.getElementsByTagName("pokemon"): #loop through all pokemon
		name = pokemon.getAttribute("name") #get name of pokemon
		poke_data = data.load_xml(data.get_node_text(pokemon)).documentElement #load data file
		pokemon_data[name] = PokemonData(poke_data) #load and parse data