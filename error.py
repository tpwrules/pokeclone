import pygame #import everything pygame-related
from pygame.locals import *
import traceback #import traceback module to display exceptions
import time

import font #import font to show a pretty traceback
import settings

#defines a whole bunch of different exceptions for error handling

class QuitException(Exception): #exception to force a quit
	def __init__(self, message=""):
		Exception.__init__(self, message)

#exception handler routines
def exception_write(g, strin): #writes a line to exception outputs
	print strin #print it
	try:
		if g.out: g.out.write(strin+"\n") #write it to output if present
		if g.font is None: return #return if we don't need to write it to the screen
		words = strin.split(" ") #draw it nice and word-wrapped
		curr = []
		while len(words) > 0:
			curr.append(words[0]) #append current word
			if g.font.get_width(" ".join(curr))+4 > settings.screen_x: #if current line is too wide
				if g.linepos+g.font.height >= settings.screen_y: #if we've gone off the screen
					break #stop rendering
				g.font.render(" ".join(curr[:-1]), g.surf, (2, g.linepos)) #render the line minus last word
				g.linepos += g.font.height #go to next line
				curr = [curr[-1]] #put last word as only one in buffer
			words = words[1:] #go to next word
		#once we're done, render current buffer
		if len(curr) == 0: return #return if it's empty
		#return if we've gone off the screen
		if g.linepos+g.font.height >= settings.screen_y: return
		g.font.render(" ".join(curr), g.surf, (2, g.linepos)) #render last line
		g.linepos += g.font.height #and go to next line
	except:
		pass

def exception_handler(g, e): #handles exception
	tb = traceback.format_exc() #get exception
	try: #attempt to load a font
		g.font = font.Font("fonts/battle_font.xml")
		g.surf = pygame.Surface((settings.screen_x, settings.screen_y)) #and a surface to draw on
		g.surf.fill((0, 0, 100)) #fill with pretty blue
		g.linepos = 0
	except: #if there was an error loading it
		g.font = None #set font to none
	try: #attempt to open an output file
		g.out = open("exception.txt", "w")
	except: #if that couldn't be done
		g.out = None #set it to none
	#write header
	exception_write(g, "We're terribly sorry, but an internal error has occurred :(")
	t = "This will be written to the console" #only say file if file could be opened
	if g.out: t += " and a file named exception.txt in the current directory"
	exception_write(g, t+".")
	exception_write(g, "Press ESCAPE to exit (if displayed on-screen)")
	try: #attempt to make a backup save
		g.game.save("error.pokesav") #say if it could be done successfully
		exception_write(g, "Game was saved to error.pokesav.")
	except:
		exception_write(g, "Game could not be saved.")
	if hasattr(e, "specific"): #if the exception has specific error data
		exception_write(g, "Specific error data is:") #write it out
		for line in e.specific.split("\n"):
			exception_write(g, line)
	#now write out traceback
	for line in tb.split("\n"):
		exception_write(g, line)
	exception_write(g, "Error handler finished.")

	#now, finish display
	if g.out is not None: g.out.close() #close output file if it was opened
	if g.font is None: return #return if the font was never opened
	#otherwise, draw font and do a short event loop
	pygame.transform.scale(g.surf, (settings.screen_x*settings.screen_scale, \
		settings.screen_y*settings.screen_scale), g.screen) #draw the screen scaled properly
	pygame.display.flip() #flip double buffers
	running = True
	while running: #do a brief event loop that watches for escape key
		for event in pygame.event.get():
			if event.type == QUIT: #if we're being told to quit
				running = False #stop running
				break #and stop processing events
			elif event.type == KEYDOWN: #if a key has been pressed
				if event.key == K_ESCAPE: #and it was escape
					running = False #stop running
					break #and processing events
		time.sleep(0.1)
