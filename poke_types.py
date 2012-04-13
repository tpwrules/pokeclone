from xml.dom.minidom import parseString #import XML parser for loading pokemon types
import gzip #import gzip file reader for loading xml data
from fractions import Fraction #import fractions for more accurate numbers

class PokemonType: #class to hold data for one type
	def __init__(self, data): #initialize type data
		self.name = data["name"] #store name
		self.modifiers = data["modifiers"] #store modifier list
	def get_effectiveness(self, attacker): #get the effectiveness for a given attacker
		try: #return it if it exists
			return self.modifiers[attacker]
		except: #if it didn't exist
			return Fraction(1) #just use the default
		
poke_types = {} #dictionary to hold the different types

def load_data(): #load the type data
	global poke_types
	poke_types = {} #ensure type data is cleared
	dom = gzip.open("data/types.xml.gz", "rb").read() #load xml data from archive
	dom = parseString(dom).documentElement #read in and parse type data
	for type in dom.getElementsByTagName("type"): #loop through different types
		type_data = {} #dictionary to hold data for this type
		type_data["name"] = type.getAttribute("name") #store name of type
		type_data["modifiers"] = {} #dictionary to hold modifier data
		for modifier in type.getElementsByTagName("modifier"): #loop through different modifiers
			#store modifier data
			type_data["modifiers"][modifier.getAttribute("defender")] = \
				Fraction(modifier.getAttribute("amount"))
		poke_types[type_data["name"]] = PokemonType(type_data) #store a type class for this type