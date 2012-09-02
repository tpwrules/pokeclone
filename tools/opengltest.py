from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import math


def resize((width, height)):
    if height==0:
        height=1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    #gluPerspective(45, 1.0*width/height, 0.1, 100.0)
    gluOrtho2D(0, width, 0, height)
    glScalef(1, -1, 1)
    glTranslatef(0, -height, 0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()

def init():
    global tex
    glEnable(GL_TEXTURE_2D)
    surf = pygame.image.load("../data/item086.png")
    surfdata = pygame.image.tostring(surf, "RGBA", True)
    glBindTexture(GL_TEXTURE_2D, tex)
    print tex
    glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, surf.get_width(), surf.get_height(), 0,
                  GL_RGBA, GL_UNSIGNED_BYTE, surfdata )
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glShadeModel(GL_SMOOTH)
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glEnable(GL_BLEND);

def draw(child=False):
    global rot
    if not child:
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glPopMatrix()
        glPushMatrix()

        glTranslatef(320, 240, 0)

        glRotatef(math.radians(rot), 0, 0, 1)

        #glTranslatef(0, 35, 0)

    if child:
        glTranslatef(70+35, 70, 0)
        glRotatef(math.radians(rot), 0, 0, 1)
        glTranslatef(-35, 0, 0)

    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex2f(0, 70)
    glTexCoord2f(1.0, 0.0)
    glVertex2f(70, 70)
    glTexCoord2f(1.0, 1.0)
    glVertex2f(70, 0)
    glTexCoord2f(0.0, 1.0)
    glVertex2f(0, 0)
    glEnd()
    if not child:
        draw(True)

rot = 0

tex = 0

def main():
    global rot, tex
    video_flags = OPENGL|DOUBLEBUF
    
    pygame.init()
    pygame.display.set_mode((640,480), video_flags)

    resize((640,480))
    init()

    frames = 0
    ticks = pygame.time.get_ticks()



    while 1:
        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break
        
        draw()
        rot += 20
        pygame.display.flip()
        frames = frames+1

    print "fps:  %d" % ((frames*1000)/(pygame.time.get_ticks()-ticks))


if __name__ == '__main__': main()
