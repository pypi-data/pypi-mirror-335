# 导入前面定义的DCEL类  
from definition import DCEL, Vertex, Edge, Face  
  
# 创建一个DCEL实例  
dcel = DCEL()  
  
# 添加顶点  
v1 = dcel.add_vertex(0, 0)  
v2 = dcel.add_vertex(1, 0)  
v3 = dcel.add_vertex(1, 1)  
v4 = dcel.add_vertex(0, 1)  
  
# 添加边  
e1 = dcel.add_edge(v1, None, None, None, None)  # v1 -> v2  
e2 = dcel.add_edge(v2, None, None, None, None)  # v2 -> v3  
e3 = dcel.add_edge(v3, None, None, None, None)  # v3 -> v4  
e4 = dcel.add_edge(v4, None, None, None, None)  # v4 -> v1  
  
# 设置边的连接关系  
e1.next = e2  
e2.prev = e1  
e2.next = e3  
e3.prev = e2  
e3.next = e4  
e4.prev = e3  
e4.next = e1  
e1.prev = e4  
  
# 设置边的反向边  
e1.twin = dcel.add_edge(v2, e1, None, None, None)  # v2 -> v1  
e2.twin = dcel.add_edge(v3, e2, None, None, None)  # v3 -> v2  
e3.twin = dcel.add_edge(v4, e3, None, None, None)  # v4 -> v3  
e4.twin = dcel.add_edge(v1, e4, None, None, None)  # v1 -> v4  
  
# 设置面  
f1 = dcel.add_face(e1)  
  
# 为每条边设置相邻的面  
e1.face = f1  
e2.face = f1  
e3.face = f1  
e4.face = f1  
e1.twin.face = f1  
e2.twin.face = f1  
e3.twin.face = f1  
e4.twin.face = f1  
  
# 至此，我们已经创建了一个包含4个顶点和4条边的简单DCEL，代表一个正方形  
  
import matplotlib.pyplot as plt  
  
def draw_dcel(dcel):  
    # 提取顶点和边  
    vertices = list(dcel.vertices.values())  
    edges = list(dcel.edges.values())  
      
    # 绘制顶点  
    plt.scatter([v.x for v in vertices], [v.y for v in vertices])  
      
    # 为每条边绘制线段  
    for edge in edges:  
        if edge.face is not None:  # 只绘制有相邻面的边（即图形的外边界）  
            x_coords = [edge.origin.x, edge.origin.x + (edge.twin.origin.x - edge.origin.x) if edge.twin else edge.origin.x]  
            y_coords = [edge.origin.y, edge.origin.y + (edge.twin.origin.y - edge.origin.y) if edge.twin else edge.origin.y]  
            plt.plot(x_coords, y_coords, '-o')  
      
    # 设置坐标轴范围以适应图形  
    plt.xlim(min([v.x for v in vertices]) - 0.5, max([v.x for v in vertices]) + 0.5)  
    plt.ylim(min([v.y for v in vertices]) - 0.5, max([v.y for v in vertices]) + 0.5)  
      
    # 显示图形  
    plt.grid(True)  
    plt.show()  
  
# 假设dcel是之前创建好的DCEL实例  
draw_dcel(dcel)  # 调用此函数以绘制DCEL图形