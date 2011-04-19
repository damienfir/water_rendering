from gl import *
import numpy as np
import scipy as sp
from scipy import signal


class WaterViewer(Viewer):
	refresh = 20
	
	def display(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		self.shader.use()
		self.shader.set_matrices(self.water, self.camera)
		self.shader.set_vector3('eye', self.camera.origin())
		self.shader.set_vector3('light', self.light.origin())
		
		self.water.draw()
		
		glutSwapBuffers()
	
	def idle(self):
		if self.can_refresh():
			self.water.update_map()
			self.water.make_vertices()
			glutPostRedisplay()
	
	def resources(self):
		self.shader = Shader('shaders/water.vs', 'shaders/water.fs', ['eye', 'light'])
		self.water = Water(40, 40)
		self.camera = Camera(60.0, 3./4., 0.1, 100.0).translate_object([0,1,5]).rotate_object([0,1,0], 20.0)
		self.light = Object().translate_world([0,10,0])
		
		# self.cube = Model(vertices=[
		# 	(-1,-1,-1), (1,-1,-1), (1,-1,1), (-1,-1,1),
		# ])


class Water(Object):
	def __init__(self, rows, cols):
		self.m = self.identity()
		self.rows, self.cols = rows, cols
		self.rc = rows*cols
		self.heights = np.zeros((rows, cols), 'f')
		self.velocities = np.zeros((rows, cols), 'f')
		self.kernel = self.heightmap_kernel()
		self.init_grid()
		self.make_vertices()
	
	def init_grid(self):
		self.heights[int(self.rows/2.),int(self.cols/2.)] = 5
		z, x = np.array(np.meshgrid(range(self.rows), range(self.cols)), 'f')
		x, z = x.ravel(), z.ravel()
		self.v = np.vstack((x, np.zeros_like(x), -z)).T
	
	def heightmap_kernel(self):
		return np.array([
			[0, 1, 0],
			[1, -4, 1],
			[0, 1, 0]
		]) * 0.25
	
	def update_map(self):
		self.velocities += signal.correlate2d(self.heights, self.kernel, mode='same', boundary='symm')
		self.velocities *= 0.99
		self.heights += self.velocities
	
	def make_vertices(self):
		h = self.heights.flatten()
		self.v[:,1] = h
		self.vertices_index = vbo.VBO(np.array(self.v, 'f'))
	
	def draw(self):
		glEnableClientState(GL_VERTEX_ARRAY)
		self.vertices_index.bind()
		glVertexPointerf(self.vertices_index)
		glPointSize(3.0)
		glDrawArrays(GL_POINTS, 0, self.rc)
		
		self.vertices_index.unbind()
		glDisableClientState(GL_VERTEX_ARRAY);


v = WaterViewer('Water vodka', 640, 480)

v.run()