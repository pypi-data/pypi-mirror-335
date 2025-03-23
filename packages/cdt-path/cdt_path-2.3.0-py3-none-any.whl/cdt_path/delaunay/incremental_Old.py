import numpy as np
from ..utils import ToLeft
import matplotlib.pyplot as plt
# import bisect
def Create_DT_incremental(P):
	return Create_DT_incremental_Sorted(P[np.lexsort((P[:, 1], P[:, 0]))])
	
def Create_DT_incremental_Sorted(P):
	l=len(P)
	if l<3 or P[-1][0]==P[0][0]:
		print("Insufficient points to construct Delaunay diagram.")
		return None,None
		
	i=2
	if P[0][0]==P[1][0]:
		while P[0][0]==P[i][0]:
			i+=1
			
		L_ch_i=[0,i-1,i]
		i_xmax=2
	
	else:
		while i<l:
			LogFlag=ToLeft(P[0],P[1],P[i])
			if LogFlag==0:
				i+=1
				continue
			elif LogFlag<0:
				L_ch_i=[0,i,i-1]
				i_xmax=1
				break
			else:
				L_ch_i=[0,i-1,i]
				i_xmax=2
				break
			
		else:
			print("Insufficient points to construct Delaunay diagram.")
			return None,None
		
	#返回点与点之间的关系
	#S_neighbor[0]表示P[0]相邻的点的索引的集合
	S_neighbor=[{1,i}]
	i1=1
	while i1<i-1:
		S_neighbor.append({i1-1,i,i1+1})
		i1+=1
		
	S_neighbor.append({i1-1,i})
	S_neighbor.append(set(range(i)))
	S_neighbor+=[set() for _ in range(l-i-1)]
	#返回线段的Delaunay对应点
	#某一线段，用点索引对来表示
	D_tri={(0,i):[1],(i,0):[1],(0,1):[i],(1,0):[i],(i-1,i):[i-2],(i,i-1):[i-2]}
	D_tri[i,i-1]=[i1]
	for i1 in range(1,i-1):
		D_tri[i1,i1+1]=[i]
		D_tri[i1+1,i1]=[i]
		D_tri[i1,i]=[i1-1,i1+1]
		D_tri[i,i1]=[i1-1,i1+1]
		
	i+=1
	while i<l:
		L_ch_i,i_xmax=add_point_i(P,L_ch_i,S_neighbor,D_tri,i_xmax,i)
		print("Added i:\t",i)
		print("L_ch_i")
		print(L_ch_i)
		print('-------------------')
		# show_ch_i(P,L_ch_i)
		# show(P,D_tri)
		# show_ch_dt(P,L_ch_i,D_tri)
		
		i+=1
		
	return L_ch_i,S_neighbor,D_tri

"""
用集合来实现记录点
"""
	
def add_point_i(P,A,S,D,a1,i_p):
	p=P[i_p]
	if ToLeft(p,P[A[a1-1]],P[A[a1]])>=0:
		a2=a1-len(A)+1
	else:
		a2=a1-len(A)
		while ToLeft(p,P[A[a1-1]],P[A[a1]])<0:
			a1-=1
			
	while ToLeft(p,P[A[a2]],P[A[a2+1]])<0:
		a2+=1
			
	b1=a1-len(A)
	b2=a2
	L_i=[A[a1]]
	N=[]
	# print("b1",b1)
	# print("b2",b2)
	while b2>b1:
		N.append(A[b2])
		b2-=1
		
	# find_border(P,S,D,N,L_i,i_b,i_p)
	print("N:",N)
	print("A:",A)
	find_border_while(P,S,D,N,L_i,A[a1],i_p)
	print("add_edge\tL_i",L_i)
	add_edge(S,D,L_i,i_p)
	print("After add_edge\tD",D)
	if a2==0:
		return A[:a1+1]+[i_p],a1+1
	return A[:a1+1]+[i_p]+A[a2:],a1+1

#N是一个列表，实际使用类似栈，记录着每个要进行in_circle操作的点的P中索引
#L_i返回，原始集合P[:i_p]应该与p相连的点的P中索引
def find_border_rec(P,S,D,N,L_i,i_b,i_p):
	if not N or (i_b,N[-1]) not in D:
		return
	i_d=D[i_b,N[-1]][0]
	if in_circle_bcd(P,i_p,i_b,N[-1],i_d):
		S[i_b].discard(N[-1])
		S[N[-1]].discard(i_b)
		del D[i_b,N[-1]]
		del D[N[-1],i_b]
		N.append(i_d)
		find_border(P,S,D,N,L_i,i_b,i_p)
		
	else:
		L_i.append(i_b)
		find_border(P,S,D,N,L_i,N.pop(),i_p)
	
def find_border_while(P,S,D,N,L_i,i_b,i_p):
	print("def find_border_while():")
	print("\tD:",D)
	while N:
		if (i_b,N[-1]) not in D:
			print(f"({i_b},{N[-1]}) not in D")
			print("\tL_i:",L_i)
			print("\tN:",N)
		if (i_b,N[-1]) in D and D[i_b,N[-1]]:
			i_d=D[i_b,N[-1]][0]
			print("\tin_circle_bcd():",in_circle_bcd(P,i_p,i_b,N[-1],i_d))
			if in_circle_bcd(P,i_p,i_b,N[-1],i_d):
				S[i_b].discard(N[-1])
				S[N[-1]].discard(i_b)
				del D[i_b,N[-1]]
				del D[N[-1],i_b]
				D[i_d,i_b].remove(N[-1])
				D[i_b,i_d].remove(N[-1])
				print(f"i_d:\t{i_d}\tN[-1]:{N[-1]}\ti_b:{i_b}")
				print("D:",D)
				D[i_d,N[-1]].remove(i_b)
				D[N[-1],i_d].remove(i_b)
				N.append(i_d)
				continue
			
		i_b=N.pop()
		L_i.append(i_b)
	

def add_edge(S,D,L,i_p):
	l=len(L)
	D[L[0],L[1]].append(i_p)
	D[L[1],L[0]].append(i_p)
	D[L[0],i_p]=[L[1]]
	D[i_p,L[0]]=[L[1]]
	for i in range(1,l-1):
		D[L[i],L[i+1]].append(i_p)
		D[L[i+1],L[i]].append(i_p)
		D[L[i],i_p]=[L[i-1],L[i+1]]
		D[i_p,L[i]]=[L[i-1],L[i+1]]
		
	#i==l-2
	D[L[l-1],i_p]=[L[l-2]]
	D[i_p,L[l-1]]=[L[l-2]]
	
	for i in L:
		S[i].add(i_p)
		S[i_p].add(i)
	
def check_and_del(P,S,D,L,i_p,i_b,i_c):
	i_d=D[i_b,i_c]
	if in_circle_bcd_p(P,i_p,i_b,i_c,i_d):
		S[i_b].discard(i_c)
		S[i_c].discard(i_b)
		del D[i_b,i_c]
		del D[i_c,i_b]
		check_and_del(P,S,D,L,i_p,i_b,i_c)
	else:
		L.append(i_c)
		
def check_and_Flip(P,S,D,i_p,i_b,i_c):
	i_d=D[i_b,i_c]
	if in_circle_bcd_p(P,i_p,i_b,i_c,i_d):
		S[i_b].discard(i_c)
		S[i_c].discard(i_b)
		del D[i_b,i_c]
		del D[i_c,i_b]
		check_and_Flip(P,S,D,i_p,i_b,i_c)
	
	
def Flip_T(S,D,i_p,i_b,i_c,i_d):
	S[i_b].discard(i_c)
	S[i_c].discard(i_b)
	del D[i_b,i_c],D[i_c,i_b]
	D[i_b,i_d]=D[i_d,i_b]=D[i_c,i_d]=D[i_d,i_c]=ip
	D[i_b,i_d]=D[i_d,i_b]=D[i_c,i_d]=D[i_d,i_c]=ip
	S[i_d].add(i_p)
	S[i_p].add(i_d)

def Sorted_Increment_w_d(A,p,a1):
	if ToLeft(p,A[a1-1],A[a1])>0:
		a2=a1-len(A)+1
		
	else:
		a2=a1-len(A)
		while ToLeft(p,A[a1-1],A[a1])<=0:
			a1-=1
			
	while ToLeft(p,A[a2],A[a2+1])<=0:
		a2+=1
			
	if a2==0:
		return A[:a1+1]+[p],a1+1
	return A[:a1+1]+[p]+A[a2:],a1+1
	
def point_to_edge(L_neighbor,i,j):
	return set(L_neighbor[i]).intersection(L_neighbor[j])
"""
下面的这些涉及L_neighbor。暂时先不写
"""
# def add_point_i(P,A,i_p,a1,L_neighbor,S):
# 	p=P[i_p]
# 	if ToLeft(p,[A[a1-1]],P[A[a1]])>0:
# 		a2=a1-len(A)+1
		
# 	else:
# 		a2=a1-len(A)
# 		while ToLeft(p,P[A[a1-1]],P[A[a1]])<=0:
# 			a1-=1
			
# 	while ToLeft(p,P[A[a2]],P[A[a2+1]])<=0:
# 		a2+=1
			
# 	b1=a1
# 	b2=a2+len(A)
# 	rques_Flip=[]
# 	while b1<b2:
# 		i_d=S[A[b1]].intersection(S[A[b1+1]])
# 		if in_circle_bcd_p(P,i_p,A[b1],A[b1+1],i_d):
# 			Flip_T()
	
# 	if a2==0:
# 		return A[:a1+1]+[p],a1+1
# 	return A[:a1+1]+[p]+A[a2:],a1+1

# def check_and_Flip():
	
# def Flip_T(P,L_neighbor,S,i_p,i_b,i_c,i_d):
# 	S[i_b].discard(i_c)
# 	S[i_c].discard(i_b)
# 	L_neighbor[i_b].remove(i_c)
# 	L_neighbor[i_c].remove(i_b)
	
# 	S[i_d].add(i_p)
	
# def L_neighbor_add(L_neighbor):
# 	pass

# def Sorted_Increment_w_d(A,p,a1,L_neighbor):
# 	if ToLeft(p,A[a1-1],A[a1])>0:
# 		a2=a1-len(A)+1
		
# 	else:
# 		a2=a1-len(A)
# 		while ToLeft(p,A[a1-1],A[a1])<=0:
# 			a1-=1
			
# 	while ToLeft(p,A[a2],A[a2+1])<=0:
# 		a2+=1
			
# 	if a2==0:
# 		return A[:a1+1]+[p],a1+1
# 	return A[:a1+1]+[p]+A[a2:],a1+1
	
# def point_to_edge(L_neighbor,i,j):
# 	return set(L_neighbor[i]).intersection(L_neighbor[j])
	
def point_to_edge_S(S,i,j):
	return S[i].intersection(S[j]).pop()
	
def out_of_circle_bcd(P,i_a,i_b,i_c,i_d):
	ab=P[i_b]-P[i_a]
	ac=P[i_c]-P[i_a]
	db=P[i_b]-P[i_d]
	dc=P[i_c]-P[i_d]
	
	#np.dot(v1,v2)==|v1| |v2| cos<v1,v2>
	#
	return np.dot(ab,ac)*np.linalg.norm(db)*np.linalg.norm(dc)+np.dot(db,dc)*np.linalg.norm(ab)*np.linalg.norm(ac)>0
	
def in_circle_bcd(P,i_a,i_b,i_c,i_d):
	ab=P[i_b]-P[i_a]
	ac=P[i_c]-P[i_a]
	db=P[i_b]-P[i_d]
	dc=P[i_c]-P[i_d]
	
	return np.dot(ab,ac)*np.linalg.norm(db)*np.linalg.norm(dc)+np.dot(db,dc)*np.linalg.norm(ab)*np.linalg.norm(ac)<0
	
def in_circle_bcd_p(P,p,i_b,i_c,i_d):
	ab=P[i_b]-p
	ac=P[i_c]-p
	db=P[i_b]-P[i_d]
	dc=P[i_c]-P[i_d]
	
	return np.dot(ab,ac)*np.linalg.norm(db)*np.linalg.norm(dc)+np.dot(db,dc)*np.linalg.norm(ab)*np.linalg.norm(ac)<0
	
def show_ch_i(P,ch_i):
	# print("ch_i in show_ch_i")
	# print(ch_i)
	# print(type(ch_i))
	# for i in ch_i:
	# 	print(i)
	plt.scatter(P[:,0],P[:,1])
	ch_i.append(ch_i[0])
	plt.plot(P[ch_i,0],P[ch_i,1])
	del ch_i[-1]
	plt.show()
	
def show(P,D_tri):
	plt.scatter(P[:,0],P[:,1])
	for key1,key2 in D_tri:
		if key1>key2:
			plt.plot([P[key1][0],P[key2][0]],[P[key1][1],P[key2][1]],color = 'blue')
			
	plt.show()
	
	
def show_ch_dt(P,ch_i,D_tri):
	plt.figure(figsize=(8, 6))
	plt.scatter(P[:,0],P[:,1])
	for key1,key2 in D_tri:
		if key1>key2:
			plt.plot([P[key1][0],P[key2][0]],[P[key1][1],P[key2][1]],color = 'blue',alpha=0.5)
			
	ch_i.append(ch_i[0])
	i=0
	while i<len(ch_i)-1:
		if (ch_i[i],ch_i[i+1]) in D_tri:
			plt.plot([P[ch_i[i]][0],P[ch_i[i+1]][0]],[P[ch_i[i]][1],P[ch_i[i+1]][1]],color='green',alpha=0.5)
		
		else:
			# plt.plot(P[ch_lack,0],P[ch_lack,1],color='red',alpha=0.5)
			plt.plot([P[ch_i[i]][0],P[ch_i[i+1]][0]],[P[ch_i[i]][1],P[ch_i[i+1]][1]],color='red',alpha=0.5)
		
		i+=1
		
	del ch_i[-1]
			
	plt.savefig(f"ch_dt_{show_ch_dt.count}.png")
	show_ch_dt.count+=1
	plt.show()
	
show_ch_dt.count=0