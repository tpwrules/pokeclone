from OpenGL.GL import *
from OpenGL.GLU import *

#simple command line animation viewer
import pygame
from pygame.locals import *
import sys
import os

sys.path.append("..")

import animation2 as animation
import settings

#screen = pygame.display.set_mode((512, 512))

screen = pygame.display.set_mode((settings.screen_x*settings.screen_scale, \
	settings.screen_y*settings.screen_scale), OPENGL|DOUBLEBUF)

anim_dest = pygame.Surface((settings.screen_x, settings.screen_y))

w = settings.screen_x*settings.screen_scale
h = settings.screen_y*settings.screen_scale

print "gl"

glViewport(0, 0, w, h)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluOrtho2D(0, w, 0, h)
glScalef(2, -2, 1)
glTranslatef(0, -(h/2), 0)
glMatrixMode(GL_MODELVIEW)
glPushMatrix()

glEnable(GL_TEXTURE_2D)
glShadeModel(GL_SMOOTH)
glClearColor(1.0, 1.0, 1.0, 1.0)
glClearDepth(1.0)
glEnable(GL_DEPTH_TEST)
glDepthFunc(GL_LEQUAL)
glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glEnable(GL_BLEND)

anim = animation.PartAnimationSet(None, sys.argv[1].replace("data/", "").replace("data\\", ""))
anim.set_animation(sys.argv[2])

#posx, posy = int(sys.argv[3]), int(sys.argv[4])

running = True
stepping = False

clock = pygame.time.Clock()

img = pygame.image.load("/Users/thomaswatson/Desktop/Downloads/Pokemon Essentials v8 2012-07-10/Graphics/Battlebacks/enemybaseFieldSandEve.png")
img = pygame.transform.scale(img, (128, 64))

while running: #loop while we are still running
	for event in pygame.event.get(): #process events
		if event.type == QUIT: #if we're being told to quit
			running = False #stop running
			break #and stop processing events
		elif event.type == KEYDOWN: #if a key has been pressed
			if event.key == K_ESCAPE: #if it's one we care about
				running = False
			elif event.key == ord("r"):
				anim = animation.PartAnimationSet(None, sys.argv[1])
				anim.set_animation(sys.argv[2])
				if stepping:
					anim_dest.fill((255, 255, 255))
					anim.update()
			elif event.key == ord("s"): #if it's to toggle stepping
				stepping = not stepping
			elif event.key == ord("n"): #if it's to step to the next frame
				if stepping:
					anim.update()
	if running == False: #if we aren't supposed to be running any more
		break #stop running
	if not stepping:
		anim.update()
	glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
	anim.render(130, 100)
	#pygame.transform.scale(anim_dest, (settings.screen_x*settings.screen_scale, \
	#	settings.screen_y*settings.screen_scale), screen) #draw the screen scaled properly
	pygame.display.flip() #flip double buffers
	clock.tick(30)