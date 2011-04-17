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
		
		glutSwapBuffers()
	
	def idle(self):
		if self.can_refresh():
			self.water.update_map()
			self.water.make_vertices()
			glutPostRedisplay()
	
	def resources(self):
		self.water = Water(50,50)
		self.shader = Shader('water.vs', 'water.fs')
		self.camera = Camera(60, 3./4., 0.1, 100.0)


class Water(Object):
	def __init__(self, rows, cols):
		self.m = self.identity()
		self.rows, self.cols = rows, cols
		self.heights = np.zeros((rows, cols))
		self.velocities = np.zeros((rows, cols))
		self.kernel = self.heightmap_kernel()
		self.init_grid()
	
	def init_grid(self):
		self.heights[int(self.rows/2.),int(self.cols/2.)] = 5
		x = np.ones((self.rows, self.cols))
		self.x = x * np.arange(self.cols)[:,np.newaxis]
		y = np.ones((self.rows, self.cols))
		self.y = y * np.arange(self.rows)[:,np.newaxis]
	
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
		self.vertices = np.dstack((self.x, self.y, self.heights))
		
	
	def draw(self):
		glEnableClientState(GL_VERTEX_ARRAY)
		self.vertices_index.bind()
		glVertexPointerf(self.vertices_index)
		
		glDrawArrays(GL_TRIANGLES, 0, 3)
		
		self.vertices_index.unbind()
		glDisableClientState(GL_VERTEX_ARRAY);


v = WaterViewer('Water vodka', 640, 480)

v.run()