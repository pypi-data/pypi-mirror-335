def funnel_slow(apex, Pl, Pr, Li):
	r=Pr[0]-apex
	l=Pl[0]-apex
	P=[Pl[0],Pr[0]]
	il=ir=1
	for i in Li:
		if i==0:
			P.append(Pl[il])
			il+=1
		else:
			P.append(Pr[ir])
			ir+=1
			
	P.append(Pr[-1])
	P.append(Pr[-1])
	
	L=[]
	Li = [0,1]+Li+[0,1]
	li=0
	ri=1
	i=2
	while i < len(P)-2:
		if Li[i]==0:
			nl = P[i] - apex
			if cp(l,nl)<=0:
				if cp(r,nl)>0:
					l = nl
					li = i
				else:
					apex = P[ri]
					L.append(apex)
					ri = ri+1
					if Li[ri]==1:
						li = ri-2
						while Li[li]!=0:
							li-=1
							
					else:
						while Li[ri]!=1:
							ri+=1
							
						li = ri-1
					l=P[li]-apex
					r=P[ri]-apex
					i=ri
					
		else:
			nr = P[i] - apex
			if cp(r,nr)>=0:
				if cp(l,nr)<0:
					r = nr
					ri = i
				else:
					apex = P[li]
					L.append(apex)
					li = li+1
					if Li[li]==0:
						ri = li-2
						while Li[ri]!=1:
							ri-=1
							
					else:
						while Li[li]!=0:
							li+=1
							
						ri = li-1
					l=P[li]-apex
					r=P[ri]-apex
					i=li
			
		i+=1
	# End while
	if i<len(P):
		nl = P[i] - apex
		if cp(l,nl)>=0:
			L.append(P[li])
		elif cp(nl,r)>=0:
			L.append(P[ri])
	return L
	
def cross_product(A,B):
	return A[0]*B[1] - A[1]*B[0]
	
cp = cross_product