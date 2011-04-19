import sys
import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo

import Image
import numpy as np

class Viewer:
	refresh = 40
	
	def __init__(self, name, width, height):
		self.width = width
		self.height = height
		self.name = name
		self.fullscreen = False
	
	def init(self):
		glClearColor(0,0,0,0)
		glEnable(GL_DEPTH_TEST)
		glShadeModel(GL_SMOOTH)
		self.last = glutGet(GLUT_ELAPSED_TIME)
	
	def can_refresh(self):
	 	delta = glutGet(GLUT_ELAPSED_TIME) - self.last
		ok = delta >= self.refresh
		if ok: self.last += delta
		return ok
	
	def reshape(self, w, h):
		glViewport(0,0,w,h)
	
	def display(self):
		pass
	
	def idle(self):
		pass
	
	def keyboard(self, key, x, y):
		if key == 'f':
			if self.fullscreen:
				glutReshapeWindow(self.width, self.height)
			else:
				glutFullScreen()
			self.fullscreen = not self.fullscreen
		if key == 'w':
			self.camera.rotate_object([1,0,0], -5.0)
		if key == 's':
			self.camera.rotate_object([1,0,0], 5.0)
		if key == 'a':
			self.camera.rotate_object([0,1,0], -5.0)
		if key == 'd':
			self.camera.rotate_object([0,1,0], 5.0)
	
	def resources(self):
		pass
	
	def run(self):
		glutInit(sys.argv)
		glutInitWindowSize(self.width, self.height)
		glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
		window = glutCreateWindow(self.name)
		
		glutDisplayFunc(self.display)
		glutIdleFunc(self.idle)
		glutReshapeFunc(self.reshape)
		glutKeyboardFunc(self.keyboard)
		
		self.init()
		self.resources()
		
		glutMainLoop()


class Object:
	def __init__(self):
		self.m = self.identity()
	
	def identity(self):
		return np.matrix(np.identity(4, 'f'))
	
	def modelworld(self):
		return self.m
	
	def modelworld_n(self):
		return np.linalg.inv(self.m).T
	
	def origin(self):
		return self.m * np.matrix([0,0,0,0]).T
	
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
			[0, z, -y, 0],
			[-z, 0, x, 0],
			[y, -x, 0, 0],
			[0,0,0,0]
		])
		return np.matrix(rot, 'f')


# Objects
class Model(Object):
	def __init__(self, vertices, elements=None, colors=None, normals=None):
		self.vertices_index = vbo.VBO(np.asarray(vertices, 'f'))
		if elements:
			self.elements_index = vbo.VBO(np.asarray(elements, 'f'))
		if colors:
			self.colors_index = vbo.VBO(np.asarray(colors, 'f'))
		if normals:
			self.normals_index = vbo.VBO(np.asarray(normals, 'f'))
		self.m = self.identity()
	
	def draw(self):
		pass


class Camera(Object):
	def __init__(self, angle, aspect, near, far):
		self.angle = math.radians(angle)
		self.aspect = aspect
		self.near = near
		self.far = far
		self.update_projection()
		self.m = self.identity()
	
	def worldcamera(self):
		try:
			return np.linalg.inv(self.m)
		except np.linalg.LinAlgError:
			print "Cannot inverse matrix"
	
	def worldcamera_n(self):
		return self.m.T
	
	def update_projection(self):
		n = self.near
		f = self.far
		t = n * math.tan(self.angle / 2)
		r = t * self.aspect
		
		fx = n/r
		fy = n/r
		fz = -(f+n)/(f-n)
		fw = -2.*f*n/(f-n)
		
		self.proj =  np.matrix([
			[fx, 0, 0, 0],
			[0, fy, 0, 0],
			[0, 0, fz, fw],
			[0, 0, -1, 0]
		])
	

# Textures
class Texture:
	tex = [GL_TEXTURE0, GL_TEXTURE1]
	
	def __init__(self, filename):
		self.filename = filename
		self.im, self.width, self.height = self.read()
		self.name = self.generate()
		self.type = GL_TEXTURE_2D
	
	def read(self, filename=None):
		fname = filename or self.filename
		im = Image.open(fname)
		w, h = im.size
		return np.asarray(im), w, h
	
	def generate(self):
		tex = glGenTextures(1)
		glBindTexture(self.type, tex)
		glTexParameteri(self.type, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
		glTexParameteri(self.type, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
		glTexParameteri(self.type, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
		glTexParameteri(self.type, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
		glTexImage2D(self.type, 0, GL_RGB8, self.width, self.height, 0, GL_BGR, GL_UNSIGNED_BYTE, self.im)
		return tex
	
	def bind(self, n):
		glActiveTexture(self.tex[n])
		glBindTexture(self.type, self.name)


class Cubemap(Texture):
	tex = [
		GL_TEXTURE_CUBE_MAP_POSITIVE_X,
		GL_TEXTURE_CUBE_MAP_NEGATIVE_X,
		GL_TEXTURE_CUBE_MAP_POSITIVE_Y,
		GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
		GL_TEXTURE_CUBE_MAP_POSITIVE_Z,
		GL_TEXTURE_CUBE_MAP_NEGATIVE_Z
	]
	
	def __init__(self, folder):
		self.type = GL_TEXTURE_CUBE_MAP
		self.index = self.load(folder, format)
	
	def bind(self):
		glBindTexture(self.type, self.index)
	
	def unbind(self):
		glBindTexture(self.type, 0)
	
	def load(self, folder, format):
		glEnable(GL_TEXTURE_CUBE_MAP)
		index = glGenTextures(1)
		glBindTexture(self.type, index)
		
		for i in range(6):
			im, w, h = self.read('%s/map%s.bmp' % (folder, i))
			glTexImage2D(self.tex[i], 0, 3, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, im)
		
		glTexParameteri(self.type, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameteri(self.type, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexParameterf(self.type, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
		glTexParameterf(self.type, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
		return index


# Shaders
class Shader:
	def __init__(self, vs_fname, fs_fname, uniforms=[], attributes=[]):
		self.vs = self.compile(GL_VERTEX_SHADER, vs_fname)
		self.fs = self.compile(GL_FRAGMENT_SHADER, fs_fname)
		self.program = self.make_program()
		self.uniforms = {}
		self.save_locations(uniforms + ['modelworld', 'worldcamera', 'projection', 'modelworld_n', 'worldcamera_n'], attributes)
	
	def compile(self, target, fname):
		source = open(fname).read()
		shader = glCreateShader(target)
		glShaderSource(shader, source)
		glCompileShader(shader)
		if not self.check_compile(shader):
			print "Failed to compile %s: %s" % (target, fname)
			return 0
		return shader
	
	def make_program(self):
		p = glCreateProgram()
		glAttachShader(p, self.vs)
		glAttachShader(p, self.fs)
		glBindAttribLocation(p, 0, "position")
		glLinkProgram(p)
		if not self.check_link(p):
			print "Failed to link shader program"
			return 0
		return p
	
	def check_compile(self, shader):
		status = glGetShaderiv(shader, GL_COMPILE_STATUS, None)
		if not status:
			glDeleteShader(shader)
		return status
	
	def check_link(self, program):
		status = glGetProgramiv(program, GL_LINK_STATUS, None)
		if not status:
			glDeleteProgram(program)
		return status
	
	def save_locations(self, uniforms, attributes):
		for u in uniforms:
			self.uniforms[u] = glGetUniformLocation(self.program, u)
		for a in attributes:
			self.attributes[a] = glGetAttribLocation(self.program, a)
	
	def set_uniform(self, func, name, value):
		func(self.uniforms[name], value)
	
	def set_matrices(self, model, camera):
		self.set_matrix4('modelworld', model.modelworld())
		self.set_matrix4('worldcamera', camera.worldcamera(), False)
		self.set_matrix4('projection', camera.proj)
		self.set_matrix3('modelworld_n', model.modelworld_n())
		self.set_matrix3('worldcamera_n', camera.worldcamera_n(), False)
	
	def set_matrix4(self, name, mat, rowmajor=True):
		rowm = GL_TRUE if rowmajor else GL_FALSE
		mat = np.matrix(mat, 'f')
		glUniformMatrix4fv(self.uniforms[name], 1, rowm, mat)
	
	def set_matrix3(self, name, mat, rowmajor=True):
		rowm = GL_TRUE if rowmajor else GL_FALSE
		mat = np.matrix(mat, 'f')
		glUniformMatrix3fv(self.uniforms[name], 1, rowm, mat)
	
	def set_vector3(self, name, v):
		v = np.array(v, 'f')
		glUniform3f(self.uniforms[name], v[0], v[1], v[2])
	
	def use(self):
		glUseProgram(self.program)
	
	def unuse(self):
		glUseProgram(0)
