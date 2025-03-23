from matplotlib.patches import Polygon

def update_polygon(tri):
	global triang
	if tri == -1:
		points = [0, 0, 0]
	else:
		points = triang.triangles[tri]
	xs = triang.x[points]
	ys = triang.y[points]
	polygon.set_xy(np.column_stack([xs, ys]))


def on_mouse_move(event):
	if event.inaxes is None:
		tri = -1
	else:
		tri = trifinder(event.xdata, event.ydata)
	update_polygon(tri)
	ax.set_title(f'In triangle {tri}')
	event.canvas.draw()
	
_click_state=0
_start_point=None
_end_point=None

def on_click(event):
	if event.button is MouseButton.LEFT:
		# print('disconnecting callback')
		# plt.disconnect(binding_id)
		global _click_state
		if _click_state==0:
			_start_point=(event.xdata, event.ydata)
			on_click._start_tri=trifinder(event.xdata, event.ydata)
			_click_state+=1
			
		elif _click_state==1:
			_end_point=(event.xdata, event.ydata)
			on_click._end_tri=trifinder(event.xdata, event.ydata)
			global came_from
			global cost_so_far
			start, goal = on_click._start_tri, on_click._end_tri
			came_from, cost_so_far = pathal.a_star_search_G(triang, start, goal)
			L=[goal]
			val = came_from[goal]
			
			while val != start:
				L.append(val)
				val = came_from[val]
			
			Ll, Lr=pathal.tri_to_funnel(triang, start, L)
			
			Ll.reverse()
			Pr = cc['vertices'][Lr]
			Pl = cc['vertices'][Ll]
			
			points = np.concatenate((start_points, Pr, end_points, Pl))
			
			polygon2 = Polygon(points, closed = True, facecolor='#80FF00',alpha = 0.6)
			ax.add_patch(polygon2)