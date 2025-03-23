def circumcircle(A,B,C):
	u1, v1 = B[0]-A[0], B[1]-A[1]
	u2, v2 = C[0]-A[0], C[1]-A[1]
	
	det_m2 = 2*(u1*v2-v1*u2)
	l1=u1**2+v1**2
	l2=u2**2+v2**2
	
	x=(v2*l1-v1*l2)/det_m2
	y=(u1*l2-u2*l1)/det_m2
	
	R = (x**2+y**2)**(0.5)
	return (x+A[0],y+A[1]),R
	
def intersect_circle(O,R,A):
	OA=(A[0]-O[0],A[1]-O[1])
	la=(OA[0]**2+OA[1]**2)**(0.5)
	return O[0]+R/la * OA[0],O[1]+R/la * OA[1]
	
def intersect_circle_in(O,R,A,C):
	OC=(C[0]-O[0],C[1]-O[1])
	CA=(A[0]-C[0],A[1]-C[1])
	l_CA2=(CA[0]**2+CA[1]**2)
	l_CE_l_CA=-2*(OC[0]*CA[0]+OC[1]*CA[1])
	alpha = l_CE_l_CA/l_CA2
	CE = (alpha*CA[0],alpha*CA[1])
	return C[0]+CE[0],C[1]+CE[1]