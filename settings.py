from pygame.locals import * #import keymap

screen_scale = 2 #scale factor of the screen before displaying
screen_x = 256 #size of screen before scaling
screen_y = 192

keys = [-1, K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT, ord("x")] #array of keys

key_escape = 1 #index into keys array
key_up = 2
key_down = 3
key_left = 4
key_right = 5
key_accept = 6

TILE_NORMAL = 0
TILE_SOLID = 1
TILE_WATER = 2
TILE_WARP = 3
TILE_GRASS = 5
TILE_DOUBLEGRASS = 8