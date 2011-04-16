import sys

import OpenGL
OpenGL.ERROR_ON_COPY = True
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo

import Image
import numpy as np


class Viewer:
	def __init__(self):
		pass
	
	def init(self, w, h):
		glClearColor(0,0,0,0)
		glClearDepth(1.0)
		glDepthFunc(GL_LESS)
		glEnable(GL_DEPTH_TEST)
		glShadeModel(GL_SMOOTH)
		
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(45.0, float(w)/float(h), 0.1, 100.0)
		glMatrixMode(GL_MODELVIEW)
	
	def reshape(self, w, h):
		glViewport(0,0,w,h)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(45.0, float(w)/float(h), 0.1, 100.0)
		glMatrixMode(GL_MODELVIEW)
		
	
	def display(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		glUseProgram(self.shader.program)
		
		self.vbo.bind()
		glEnableClientState(GL_VERTEX_ARRAY)
		glVertexPointerf(self.vbo)
		glDrawArrays(GL_TRIANGLES, 0, 3)
		
		glutSwapBuffers()
	
	def idle(self):
		pass
	
	def resources(self):
		self.object = Object(
			vertices=[-1.0, -1.0,  1.0, -1.0,  -1.0, 1.0,  1.0, 1.0],
			# colors=[1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0]
		)
		# # self.textures = [Texture('tex1.jpg'), Texture('tex2.jpg')]
		self.shader = Shader('hello.vs', 'hello.fs')
		print 'resources'
		# self.vs = compileShader(open('hello.vs').read(), GL_VERTEX_SHADER)
		# self.fs = compileShader(open('hello.fs').read(), GL_FRAGMENT_SHADER)
		# self.shader = compileProgram(self.vs, self.fs)
		self.vbo = vbo.VBO(np.array([
			[0.0, 1.0, 0.0],
			[-1.0,-1.0, 0.0],
			[1.0,-1.0, 0.0]
		], 'f'))
	
	def run(self):
		glutInit(sys.argv)
		glutInitWindowSize(640, 480)
		glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
		window = glutCreateWindow('Hello')

		glutDisplayFunc(self.display)
		glutIdleFunc(self.display)
		glutReshapeFunc(self.reshape)
		
		self.init(640, 480)
		self.resources()
		
		glutMainLoop()
	

# Objects
class Object:
	def __init__(self, vertices, elements=None, colors=None, normals=None):
		self.vertices_index = self.buffer(GL_ARRAY_BUFFER, np.asarray(vertices))
		# self.vertices_index = self.gen_vertices(np.asarray(vertices))
		# self.elements_index = self.buffer(GL_ELEMENT_ARRAY_BUFFER, np.asarray(elements))
		# self.colors_index = self.buffer(GL_ARRAY_BUFFER, np.asarray(colors))
		# self.normals_index = self.buffer(GL_ARRAY_BUFFER, np.asarray(normals))
	
	def buffer(self, target, data):
		if not data.size: return None
		buf = glGenBuffers(1)
		glBindBuffer(target, buf)
		glBufferData(target, ADT.arrayByteCount(data), ADT.voidDataPointer(data), GL_STATIC_DRAW)
		glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)
		glEnableVertexAttribArray(0)
		return buf
	
	def gen_vertices(self, data):
		a = glGenBuffers(1)
		glBindBuffer(GL_ARRAY_BUFFER, a)
		glBufferData(GL_ARRAY_BUFFER, data, GL_STATIC_DRAW)
		glVertexPointer(4, GL_FLOAT, 0, None)
		glBindBuffer(GL_ARRAY_BUFFER, a)
		glEnableClientState(GL_VERTEX_ARRAY)


# Textures
class Texture:
	tex = [GL_TEXTURE0, GL_TEXTURE1]
	
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
	
	def bind(self, n):
		glActiveTexture(self.tex[n])
		glBindTexture(GL_TEXTURE_2D, self.name)


# Shaders
class Shader:
	def __init__(self, vs_fname, fs_fname):
		self.vs = self.compile(GL_VERTEX_SHADER, vs_fname)
		self.fs = self.compile(GL_FRAGMENT_SHADER, fs_fname)
		self.program = self.make_program()
	
	def compile(self, target, fname):
		source = open(fname).read()
		shader = glCreateShader(target)
		glShaderSource(shader, source)
		glCompileShader(shader)
		if not self.check_compile(shader): return 0
		return shader
		
	def make_program(self):
		p = glCreateProgram()
		glAttachShader(p, self.vs)
		glAttachShader(p, self.fs)
		glBindAttribLocation(p, 0, "position")
		glLinkProgram(p)
		if not self.check_link(p): return 0
		return p
	
	def check_compile(self, shader):
		status = glGetShaderiv(shader, GL_COMPILE_STATUS, None)
		if not status:
			print "Failed to compile shader: %s" % fname
			glDeleteShader(shader)
		return status
	
	def check_link(self, program):
		status = glGetProgramiv(program, GL_LINK_STATUS, None)
		if not status:
			print "Failed to link shader program"
		return status
	
	def save_locations(self):
		return
		self.uniforms = {
			'fade_factor': glGetUniformLocation(self.program, 'fade_factor'),
			'texture[0]': glGetUniformLocation(self.program, 'texture[0]'),
			'texture[1]': glGetUniformLocation(self.program, 'texture[1]')
		}
		self.attributes = {
			'position': glGetAttribLocation(self.program, 'position')
		}
	
	def set_uniform(self, name, value, type='f'):
		if type == 'f':
			glUniform1f(self.uniforms[name], value)
		elif type == 'i':
			glUniform1i(self.uniforms[name], value)
	
