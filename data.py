#miscellaneous helper functions
import pygame #import everything pygame-related
from pygame.locals import *
from xml.dom.minidom import parse
import os

import settings

def get_node_text(node, strip_newlines=True): #get all the text from a node
	texts = []
	for n in node.childNodes: #loop through children
		if n.nodeType == n.TEXT_NODE: #if it's text
			texts.append(n.data) #store its value
	texts = "".join(texts) #combine all the text together
	if strip_newlines: #if we're supposed to remove newlines
		return texts.replace("\r", "").replace("\n", "") #do so
	return texts #return combined text

def get_path(path, with_data=True): #convert a path to one appropriate for the host with the data directory
	path = path.replace("\\", "/") #convert backslashes to forward slashes
	if with_data: #if we're prepending the data directory
		ret = get_path(settings.data_path, False) #get it
	else: #if we aren't
		ret = "" #start with a blank string
	if path[:5] == "data/": raise Exception
	for part in path.split("/"): #loop through path components
		ret = os.path.join(ret, part) #join them together
	return ret #return finished product

def load_image(path): #load an image
	return pygame.image.load(get_path(path))

def load_xml(path): #load xml data
	return parse(get_path(path))