from . import pathplan

from triangle import triangulate as _triangulate
from .interact.base import Interact
from .interact import border
from .manipulate import *
from matplotlib.tri import Triangulation as _Triangulation

def triangulate(tri, opts = 'p'):
	return _triangulate(tri, opts)
	
def Triangulation(tri, opts = 'p'):
	cc = _triangulate(tri, opts)
	return _Triangulation(cc['vertices'][:,0],cc['vertices'][:,1],cc['triangles'])
	
# __all__=["voronoi",'convex_hull','delaunay']