from ..utils import ToLeft

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

import matplotlib.pyplot as plt
def funnel(apex, Pl, Pr, Li):
	r=Pr[0]-apex
	l=Pl[0]-apex
	L=[]
	i=ri=li=0
	nli=nri=1
	while i < len(Li):
		if Li[i]==0:
			nl = Pl[nli] - apex
			if cp(l,nl)<=0:
				li = nli
				if cp(r,nl)>0:
					l = nl
				else:
					apex = Pr[ri]
					L.append(apex)
					l=Pl[nli]-apex
					ri+=1
					while ri<nri:
						nr = Pr[ri]-apex
						nnri=ri+1
						while nnri<=nri:
							nnr = Pr[nnri] - apex
							if cp(nr,nnr)>=0:
								nr = nnr
								ri= nnri
							nnri+=1
								
						if cp(nr,l)<=0:
							apex = Pr[ri]
							L.append(apex)
							l= Pl[nli]-apex
							ri+=1
						else:
							break
						
					r=Pr[ri]-apex
					
			nli+=1
		else:
			nr = Pr[nri] - apex
			if cp(r,nr)>=0:
				ri = nri
				if cp(l,nr)<0:
					r = nr
				else:
					apex = Pl[li]
					L.append(apex)
					r=Pr[nri]-apex
					li+=1
					while li<nli:
						nl = Pl[li]-apex
						nnli=li+1
						while nnli<=nli:
							nnl = Pl[nnli] - apex
							if cp(nl,nnl)<=0:
								nl = nnl
								li= nnli
							nnli+=1
								
						if cp(nl,r)>=0:
							apex = Pl[li]
							L.append(apex)
							r= Pr[nri]-apex
							li+=1
						else:
							break
						
					l=Pl[li]-apex
			nri+=1
		i+=1
	# End while
	if i<=len(Li)+1:
		nl = Pr[-1] - apex
		if cp(l,nl)>0:
			if li<len(Pl)-2:
				apexs =[Pl[li],Pl[li+1]]
				nli = li+2
				while nli<len(Pl):
					if ToLeft(apexs[-2],apexs[-1],Pl[nli])>=0:
						apexs.append(Pl[nli])
						nli+=1
					else:
						apexs.pop()
						if len(apexs) == 1:
							apexs.append(Pl[nli])
							nli+=1
						
				apexs.pop()
				L+=apexs
			else:
				L.append(Pl[li])
		elif cp(nl,r)>0:
			if ri<len(Pr)-2:
				apexs =[Pr[ri],Pr[ri+1]]
				nri = ri+2
				while nri<len(Pr):
					if ToLeft(apexs[-2],apexs[-1],Pr[nri])<=0:
						apexs.append(Pr[nri])
						nri+=1
					else:
						apexs.pop()
						if len(apexs) == 1:
							apexs.append(Pr[nri])
							nri+=1
						
				apexs.pop()
				L+=apexs
			else:
				L.append(Pr[ri])
	return L
	# return []