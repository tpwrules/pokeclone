#simple command line animation viewer
import pygame
from pygame.locals import *
import sys
import os

sys.path.append("..")

import animation
import settings

screen = pygame.display.set_mode((512, 512))

screen = pygame.display.set_mode((settings.screen_x*settings.screen_scale, \
	settings.screen_y*settings.screen_scale))

anim_dest = pygame.Surface((settings.screen_x, settings.screen_y))

anim = animation.PartAnimationSet(None, sys.argv[1])
anim.set_animation(sys.argv[2])

posx, posy = int(sys.argv[3]), int(sys.argv[4])

running = True

clock = pygame.time.Clock()

while running: #loop while we are still running
	for event in pygame.event.get(): #process events
		if event.type == QUIT: #if we're being told to quit
			running = False #stop running
			break #and stop processing events
		elif event.type == KEYDOWN: #if a key has been pressed
			if event.key == K_ESCAPE: #if it's one we care about
				running = False
	if running == False: #if we aren't supposed to be running any more
		break #stop running
	anim_dest.fill((255, 255, 255))
	anim.update(anim_dest, posx, posy)
	pygame.transform.scale(anim_dest, (settings.screen_x*settings.screen_scale, \
		settings.screen_y*settings.screen_scale), screen) #draw the screen scaled properly
	pygame.display.flip() #flip double buffers
	clock.tick(30)