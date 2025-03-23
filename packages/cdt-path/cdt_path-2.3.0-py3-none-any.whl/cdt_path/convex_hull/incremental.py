import numpy as np
from ..utils import ToLeft,Simplify_With_X_i

def incremental(P):
	l=len(P)
	if l==0:
		return []
		
	i1=1
	while i1<l:
		if np.array_equal(P[0],P[i1]):
			i1+=1
			continue
		break
	else:
		return [P[0]]
		
	i=i1+1
	while i<l:
		LogFlag=ToLeft(P[0],P[i1],P[i])
		if LogFlag==0:
			if abs(P[i][0]-P[0][0])+abs(P[i][1]-P[0][1])>abs(P[i1][0]-P[0][0])+abs(P[i1][1]-P[0][1]):
				i1=i
				
			i+=1
			continue
		elif LogFlag<0:
			L=[P[0],P[i],P[i1]]
			break
		else:
			L=[P[0],P[i1],P[i]]
			break
	else:
		return [P[0],P[i1]]
		
	i+=1
	while i<l:
		L=conv_2(L,P[i])
		i+=1
		
	return L
	
def conv(L,p):
	l=len(L)
	flag_f=flag_o=LogLeft(L[l-1],L[0],p)
	i=0
	i_r=i_l=-1
	while i<l-1:
		flag=LogLeft(L[i],L[i+1],p)
		if flag!=flag_o:
			if flag==0:
				ac=p-L[i]
				ab=L[i+1]-L[i]
				alpha=np.dot(ac, ab) / np.dot(ab, ab)
				if alpha>1:
					i_l=i
					if i_r!=-1:
						break
				elif alpha<0:
					if flag_o!=-1:
						print("This algorithm maybe wrong! conv")
					i_r=i
					if i_l!=-1:
						break
				else:
					return L
			elif flag==1:
				i_r=i
			else:
				i_l=i
			flag_o=flag
		i+=1
	else:
		if flag_f!=flag_o:
			if flag_f==1:
				i_r=i
			else:
				i_l=i
		
	if i_r==-1:
		return L
	if i_r<i_l:
		L=[p]+L[i_r:i_l+1]
	else:
		L=L[0:i_l+1]+[p]+L[i_r:]
	return L
	
def conv_2(L,p):
	l=len(L)
	flag_o=ToLeft(L[l-1],L[0],p)
	i=0
	i_r=i_l=-1
	L.append(L[0])
	while i<l:
		flag=ToLeft(L[i],L[i+1],p)
		if flag==0:
			ac=p-L[i]
			ab=L[i+1]-L[i]
			alpha=np.dot(ac, ab)
			if alpha>np.dot(ab, ab):
				i_l=i
				if i_r!=-1:
					break
				flag_o=-1
			elif alpha<0:
				if flag_o!=-1:
					print("This algorithm maybe wrong! conv")
				i_r=i+1
				if i_l!=-1:
					break
				flag_o=1
			else:
				return L
		elif flag!=flag_o:
			if flag>0 and flag_o<=0:
				i_r=i
				if i_l!=-1:
					break
			else:
				if flag_o==0:
					i_l=i-1
				elif flag_o>0:
					i_l=i
				if i_r!=-1:
					break
			flag_o=flag
		i+=1
		
	del L[-1]
	
	if i_r==-1 and i_l==-1:
		return L
	if i_r<i_l:
		L=[p]+L[i_r:i_l+1]
	else:
		L=L[0:i_l+1]+[p]+L[i_r:]
	return L
	
	
def incremental_sort(P):
	return incremental_sorted_simplified(Simplify_With_X_i(P[P[:,0].argsort()]))
	
def incremental_sorted_simplified(P):
	l=len(P)
	if l<3:
		return P
		
	i1=1
	i=2
	while i<l:
		LogFlag=ToLeft(P[0],P[i1],P[i])
		if LogFlag==0:
			i1=i
			i+=1
			continue
		elif LogFlag<0:
			L=[P[0],P[i],P[i1]]
			i_xmax=1
			break
		else:
			L=[P[0],P[i1],P[i]]
			i_xmax=2
			break
	else:
		return [P[0],P[i1]]
		
	i+=1
	while i<l:
		L,i_xmax=sorted_increment_w(L,P[i],i_xmax)
		i+=1
		
	return L
	
def incremental_sorted_simplified_N(P):
	l=len(P)
	if l<3:
		return P
		
	i1=1
	i=2
	while i<l:
		LogFlag=ToLeft(P[0],P[i1],P[i])
		if LogFlag==0:
			i1=i
			i+=1
			continue
		elif LogFlag<0:
			L=[P[0],P[i],P[i1]]
			i_xmax=1
			break
		else:
			L=[P[0],P[i1],P[i]]
			i_xmax=2
			break
	else:
		return [P[0],P[i1]]
		
	i+=1
	while i<l:
		L,i_xmax=sorted_Increment_w(L,P[i],i_xmax)
		i+=1
		
	return L
	
def sorted_increment(A,p,a1=None):
	if a1==None:
		a1=max(enumerate(A), key=lambda x: x[1][0])[0]
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
	
def sorted_increment_w(A,p,a1):
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