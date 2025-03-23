import matplotlib.pyplot as plt
import numpy as np

def ToLeft(a,b,c):
	return a[0]*(b[1]-c[1])+a[1]*(c[0]-b[0])+b[0]*c[1]-c[0]*b[1]>0
	
def Qdet(a,b,c):
	return a[0]*(b[1]-c[1])+a[1]*(c[0]-b[0])+b[0]*c[1]-c[0]*b[1]
	
def LogLeft(a,b,c):
	O=Qdet(a,b,c)
	if O==0:
		return 0
	elif O>0:
		return 1
	return -1
def Convex_Hull_EE(P):
	l=len(P)
	i=0
	L=[]
	while i<l-1:
		j=i+1
		while j<l:
			k=0
			flag=2
			while k<l:
				if k==i or k==j:
					k+=1
					continue
				O=LogLeft(P[i],P[j],P[k])
				if O==0:
					k+=1
					continue
				if flag==2:
					flag=O
				elif flag!=O:
					break
				k+=1
			if k==l:
				if flag==1:
					L.append([P[i],P[j]])
				else:
					L.append([P[j],P[i]])
			j+=1
		i+=1
	return L
	
