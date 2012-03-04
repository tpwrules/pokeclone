import pygame #import everything pygame-related
from pygame.locals import *

import settings #load game settings
import game #and game engine

class Container: #blank class to store global variables
	pass
	
g = Container() #get the global variable container

g.keys = [False]*len(settings.keys) #variable to hold states of keys
g.old_keys = [False]*len(settings.keys) #and previous keys
g.curr_keys = [False]*len(settings.keys) #only true when key has been pressed this frame

running = True #if this is true, we continue the main loop
screen = pygame.display.set_mode((settings.screen_x*settings.screen_scale, \
	settings.screen_y*settings.screen_scale)) #create a window to draw on
g.screen = screen #store it in the globals
pygame.display.set_caption("Pokeclone") #set screen title
g.clock = pygame.time.Clock() #and a clock for keeping the framerate

g.game = game.Game(g) #create a new game class and give it our globals

g.game.start() #tell it to start from scratch

while running: #loop while we are still running
	for event in pygame.event.get(): #process events
		if event.type == QUIT: #if we're being told to quit
			running = False #stop running
			break #and stop processing events
		elif event.type == KEYDOWN: #if a key has been pressed
			if event.key in settings.keys: #if it's one we care about
				index = settings.keys.index(event.key) #get its index
				g.keys[index] = True #and mark it as pressed
		elif event.type == KEYUP: #if a key has been released
			if event.key in settings.keys: #if it's one we care about
				index = settings.keys.index(event.key) #get its index
				g.keys[index] = False #mark key as released
	if g.keys[settings.key_escape] == True: #if the escape key has been pressed
		break #stop running
	if running == False: #if we aren't supposed to be running any more
		break #stop running
	#update key variables
	for x in xrange(len(settings.keys)): #loop through key indices
		t = g.keys[x] ^ g.old_keys[x] #get whether this key has changed this frame
		t = t & g.keys[x] #make it true only if the key was pressed this frame
		g.curr_keys[x] = t #save key state
		g.old_keys[x] = g.keys[x] #and update old keys
	surface = g.game.update() #tell the game engine to update for one frame
	pygame.transform.scale(surface, (settings.screen_x*settings.screen_scale, \
		settings.screen_y*settings.screen_scale), screen) #draw the screen scaled properly
	pygame.display.flip() #flip double buffers
	g.clock.tick(30) #and wait for next frame (at 30 fps)