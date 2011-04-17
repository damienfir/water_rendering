import sys
import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo

import Image
import numpy as np

import matrix


class Viewer:
	def __init__(self, name, width, height):
		self.width = width
		self.height = height
		self.name = name
	
	def init(self):
		glClearColor(0,0,0,0)
		glEnable(GL_DEPTH_TEST)
	
	def reshape(self, w, h):
		glViewport(0,0,w,h)
	
	def display(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glUseProgram(self.shader.program)
		
		self.shader.set_matrices(self.model, self.camera)
		self.model.draw()
		
		glutSwapBuffers()
	
	def idle(self):
		# glutPostRedisplay()
		pass
	
	def resources(self):
		self.camera = Camera(60, 3./4., 0.1, 100.0)
		self.model = Model(
			vertices=[
				[0.0, 1.0, 0.0],
				[-1.0,-1.0, 0.0],
				[1.0,-1.0, 0.0]
			]
		).translate_world([0,0,-1])
		self.shader = Shader('hello.vs', 'hello.fs')
	
	def run(self):
		glutInit(sys.argv)
		glutInitWindowSize(self.width, self.height)
		glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
		window = glutCreateWindow(self.name)
		
		glutDisplayFunc(self.display)
		glutIdleFunc(self.idle)
		glutReshapeFunc(self.reshape)
		
		self.init()
		self.resources()
		
		glutMainLoop()


class Object:
	def __init__(self):
		self.m = self.identity()
	
	def modelworld(self):
		return self.m
	
	def identity(self):
		return np.matrix(np.identity(4, 'f'))
		
	def scale_world(self, s):
		self.m = self.scale_matrix(s) * self.m
		return self
	
	def scale_object(self, s):
		self.m = self.m * self.scale_matrix(s)
		return self
	
	def translate_world(self, t):
		self.m = self.translation_matrix(t) * self.m
		return self
	
	def translate_object(self, t):
		self.m = self.m * self.translation_matrix(t)
		return self

	def rotate_world(self, axis, angle):
		self.m = self.rotation_matrix(axis, angle) * self.m
		return self
	
	def rotate_object(self, axis, angle):
		r = self.rotation_matrix(axis, angle)
		self.m = self.m * r
		return self
	
	def translation_matrix(self, t):
		a = self.identity()
		a[0, 3] = t[0]
		a[1, 3] = t[1]
		a[2, 3] = t[2]
		return a
	
	def scale_matrix(self, s):
		if isinstance(s, (int, float)):
			s = [s]*3
		a = self.identity()
		a[0, 0] = s[0]
		a[1, 1] = s[1]
		a[2, 2] = s[2]
		return a
	
	def rotation_matrix(self, axis, a):
		a = math.radians(a)
		cosa, sina = math.cos(a), math.sin(a)
		x,y,z = axis
		axis = np.concatenate((np.asarray(axis, 'f'), [0]))
		rot = (cosa * np.identity(4))
		rot += (1-cosa) * np.array([x*axis, y*axis, z*axis, [0,0,0,1]])
		rot += sina * np.array([
			[0, z, -x, 0],
			[-z, 0, x, 0],
			[y, -x, 0, 0],
			[0,0,0,0]
		])
		return np.matrix(rot, 'f')


# Objects
class Model(Object):
	def __init__(self, vertices, elements=None, colors=None, normals=None):
		self.vertices_index = vbo.VBO(np.asarray(vertices, 'f'))
		# self.elements_index = self.buffer(GL_ELEMENT_ARRAY_BUFFER, np.asarray(elements))
		# self.colors_index = self.buffer(GL_ARRAY_BUFFER, np.asarray(colors))
		# self.normals_index = self.buffer(GL_ARRAY_BUFFER, np.asarray(normals))
		self.m = self.identity()
	
	def draw(self):
		glEnableClientState(GL_VERTEX_ARRAY)
		self.vertices_index.bind()
		glVertexPointerf(self.vertices_index)
		
		glDrawArrays(GL_TRIANGLES, 0, 3)
		
		self.vertices_index.unbind()
		glDisableClientState(GL_VERTEX_ARRAY);
		


class Camera(Object):
	def __init__(self, angle, aspect, near, far):
		self.angle = math.radians(angle)
		self.aspect = aspect
		self.near = near
		self.far = far
		self.m = self.identity()
		self.proj = self.projection()
	
	def worldcamera(self):
		return np.linalg.inv(self.m)
	
	def projection(self):
		n = self.near
		f = self.far
		t = n * math.tan(self.angle)
		b = -t
		l = b * self.aspect
		r = t * self.aspect
		fx = 2.*n/(r-l)
		fy = 2.*n*(t-b)
		fz = -(f+n)/(f-n)
		fw = -2.*f*n/(f-n)
		return np.matrix([
			[fx, 0, 0, 0],
			[0, fy, 0, 0],
			[0, 0, fz, fw],
			[0, 0, -1, 0]
		], 'f')
	

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
		self.save_locations()
	
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
			glDeleteProgram(program)
		return status
	
	def save_locations(self):
		self.uniforms = {
			'modelworld': glGetUniformLocation(self.program, 'modelworld'),
			'worldcamera': glGetUniformLocation(self.program, 'worldcamera'),
			'projection': glGetUniformLocation(self.program, 'projection')
		}
	
	def set_uniform(self, func, name, value):
		func(self.uniforms[name], value)
	
	def set_matrices(self, model, camera):
		self.set_matrix('modelworld', model.modelworld())
		self.set_matrix('worldcamera', camera.worldcamera())
		self.set_matrix('projection', camera.proj)
	
	def set_matrix(self, name, mat):
		glUniformMatrix4fv(self.uniforms[name], 1, GL_TRUE, mat)
