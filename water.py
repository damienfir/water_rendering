from gl import *
import numpy as np
import scipy as sp
from scipy import signal


class WaterViewer(Viewer):
	refresh = 40
	
	def display(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		self.shader.use()
		self.shader.set_matrices(self.water, self.camera)
		self.shader.set_vector3('eye', self.camera.origin())
		self.shader.set_vector3('light', self.light.origin())
		
		self.cubemap.bind()
		
		self.water.draw()
		
		self.cubemap.unbind()
		self.shader.unuse()
		
		glutSwapBuffers()
	
	def idle(self):
		if self.can_refresh():
			self.water.update_map()
			self.water.make_vertices()
			glutPostRedisplay()
	
	def keyboard(self, key, x, y):
		if key == 'b':
			self.water.bump(0,0)
		else:
			super(WaterViewer, self).keyboard(key, x, y)
	
	def resources(self):
		self.shader = Shader('shaders/water.vs', 'shaders/water.fs', ['eye', 'light'])
		self.water = Water(40, 40)
		self.camera = Camera(60.0, 3./4., 0.1, 100.0).translate_object([0,1,5]).rotate_object([0,1,0], 20.0)
		self.light = Object().translate_world([0,10,-100])
		self.cubemap = Cubemap('data/city')


class Water(Object):
	def __init__(self, rows, cols):
		self.m = self.identity()
		self.rows, self.cols = rows, cols
		self.rc = rows*cols
		self.heights = np.zeros((rows, cols), 'f')
		self.velocities = np.zeros((rows, cols), 'f')
		self.kernel = self.heightmap_kernel()
		self.init_grid()
		self.make_triangles()
		self.make_vertices()
	
	def init_grid(self):
		# self.heights[int(self.rows/2.),int(self.cols/2.)] = 5
		x, z = np.array(np.meshgrid(range(self.cols), range(self.rows)), 'f')
		x, z = x.ravel(), z.ravel()
		self.vertices = np.vstack((x, np.zeros_like(x), -z)).T
	
	def heightmap_kernel(self):
		sq2 = 1/math.sqrt(2)
		s = 4*sq2 + 4
		return np.array([
			[sq2, 1, sq2],
			[1, -s, 1],
			[sq2, 1, sq2]
		]) / s
	
	def update_map(self):
		self.velocities += signal.correlate2d(self.heights, self.kernel, mode='same', boundary='symm')
		self.velocities *= 0.99
		self.heights += self.velocities
	
	def make_triangles(self):
		n = (self.rows-1)*(self.cols-1)
		ind = np.zeros(n*6)
		c = self.cols
		base = []
		for i in xrange(self.rows-1):
			for j in xrange(self.cols-1):
				base.append(i*c + j)
		base = np.array(base)
		ind[0::6] = base[:]
		ind[1::6] = base + self.cols
		ind[2::6] = base + 1
		ind[3::6] = base + self.cols
		ind[4::6] = base + self.cols + 1
		ind[5::6] = base + 1
		self.indices = np.array(ind, 'uint32')
	
	def make_vertices(self):
		h = self.heights.flatten()
		self.vertices[:,1] = h
		self.make_normals()
	
	def make_normals(self):
		v = self.vertices
		p = v[self.indices[0::3]]
		q = v[self.indices[1::3]]
		r = v[self.indices[2::3]]
		
		c = np.cross(r-p, q-p)
		norms = np.sqrt((c**2).sum(1))
		c /= norms[:, np.newaxis]
		
		normals = np.zeros((self.rc, 3))
		normals[self.indices[0::6]] += c[0::2]
		normals[self.indices[1::6]] += c[0::2]
		normals[self.indices[2::6]] += c[0::2]
		normals[self.indices[3::6]] += c[1::2]
		normals[self.indices[4::6]] += c[1::2]
		normals[self.indices[5::6]] += c[1::2]
		
		norms = np.sqrt((normals**2).sum(1))
		self.normals = np.array(normals / norms[:, np.newaxis], 'f')
	
	def enable(self):
		glEnableClientState(GL_VERTEX_ARRAY)
		glEnableClientState(GL_NORMAL_ARRAY)
	
	def disable(self):
		glDisableClientState(GL_VERTEX_ARRAY)
		glDisableClientState(GL_NORMAL_ARRAY)		
	
	def draw(self):
		self.enable()
		glVertexPointerf(self.vertices)
		glNormalPointerf(self.normals)
		glDrawElementsui(GL_TRIANGLES, self.indices)
		self.disable()
	
	def bump(self, x, y, a=-1):
		self.velocities[x,y] = a


v = WaterViewer('Water vodka', 640, 480)
v.run()
