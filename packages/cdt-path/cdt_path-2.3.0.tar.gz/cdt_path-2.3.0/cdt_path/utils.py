import numpy as np
def cross_product(a,b):
	return a[0]*b[1]-a[1]*b[0]
	
def LogLeft(a,b,c):
	if (a==b).all():
		return 0
	else:
		ab=b-a
		ac=c-a
		cp2=ab[0]*ac[1]-ab[1]*ac[0]
		if cp2>0:
			return 1
		elif cp2<0:
			return -1
		return 0
		
def ToLeft(a,b,c):
	ab=b-a
	ac=c-a
	return ab[0]*ac[1]-ab[1]*ac[0]
	
def Project_Point(a,b,c):
	if (a==b).all():
		return a
	return (np.dot(c-b,a-b)*a+np.dot(a-c,a-b)*b)/np.dot(a-b,a-b)
	
def Distance_S(a,b,c):
	cp=c-(np.dot(c-b,a-b)*a+np.dot(a-c,a-b)*b)/np.dot(a-b,a-b)
	return np.dot(cp,cp)
	
def Project_Point_Segment(a, b, c):  
	ab = b - a  
	ac = c - a 
	lambda_ = np.dot(ac, ab) / np.dot(ab, ab)
	lambda_ = max(0, min(1, lambda_))
	p = a + lambda_ * ab
	return p

def LengthD_abs(a,b,c):
	return abs(b[0]-a[0])+abs(b[1]-a[1])
	
def Length_abs_2(a,b):
	return abs(b[0]-a[0])+abs(b[1]-a[1])
	
def In_Conv(L,p):
	l=len(L)
	i=0
	L.append(L[0])
	while i<l:
		flag=LogLeft(L[i],L[i+1],p)
		if flag==0:
			ac=p-L[i]
			ab=L[i+1]-L[i]
			beta=np.dot(ac, ab)
			if beta<0 or beta>np.dot(ab, ab):
				return False
			else:
				return True
		elif flag==-1:
			return False
		i+=1
	return True
	
def Simplify_With_X(P):
	l=len(P)
	L=[]
	i=0
	while i<l-1:
		if P[i][0]==P[i+1][0]:
			if P[i][1]==P[i+1][1]:
				i+=1
				continue
			elif P[i][1]>P[i+1][1]:
				y_max=P[i][1]
				y_min=P[i+1][1]
			else:
				y_max=P[i+1][1]
				y_min=P[i][1]
			i+=1
			while i<l-1 and P[i][0]==P[i+1][0]:
				i+=1
				if P[i][1]>y_max:
					y_max=P[i][1]
				elif P[i][1]<y_min:
					y_min=P[i][1]
			
			L.append(np.array((P[i][0],y_min)))
			L.append(np.array((P[i][0],y_max)))
			
		else:
			L.append(P[i])
		i+=1
	
	if L[-1][0]!=P[l-1][0]:
		L.append(P[l-1])
	return L
	
	
def Simplify_With_X_i(P):
	l=len(P)
	L=[]
	i=0
	while i<l-1:
		if P[i][0]==P[i+1][0]:
			if P[i][1]==P[i+1][1]:
				i+=1
				continue
			elif P[i][1]>P[i+1][1]:
				i_ymax=i
				i_ymin=i+1
			else:
				i_ymax=i+1
				i_ymin=i
			i+=1
			while i<l-1 and P[i][0]==P[i+1][0]:
				i+=1
				if P[i][1]>P[i_ymax][1]:
					i_ymax=i
				elif P[i][1]<P[i_ymin][1]:
					i_ymin=i
			
			L.append(P[i_ymin])
			L.append(P[i_ymax])
		else:
			L.append(P[i])
		i+=1
	
	if L[-1][0]!=P[l-1][0]:
		L.append(P[l-1])
	return L