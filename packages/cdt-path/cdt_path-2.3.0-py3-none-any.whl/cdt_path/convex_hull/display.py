import matplotlib.pyplot as plt
def disp(convex_hull):
	X_l=[]
	Y_l=[]
	for c in convex_hull:
		X_l.append(c[0])
		Y_l.append(c[1])
	
	X_l.append(X_l[0])
	Y_l.append(Y_l[0])
	plt.plot(X_l,Y_l)