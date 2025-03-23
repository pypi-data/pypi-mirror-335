import numpy as np
from ..utils import *
def divide_and_conquer(P):
	return divide_and_conquer_sorted(Simplify_With_X_i(P[P[:,0].argsort()]))[0]

def divide_and_conquer_sorted(P):
	i=0
	l=len(P)
	if l<6:
		L=Incremental_Convex_Hull_Sorted_Fixed(P)
		i_xmin=min(enumerate(L), key=lambda x: x[1][0])[0]
		if i_xmin!=0:
			L=L[i_xmin:]+L[:i_xmin]
		return L, max(enumerate(L), key=lambda x: x[1][0])[0]
	
	A, i_axmax=divide_and_conquer_sorted(P[:l//2])
	B, i_bxmax=divide_and_conquer_sorted(P[l//2:])
	return Combin_Convex_Hull_M_2(A,B,i_axmax,i_bxmax)
	
#计算两个凸包的切线
def _Tangent_U(A,B,a1):
	b=0
	la=len(A)
	lb=len(B)
	while LogLeft(A[a1],B[b],B[b-1])!=1 or LogLeft(B[b],A[a1],A[a1+1])!=1:
		while LogLeft(A[a1],B[b],B[b-1])!=1:
			b-=1
			if b-1==-lb:
				b=1
		
		while LogLeft(B[b],A[a1],A[a1+1])!=1:
			# or LogLeft(B[b],A[a1],A[a1-1])!=1
			a1+=1
			if a1+1==la:
				a1=-1
				
	return a1,b

def Combin_Convex_Hull_M(A,B,a1):
	a2=a1
	b2=b1=0
	la=len(A)
	lb=len(B)
	while LogLeft(A[a1],B[b1],B[b1-1])!=1 or LogLeft(B[b1],A[a1],A[a1+1])!=1:
		while LogLeft(A[a1],B[b1],B[b1-1])!=1:
			b1-=1
			if b1-1==-lb1:
				b1=1
		
		while LogLeft(B[b1],A[a1],A[a1+1])!=1:
			# or LogLeft(B[b1],A[a1],A[a1-1])!=1
			a1+=1
			if a1+1==la:
				a1=-1
				
				
	while LogLeft(A[a2],B[b2],B[b2-1])!=1 or LogLeft(B[b2],A[a2],A[a2+1])!=1:
		while LogLeft(A[a2],B[b2],B[b2-1])!=1:
			b-=1
			if b-1==-lb:
				b=1
		
		while LogLeft(B[b2],A[a2],A[a2+1])!=1:
			# or LogLeft(B[b],A[a1],A[a1-1])!=1
			a2+=1
			if a2+1==la:
				a2=-1
				
	return a1,b
	pass
	
def Combin_Convex_Hull_M_2(A,B,a1,i_xmax=None):
	if i_xmax==None:
		i_xmax=max(enumerate(B), key=lambda x: x[1][0])[0]
	a2=a1	#a1=a1,a1+1,...,la-1==-1	a2=a1,a1-1,...,0
	b2=0	#b2=0,1,2,...,lb-1
	la=len(A)
	b1=lb=len(B)	#b1=lb,lb-1,lb-2,...,1
	B.append(B[0])
	if a1+1==la: a1=-1
	while 1:
		while LogLeft(A[a1],B[b1-1],B[b1])!=1:
			b1-=1
				
		if LogLeft(B[b1],A[a1],A[a1+1])!=1:
			a1+=1
			if a1+1==la: a1=-1
			while LogLeft(B[b1],A[a1],A[a1+1])!=1:
				a1+=1
				if a1+1==la: a1=-1
				# a1=-1 if a1+2==la else a1+=1
		else:
			break
			
	while 1:
		while LogLeft(A[a2],B[b2],B[b2+1])!=1:
			b2+=1
		
		if LogLeft(B[b2],A[a2-1],A[a2])!=1:
			a2-=1
			while LogLeft(B[b2],A[a2-1],A[a2])!=1:
				a2-=1
		else:
			break
			
	if a1==0:
		return A[:a2+1]+B[b2:b1+1],a2+1+i_xmax-b2
	return A[:a2+1]+B[b2:b1+1]+A[a1:],a2+1+i_xmax-b2
	
def Combin_Convex_Hull_M_3(A,B,a1):
	a2=a1
	b2=b1=0
	la=len(A)
	lb=len(B)
	if a1+1==la: a1=-1
	while 1:
		while LogLeft(A[a1],B[b1],B[b1-1])!=-1:
			b1-=1
			if b1-1==-lb:
				b1=1
				
		if LogLeft(B[b1],A[a1],A[a1+1])!=1:
			a1+=1
			if a1+1==la: a1=-1
			while LogLeft(B[b1],A[a1],A[a1+1])!=1:
				a1+=1
				if a1+1==la: a1=-1
		else:
			break
			
	while 1:
		while LogLeft(A[a2],B[b2],B[b2+1])!=-1:
			b2+=1
			if b2+1==lb:
				b2=-1
		
		if LogLeft(B[b2],A[a2-1],A[a2])!=1:
			a2-=1
			while LogLeft(B[b2],A[a2-1],A[a2])!=1:
				a2-=1
		else:
			break
			
	if a1==0:
		return A[:a2+1]+B[b2:b1]+[B[b1]]
	return A[:a2+1]+B[b2:b1]+[B[b1]]+A[a1:]
	
def Incremental_Convex_Hull_Sorted_Fixed(P):
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
		LogFlag=LogLeft(P[0],P[i1],P[i])
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
		L=Conv_Fixed(L,P[i])
		i+=1
		
	return L
	
def Conv_Fixed(L,p):
	l=len(L)
	flag_o=LogLeft(L[l-1],L[0],p)
	i=0
	i_r=i_l=-1
	L.append(L[0])
	while i<l:
		flag=LogLeft(L[i],L[i+1],p)
		if flag==0:
			ab=L[i+1]-L[i]
			ac_ab=np.dot(p-L[i], ab)
			if ac_ab<0:
				i_r=i+1
				if i_l!=-1: break
				flag_o=1
			elif ac_ab>np.dot(ab, ab):
				i_l=i
				if i_r!=-1: break
				flag_o=-1
			else:
				del L[-1]
				return L
		elif flag!=flag_o:
			if flag==1:
				i_r=i
				if i_l!=-1: break
			else:
				if flag_o==0:
					if i==0:
						i_l=l-1
					else:i_l=i-1
				else:
					i_l=i
				if i_r!=-1: break
			flag_o=flag
		i+=1
		
	del L[-1]
	
	if i_r==-1 and i_l==-1: return L
	if i_r<i_l:
		L=[p]+L[i_r:i_l+1]
	else:
		L=L[0:i_l+1]+[p]+L[i_r:]
	return L