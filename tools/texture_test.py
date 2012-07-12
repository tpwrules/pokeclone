import pygame #import all of pygame
import pygame.gfxdraw
from pygame.locals import *
import time
import math

def dist(x, y, x2, y2):
	global center
	x *= 1.0
	y *= 1.0
	x2 *= 1.0
	y2 *= 1.0
	return int(math.sqrt(((x-x2)**2)+((y-y2)**2))/1)

screen = pygame.display.set_mode((512, 384))

#pos = [0,0]

i1 = pygame.image.load("oasisbottom.png")
i2 = pygame.image.load("oasistop.png")

iw = i1.get_width()
ih = i1.get_height()

t = pygame.Surface(i1.get_size(), SRCALPHA)
t2 = pygame.Surface((256, 192))

center = (i1.get_width()/2, i1.get_height()/2)
pos = list(center[:])
ks = {}
ks[K_UP] = False
ks[K_DOWN] = False
ks[K_LEFT] = False
ks[K_RIGHT] = False
while True:
	for event in pygame.event.get():
		if event.type == KEYDOWN:
			ks[event.key] = True
		elif event.type == KEYUP:
			ks[event.key] = False
	if ks[K_UP]:
		pos[1] -= 1
	elif ks[K_DOWN]:
		pos[1] += 1
	elif ks[K_LEFT]:
		pos[0] -= 1
	elif ks[K_RIGHT]:
		pos[0] += 1
	xs = dist(pos[0], 0, center[0], 0)
	ys = dist(0, pos[1], 0, center[1])
	t.fill((0, 0, 0, 255))
	pygame.gfxdraw.textured_polygon(t, [(0-xs, 0-ys), (iw-xs, 0-ys), (iw, ih), (0, ih)], i1, 0, 0)
	pygame.gfxdraw.textured_polygon(t, [(0, 0-ys), (iw, 0-ys), (iw-xs, ih), (0-xs, ih)], i2, 0, 0)
	#pygame.gfxdraw.textured_polygon(t, [(0, 0), (64, 0), (64, 64), (0, 64)], i1, 0, 0)
	t2.blit(t, (0, 0), (pos[0]-128, pos[1]-96, 256, 192))
	pygame.transform.scale(t2, (512, 384), screen)
	pygame.display.update()
	time.sleep(1./30)