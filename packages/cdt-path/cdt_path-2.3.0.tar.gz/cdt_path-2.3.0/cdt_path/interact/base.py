import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.backend_bases import MouseButton
from cdt_path.pathplan import *
from . import border
class Interact:
	def __init__(self, ax, triang, title=True, poly=True):
		self.ax = ax
		self.triang = triang
		self.trifinder = triang.get_trifinder()
		self.poly = poly
		
		self._click_state=0
		self._start_point=None
		self._end_point=None
		
		with mpl.rc_context({'lines.linewidth':2, 'lines.linestyle': ':'}):
			plt.triplot(triang)
			
		self.polygon = Polygon([[0, 0], [0, 0]], facecolor='#ADD8E6',alpha = 0.6)  # dummy data for (xs, ys)
		self.update_selected_tri(-1)
		ax.add_patch(self.polygon)
		fig = plt.gcf()
		if title == True:
			fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move_t)
		else:
			if title:
				ax.set_title(title)
			fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move_wt)

		plt.connect('button_press_event', self.on_click)
		ax.axes.set_aspect('equal')
		ax.axis("off")
		plt.show()
		
	def update_selected_tri(self, tri):
		if tri == -1:
			points = [0, 0, 0]
		else:
			points = self.triang.triangles[tri]
		xs = self.triang.x[points]
		ys = self.triang.y[points]
		self.polygon.set_xy(np.column_stack([xs, ys]))

	def on_mouse_move_wt(self, event):
		if event.inaxes is None:
			tri = -1
		else:
			tri = self.trifinder(event.xdata, event.ydata)
		self.update_selected_tri(tri)
		event.canvas.draw()
		
	def on_mouse_move_t(self, event):
		if event.inaxes is None:
			tri = -1
		else:
			tri = self.trifinder(event.xdata, event.ydata)
		self.update_selected_tri(tri)
		self.ax.set_title(f'In triangle {tri}')
		event.canvas.draw()
		
	def update_path(self, start_point, goal_point):
		start = int(self.trifinder(*start_point))
		goal = int(self.trifinder(*goal_point))
		
		# 使用 A* 算法搜索路径
		came_from, _ = a_star_search_G(self.triang, start, goal)
		path_indices = self._backtrack_path(came_from, start, goal)
		
		left_indices, right_indices, directions = tri_to_funnel_plus(self.triang, start, path_indices)
		left_indices.reverse()
		
		# 构建左右边界点集
		right_points = self._get_points(self.triang, right_indices)
		right_points = np.concatenate((right_points, [goal_point]))
		
		left_points = self._get_points(self.triang, left_indices)
		
		if self.poly:
			polygon_points = np.concatenate(([start_point], right_points, left_points))
			self.polygon2 = Polygon(polygon_points, closed=True, facecolor='#80FF00', alpha=0.6)
			self.ax.add_patch(self.polygon2)
		
		left_points = np.concatenate((left_points[::-1], [goal_point]))
		optimized_path = funnel(start_point, left_points, right_points, directions)
		optimized_path = [start_point] + optimized_path + [goal_point]
		
		optimized_path_np = np.array(optimized_path)
		plt.plot(optimized_path_np[:, 0], optimized_path_np[:, 1], lw=3)

	def _backtrack_path(self, came_from, start, goal):
		path = [goal]
		current = came_from[goal]
		while current != start:
			path.append(current)
			current = came_from[current]
		return path

	def _get_points(self, triang, indices):
		x = triang.x[indices]
		y = triang.y[indices]
		return np.column_stack((x, y))

	def on_click(self, event):
		if event.inaxes is None or self.trifinder(event.xdata, event.ydata) == -1:
			return
		if event.button is MouseButton.LEFT:
			if self._click_state==0:
				self._start_point=(event.xdata, event.ydata)
				self._start_point_in_axes = self.ax.scatter(event.xdata, event.ydata, color='k', marker='*')
				self._click_state+=1
				
			elif self._click_state==1:
				self._end_point=(event.xdata, event.ydata)
				self._start_point_in_axes.remove()
				if self.trifinder(*self._start_point) == self.trifinder(*self._end_point):
					self._click_state==0
					return
				self.update_path(np.array(self._start_point), np.array(self._end_point))
				self._click_state+=1
			elif self._click_state ==2:
				if self.poly:
					self.polygon2.set_visible(False)

				self._click_state=0
				