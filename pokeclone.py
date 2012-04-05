import pygame #import everything pygame-related
from pygame.locals import *

import settings #load game settings
import game #and game engine
import savegame #load savegame manager
import titlescreen #load title screen

#import parts of game that need loading
import poke_types

class Container: #blank class to store global variables
	pass
	
def wait_frame(): #wait for the next frame
	global g
	g.next_frame += 1000.0/settings.framerate #calculate time of next frame
	now = pygame.time.get_ticks() #get current number of ticks
	g.next_fps += 1 #increment one frame
	if g.next_frame < now: #if we've already passed the next frame
		g.next_frame = now #try to go as fast as possible
	else: #if we haven't
		pygame.time.wait(int(g.next_frame)-now) #wait for next frame
	if now / 1000 != g.prev_secs: #if one frame has passed
		g.fps = g.next_fps #set framerate
		g.next_fps = 0 #clear next framerate
		g.prev_secs = now/1000 #store the second this number was calculated

def reset(): #reset the game
	global g
	g.game = None #destroy current game
	g.save.new() #create a new save file
	g.title_screen = titlescreen.TitleScreen(g) #initialize title screen
	g.update_func = g.title_screen.update #set update function
	
g = Container() #get the global variable container

g.keys = [False]*len(settings.keys) #variable to hold states of keys
g.old_keys = [False]*len(settings.keys) #and previous keys
g.curr_keys = [False]*len(settings.keys) #only true when key has been pressed this frame

running = True #if this is true, we continue the main loop
screen = pygame.display.set_mode((settings.screen_x*settings.screen_scale, \
	settings.screen_y*settings.screen_scale)) #create a window to draw on
g.screen = screen #store it in the globals
pygame.display.set_caption("Pokeclone") #set screen title

g.next_frame = 0 #tick number of the next frame
g.fps = 0 #current FPS
g.next_fps = 0 #next FPS
g.prev_secs = 0 #previous number of seconds

poke_types.load_data() #load pokemon type data

g.save = savegame.SaveGame(g) #initialize a new savegame manager

g.reset = reset #store reset function

reset() #reset game

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
	surface = g.update_func() #tell current object to update for one frame
	pygame.transform.scale(surface, (settings.screen_x*settings.screen_scale, \
		settings.screen_y*settings.screen_scale), screen) #draw the screen scaled properly
	pygame.display.flip() #flip double buffers
	#g.clock.tick(30) #and wait for next frame (at 30 fps)
	wait_frame()
