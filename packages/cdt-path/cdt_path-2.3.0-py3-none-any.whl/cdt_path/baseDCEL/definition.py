class Vertex:  
	def __init__(self, x, y):  
		self.x = x  
		self.y = y  
		self.leaving_edge = None  # 出边  
		
	def incident_edges(self):
		if self.leaving_edge==None:
			return None
		twin_edge=self.leaving_edge.twin
		L=[]
		while twin_edge:
			edge=twin_edge.next
			L.append(edge)
			if edge == self.leaving_edge:
				break
			twin_edge=edge.twin
		return L
		
	def neighbor(self):
		if self.leaving_edge==None:
			return None
		twin_edge=self.leaving_edge.twin
		L_n=[]
		while twin_edge:
			L.append(edge.origin)
			edge=twin_edge.next
			if edge == self.leaving_edge:
				break
			twin_edge=edge.twin
		return L
		
  
#此处Edge即为单向边
#Half-Edge or Directed Edge
class Edge:  
	def __init__(self, origin, twin=None, face=None, next=None, prev=None):  
		self.origin = origin  # 边的起始顶点  
		self.twin = twin  # 反向边  
		self.face = face  # 相邻的面  
		self.next = next  # 下一条从同一顶点出发的边  
		self.prev = prev  # 上一条从同一顶点出发的边  
		
		origin.leaving_edge=self
		
		
#双向边
#Bidirectional Edge or Undirected Edge
#
class BEdge:  
	def __init__(self, v1, v2, face=None, next=None, prev=None):  
		self.origin = origin  # 边的起始顶点  
		self.next = next  # 下一条从同一顶点出发的边  
		self.prev = prev  # 上一条从同一顶点出发的边  
		
		origin.leaving_edge=self
  
class Face:  
	def __init__(self, edge=None):  
		self.edge = edge  # 围绕该面的任意一条边  
		self.inside = None  # 可用于存储面内部的点或其他数据  
  
class DCEL:  
	def __init__(self):  
		self.vertices = {}  # 顶点集合  
		self.edges = {}  # 边集合  
		self.faces = {}  # 面集合  
  
	def add_vertex(self, x, y):  
		vertex = Vertex(x, y)  
		self.vertices[(x, y)] = vertex  
		return vertex  
  
	def add_edge(self, v1, v2, face=None, next_edge1=None, prev_edge1=None, next_edge2=None, prev_edge2=None):  
		edge1 = Edge(v1, None, face, next_edge1, prev_edge1)
		edge2 = Edge(v2, edge1, face, next_edge2, prev_edge2)
		edge1.twin_edge=edge2
		self.edges[id(edge1)] = edge1
		self.edges[id(edge2)] = edge2
		return edge1, edge2
		
	def add_half_edge(self, origin_vertex, twin_edge=None, face=None, next_edge=None, prev_edge=None):
		edge = Edge(origin_vertex, twin_edge, face, next_edge, prev_edge)  
		self.edges[id(edge)] = edge  
		return edge  
  
	def add_face(self, edge):  
		face = Face(edge)  
		self.faces[id(face)] = face  
		return face  
  
	# 更多的方法可以在这里添加，例如连接顶点、边和面，或者搜索、遍历等
	def incident_edges(self, vertex):
		return vertex.incident_edges()
		