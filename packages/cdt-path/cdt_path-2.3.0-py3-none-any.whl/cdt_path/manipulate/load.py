import json
def load(file):
	with open(file,'r',encoding = 'utf-8') as f:
		data = json.load(f)
		
	return data