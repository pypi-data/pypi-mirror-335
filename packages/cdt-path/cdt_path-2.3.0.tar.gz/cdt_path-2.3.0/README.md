# 使用约束Delaunay三角来寻路
# Using Constrained Delaunay Triangle for path-planning

## 快速使用 Quick start：
``` bash
pip install cdt_path
```
``` python
import cdt_path.demo # 尝试用鼠标左键点击，对功能的直观认识
```

``` python
#import cdt_path.demo # 等价于如下代码
import matplotlib.pyplot as plt
import cdt_path as cdt
import matplotlib.tri as tri

fig ,ax = plt.subplots(figsize=(14,8))

floor = {"vertices":[],
    "segments":[],
    "holes": []
    }

cc  = cdt.triangulate(floor)
# cc  = cdt.triangulate(floor, 'pD') # 使用CCDT
# cc  = cdt.triangulate(floor, 'pDc') # 使用CCDT，并且使用凸包

cdt.border.plot(ax, **cc) # 绘制红色约束边

triang = tri.Triangulation(cc['vertices'][:,0],cc['vertices'][:,1],cc['triangles']) # 转换成matplotlib的格式

cdt.Interact(ax, triang) # 开启交互界面
plt.show()
```

## 功能特点 Features
``` python
import cdt_path as cdt # 建议取别名导入
```
### 三角剖分支持 Triangulation Support：
库提供了对二维空间中的点集进行三角剖分的功能，这些三角形可以作为寻路的基础网格。
自主实现了Delaunay三角剖分的外增量算法，以及各种凸包算法。
支持调用triangle库以实现约束Delaunay三角剖分或者“约束一致的Delaunay三角剖分”以及其他剖分方式。


The library supports triangulating a set of points in 2D space, and the resulting triangular grid can serve as the basis for pathfinding.
The library independently implements the incremental algorithm for Delaunay triangulation and is compatible with various convex hull algorithms.
Additionally, the library provides the ability to call the triangle library to achieve constrained Delaunay triangulation or "constrained conforming Delaunay triangulation" and other triangulation methods.

### 高效寻路算法 Efficient Pathfinding Algorithm：
``` python
#came_from, cost_so_far = a_star_search_G(triang, start, goal) # 只使用起点终点所在三角形的重心作为代表
came_from, cost_so_far = cdt.pathplan.a_star_P(triang, start_point, goal_point, start=None, goal=None)

#L_apex = cdt.pathplan.funnel_slow(apex, Pl, Pr, Li)
L_apex = cdt.pathplan.funnel(apex, Pl, Pr, Li)
```
基于三角剖分的网格，库实现了A*算法，能够快速找到两点之间的三角形通路。
自研快速漏斗算法，以在三角形通路中找到具体直线段路径。
同时保留了简单漏斗算法，用以测试比较。

Based on the triangular grid, the library integrates the A* algorithm to quickly find a triangular path between two points.
The library also develops a fast funnel algorithm to determine the specific line segment path within the triangular path.

### 障碍物标记 Obstacle Marking：
``` python
border = cdt_path.load("XXXX.json")
```
以平面直线图刻画障碍物，库内部支持画图功能，支持将绘制的平面直线图保存为json格式。
同时支持用户自定义扩展格式。

The library supports using planar line graphs to depict obstacles and has built-in drawing functionality that allows saving the drawn planar line graphs in JSON format. It also supports user-defined extended formats

### 接口友好 User-friendly Interface：
提供了易于使用的API接口，方便开发者集成到项目中。

The library provides concise and easy-to-use API interfaces, making it convenient for developers to integrate into their projects.

