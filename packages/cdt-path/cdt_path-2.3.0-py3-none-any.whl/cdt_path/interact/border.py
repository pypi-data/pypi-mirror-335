import matplotlib.pyplot as plt
def plot(ax, **kw):
	verts = kw['vertices']
	segs = kw['segments']
	for beg, end in segs:
		x0, y0 = verts[beg, :]
		x1, y1 = verts[end, :]
		ax.plot(
			[x0, x1],
			[y0, y1],
			color='r',
			linewidth=3,
		)
	