import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import Image
import numpy as np


class Viewer:
	def __init__(self):
		pass
		
	def init(self):
		glClearColor(1,1,1,1)
		glEnable(GL_DEPTH_TEST)
	
	def display(self):
		glUseProgram(self.shader.program)
		glUniform1f(self.shader.uniforms['fade_factor'], self.shader.fade_factor)
		
		glActiveTexture(GL_TEXTURE0)
		glBindTexture(GL_TEXTURE_2D, self.textures[0].name)
		glUniform1i(self.shader.uniforms['textures'][0], 1)
			
		glActiveTexture(GL_TEXTURE1)
		glBindTexture(GL_TEXTURE_2D, self.textures[1].name)
		glUniform1i(self.shader.uniforms['textures'][1], 1)
		
		glBindBuffer(GL_ARRAY_BUFFER, self.object.vertices)
		glVertexAttribPointer(self.shader.uniforms['position'], 2, GL_FLOAT, GL_FALSE, sys.getsizeof(GLfloat)*2, None)
		
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.object.elements)
		glDrawElements(GL_TRIANGLE_STRIP, 4, GL_UNSIGNED_SHORT, None)
		
		glutSwapBuffers()
	
	def idle(self):
		pass
	
	def resources(self):
		self.object = Object([
			-1.0, -1.0,
			1.0, 1.0,
			-1.0, 1.0,
			1.0, 1.0
		], [0, 1, 2, 3])
		self.textures = [Texture('tex1.jpg'), Texture('tex2.jpg')]
		self.shader = Shader('hello.vs', 'hello.fs')
		pass
	
	
	def callbacks(self):
		glutDisplayFunc(self.display)
		glutIdleFunc(self.idle)
	
	
	def run(self):
		glutInit(len(sys.argv), sys.argv)
		glutInitWindowSize(400, 300)
		glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
		glutCreateWindow('Hello')

		self.init()
		self.callbacks()
		
		self.resources()

		glutMainLoop()



# Objects
class Object:
	def __init__(self, vertices, elements):
		self.vertices = self.buffer(GL_ARRAY_BUFFER, np.asarray(vertices), sys.getsizeof(vertices[0]))
		self.elements = self.buffer(GL_ELEMENT_ARRAY_BUFFER, np.asarray(elements), sys.getsizeof(elements[0]))
	
	def buffer(self, target, data, size):
		buf = glGenBuffers(1)
		glBindBuffer(target, buf)
		glBufferData(target, size, data, GL_STATIC_DRAW)
		return buf



# Textures
class Texture:
	def __init__(self, filename):
		self.filename = filename
		self.im = self.read()
		self.name = self.generate()
	
	def read(self):
		im = Image.open(self.filename)
		self.width, self.height = im.size
		return np.asarray(im)
	
	def generate(self):
		tex = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, tex)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8, self.width, self.height, 0, GL_BGR, GL_UNSIGNED_BYTE, self.im)
		return tex



# Shaders
class Shader:
	def __init__(self, vs_fname, fs_fname):
		self.vs = self.compile(GL_VERTEX_SHADER, vs_fname)
		self.fs = self.compile(GL_FRAGMENT_SHADER, fs_fname)
		self.program = self.make_program()
		self.uniforms = self.location()
		self.fade_factor = 0.0
	
	def compile(self, type, fname):
		source = open(fname, 'r').read()
		shader = glCreateShader(type)
		glShaderSource(shader, source)
		glCompileShader(shader)
		
		# check if compilation was ok
		status = 0
		# glGetShaderiv(shader, GL_COMPILE_STATUS, status)
		# if not status:
		# 	print "Failed to compile shader: %s" % fname
		# 	glDeleteShader(shader)
		# 	return 0
		return shader
	
	def make_program(self):
		p = glCreateProgram()
		glAttachShader(p, self.vs)
		glAttachShader(p, self.fs)
		glLinkProgram(p)
		
		# check if link was ok
		# status = 0
		# glGetProgramiv(p, GL_LINK_STATUS, status)
		# if not status:
		# 	print "Failed to link shader program"
		# 
		return p
	
	def location(self):
		return {
			'fade_factor': glGetUniformLocation(self.program, 'fade_factor'),
			'textures': [
				glGetUniformLocation(self.program, 'texture[0]'),
				glGetUniformLocation(self.program, 'texture[1]')
			],
			'position': glGetAttribLocation(self.program, 'position')
		}
