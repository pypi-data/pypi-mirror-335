def tri_to_funnel(triang, start, L):
	triangles = triang.triangles
	neighbors = triang.neighbors
	Ll=[]
	Lr=[]
	current = start
	if L:
		next = L.pop()
		for i in range(3):
			if neighbors[current][i] == next:
				Lr.append(triangles[current][i])
				Ll.append(triangles[current][(i+1)%3])
				current=next
				break
				
	while L:
		next = L.pop()
		for i in range(3):
			if neighbors[current][i] == next:
				if Lr[-1]==triangles[current][i]:
					Ll.append(triangles[current][(i+1)%3])
				else:
					Lr.append(triangles[current][i])
					
				current=next
				break
				
	return Ll, Lr
				
def tri_to_funnel_plus(triang, start, L):
	triangles = triang.triangles
	neighbors = triang.neighbors
	Ll=[]
	Lr=[]
	Li=[0] *(len(L)-1)
	j=0
	if L:
		next = L.pop()
		for i in range(3):
			if neighbors[start][i] == next:
				Lr.append(triangles[start][i])
				Ll.append(triangles[start][(i+1)%3])
				current=next
				break
				
	while L:
		next = L.pop()
		for i in range(3):
			if neighbors[current][i] == next:
				if Lr[-1]==triangles[current][i]:
					Ll.append(triangles[current][(i+1)%3])
				else:
					Lr.append(triangles[current][i])
					Li[j]=1
				current=next
				j+=1
				break
				
	return Ll, Lr, Li
	
from .funnel import funnel
def tri_and_funnel(triang, start, L):
	Ll, Lr, Li = tri_to_funnel_plus(triang, start, L)
	pass
	
def path(triang, start_point, goal_point):
	a_star_P(triang, start_point, goal_point, start=None, goal=None)