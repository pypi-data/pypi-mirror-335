import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.backend_bases import MouseButton
import json
class Draw:
	def __init__(self, ax, save='data'):
		self.ax = ax
		self.points = []
		self.segments = []
		self.l=0
		self.start = True
		
		plt.connect('button_press_event', self.on_click)
		plt.connect('key_press_event', self.on_press)
		ax.axes.set_aspect('equal')
		ax.axis("off")
		plt.show()
		
		data={"vertices":self.points, "segments":self.segments}
	
		if save[-5:]!=".json":
			save+='.json'
			
		with open(save,'w',encoding='utf-8') as f:
			json.dump(data, f, ensure_ascii=False, indent=4)
			
		
	
	def on_click(self,event):  
		if event.inaxes:
			rounded_x = round(event.xdata, 1)  
			rounded_y = round(event.ydata, 1)  
			
			if self.start:
				self.start=False
			else:
				self.line,=plt.plot([rounded_x,self.points[-1][0]],[rounded_y,self.points[-1][1]],color = 'r')
				
			self.points.append((rounded_x, rounded_y))  
			print(f"Added point: ({rounded_x}, {rounded_y})")  
			  
			self.scat=plt.scatter(rounded_x, rounded_y, color='red')  # 可视化新添加的点  
			
				
			plt.draw()  # 更新图形
	  
	def on_press(self,event):
		print('press', event.key)
		if event.key == 'c':
			for i in range(self.l,len(self.points)-1):
				self.segments.append((i,i+1))
			self.segments.append((len(self.points)-1,self.l))
			plt.plot([self.points[-1][0],self.points[self.l][0]],[self.points[-1][1],self.points[self.l][1]],color = 'r')
			plt.draw()
			self.l=len(self.points)
			self.start = True
			
		if event.key == 'x':
			for i in range(self.l,len(self.points)-1):
				self.segments.append((i,i+1))
			self.l=len(self.points)
			self.start = True
			
		if event.key == 'z':
			if self.start==False:
				self.line.remove()
			else:
				return
				
			self.scat.remove()
			if self.l==len(self.points):
				self.start = True
			else:
				self.start = False