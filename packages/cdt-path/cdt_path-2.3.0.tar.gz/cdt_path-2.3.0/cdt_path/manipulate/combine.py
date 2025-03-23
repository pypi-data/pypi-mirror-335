import numpy as np

def combine_O(A,B):
	l=len(A['vertices'])
	C={}
	C['vertices'] = np.concatenate((A['vertices'], B['vertices']), axis=0)
	if 'segments' in A:
		C['segments'] = np.concatenate((A['segments'], B['segments']+l), axis=0)
	
	if 'holes' in A:
		if 'holes' in B:
			C['holes'] = np.concatenate((A['holes'], B['holes']+l), axis=0)
		else:
			C['holes'] = A['holes']
	elif 'holes' in B:
		C['holes'] = B['holes']
	return C
	
def combine(A,B):
	C={}
	if 'vertices' in A:
		l=len(A['vertices'])
		if 'vertices' in B:
			C['vertices'] = np.concatenate((A['vertices'], B['vertices']), axis=0)
		else:
			C['vertices'] = A['vertices']
			
	if 'segments' in A:
		C['segments'] = np.concatenate((A['segments'], B['segments']+l), axis=0)
	
	if 'holes' in A:
		if 'holes' in B:
			C['holes'] = np.concatenate((A['holes'], B['holes']), axis=0)
		else:
			C['holes'] = A['holes']
	elif 'holes' in B:
		C['holes'] = B['holes']
	return C
