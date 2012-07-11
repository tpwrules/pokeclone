import pygame #import all of pygame
from pygame.locals import *

import time
import sys

modes = [BLEND_RGBA_ADD, BLEND_RGBA_SUB, BLEND_RGBA_MULT, BLEND_RGBA_MIN, BLEND_RGBA_MAX]
mode_num = 0

screen = pygame.display.set_mode((512, 384))

i1 = pygame.image.load(sys.argv[1])
i2 = pygame.image.load(sys.argv[2])

s = pygame.Surface((512, 384), SRCALPHA)

while True:
	s.blit(i1, (0, 0))
	s.blit(i2, (0, 0), special_flags=modes[mode_num])
	screen.blit(s, (0, 0))
	mode_num += 1
	if len(modes) == mode_num:
		mode_num = 0
	pygame.display.update()
	pygame.event.pump()
	time.sleep(0.5)