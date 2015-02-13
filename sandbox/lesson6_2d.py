#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# This code was created by Richard Campbell '99 (ported to Python/PyOpenGL by John Ferguson 2000)
#
# The port was based on the lesson5 tutorial module by Tony Colston (tonetheman@hotmail.com).  
#
# If you've found this code useful, please let me know (email John Ferguson at hakuin@voicenet.com).
#
# See original source and C based tutorial at http:#nehe.gamedev.net
#
# Note:
# -----
# Now, I assume you've read the prior tutorial notes and know the deal here.  The one major, new requirement
# is to have a working version of PIL (Python Image Library) on your machine.
#
# General Users:
# --------------
# I think to use textures at all you need Nunmeric Python, I tried without it and BAM Python didn't "like" the texture API.
#
# Win32 Users:
# ------------
# Well, here's the install I used to get it working:
# [1] py152.exe - include the TCL install!
# [2] PyOpenGL.EXE - probably the latest, the Vaults notes should give you a clue.
# [3] Distutils-0.9.win32.exe for step #4
# [4] Numerical-15.3.tgz - run the setup.py (need VC++ on your machine, otherwise, have fun with #3, it looks fixable to use gCC).
#
# Win98 users (yes Win98, I have Mandrake on the other partition okay?), you need to the Tcl bin directory in your PATH, not PYTHONPATH,
# just the DOS PATH.
#
# BTW, since this is Python make sure you use tabs or spaces to indent, I had numerous problems since I 
# was using editors that were not sensitive to Python.
#
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import Image
import numpy as np

# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'

# Number of the glut window.
window = 0

# Rotations for cube. 
yrot = 0.0

texture = 0

def LoadTextures():
    #global texture
    array_red = (np.random.rand(640,480)*255).astype(np.uint8)
    array_blue = (np.random.rand(640,480)*255).astype(np.uint8)
    array_green =  (np.random.rand(640,480)*255).astype(np.uint8)
    array_alpha = np.ones((640,480),dtype=np.uint8)*255
    array = np.dstack((array_red, array_blue, array_green, array_alpha))
    
    image = array.tostring()
    ix = array_red.shape[0]
    iy = array_red.shape[1]
	
    # Create Texture
    glGenTextures(1, texture) # generate one texture name
    glBindTexture(GL_TEXTURE_2D, texture) # bind a 2d texture to the generated name
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

# A general OpenGL initialization function.  Sets all of the initial parameters. 
def InitGL(Width, Height): # We call this right after our OpenGL window is created.
    LoadTextures()
    glEnable(GL_TEXTURE_2D)
    glClearColor(0.0, 0.0, 0.0, 0.0) # This Will Clear The Background Color To Black
    #glClearDepth(1.0) # Enables Clearing Of The Depth Buffer
    #glDepthFunc(GL_LESS) # The Type Of Depth Test To Do
    glDisable(GL_DEPTH_TEST) # 2D means no depth !
    glShadeModel(GL_SMOOTH) # Enables Smooth Color Shading
	
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity() # Reset The Projection Matrix

    glOrtho (0, Width, Height, 0, 0, 1) # use this to have coordinates in window pixels

    glMatrixMode(GL_MODELVIEW)

# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene(Width, Height):
    if Height == 0: # Prevent A Divide By Zero If The Window Is Too Small 
	    Height = 1

    glViewport(0, 0, Width, Height) # Reset The Current Viewport And Perspective Transformation
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho (0, Width, Height, 0, 0, 1) # use this to have coordinates in window pixels
    glMatrixMode(GL_MODELVIEW)

# The main drawing function. 
def DrawGLScene():
	global texture, yrot

	#array = np.random.rand(1, 480)
	#image = array.tostring()
	array_red = (np.random.rand(1,480)*255).astype(np.uint8)
	array_blue = (np.random.rand(1,480)*255).astype(np.uint8)
	array_green =  (np.random.rand(1,480)*255).astype(np.uint8)
	array_alpha = np.ones((1,480),dtype=np.uint8)*255
	array = np.dstack((array_red, array_blue, array_green, array_alpha))
	image = array.tostring()
	
	glTexSubImage2D(GL_TEXTURE_2D, 0, yrot, 0, 1, 480, GL_RGBA, GL_UNSIGNED_BYTE, image)

	glLoadIdentity() # Reset The View

	glBegin(GL_QUADS) # Start Drawing The Cube
	
	# note that the texture's corners have to match the quad's corners
	glTexCoord2f(0.0, 0.0); glVertex2f(0, 0) # Bottom Left Of The Texture and Quad
	glTexCoord2f(1.0, 0.0); glVertex2f(640, 0) # Bottom Right Of The Texture and Quad
	glTexCoord2f(1.0, 1.0); glVertex2f(640,  480) # Top Right Of The Texture and Quad
	glTexCoord2f(0.0, 1.0); glVertex2f(0,  480) # Top Left Of The Texture and Quad

	glEnd() # Done Drawing The Rectangle
	
	yrot = (yrot + 1)%640

	# since this is double buffered, swap the buffers to display what just got drawn. 
	glutSwapBuffers()

# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)  
def keyPressed(*args):
	# If escape is pressed, kill everything.
    if args[0] == ESCAPE:
	    glutDestroyWindow(window)
	    sys.exit(0)

def main():
	global window
	# For now we just pass glutInit one empty argument. I wasn't sure what should or could be passed in (tuple, list, ...)
	# Once I find out the right stuff based on reading the PyOpenGL source, I'll address this.
	glutInit("")

	# Select type of Display mode:   
	#  Double buffer 
	#  RGBA color
	# Alpha components supported 
	# Depth buffer
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
	
	# get a 640 x 480 window 
	glutInitWindowSize(640, 480)
	
	# the window starts at the upper left corner of the screen 
	glutInitWindowPosition(0, 0)
	
	# Okay, like the C version we retain the window id to use when closing, but for those of you new
	# to Python (like myself), remember this assignment would make the variable local and not global
	# if it weren't for the global declaration at the start of main.
	window = glutCreateWindow("Jeff Molofee's GL Code Tutorial ... NeHe '99")

   	# Register the drawing function with glut, BUT in Python land, at least using PyOpenGL, we need to
	# set the function pointer and invoke a function to actually register the callback, otherwise it
	# would be very much like the C version of the code.	
	glutDisplayFunc(DrawGLScene)
	
	# Uncomment this line to get full screen.
	#glutFullScreen()

	# When we are doing nothing, redraw the scene.
	#glutIdleFunc(DrawGLScene)
	glutIdleFunc(DrawGLScene)
	
	# Register the function called when our window is resized.
	glutReshapeFunc(ReSizeGLScene)
	
	# Register the function called when the keyboard is pressed.  
	glutKeyboardFunc(keyPressed)

	# Initialize our window. 
	InitGL(640, 480)

	# Start Event Processing Engine	
	glutMainLoop()

# Print message to console, and kick off the main to get it rolling.
print("Hit ESC key to quit.")
main()
    	
