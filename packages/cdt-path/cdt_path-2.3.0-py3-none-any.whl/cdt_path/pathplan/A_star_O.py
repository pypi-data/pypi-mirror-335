from queue import PriorityQueue
def a_star_search_O(graph,start,goal):
	frontier = PriorityQueue()
	frontier.put(start,0)
	came_from={}
	cost_so_far={}
	came_from[start]=None
	cost_so_far[start]=0
	
	while not frontier.empty():
		current= frontier.get()
		
		if current==goal:
			break
			
		for next in graph.neighbors(current):
			new_cost = cost_so_far[current] + graph.cost(current,next)
			if next not in cost_so_far or new_cost< cost_so_far[next]:
				cost_so_far[next]=new_cost
				#Change heuristic
				priority = new_cost + heuristic(goal,next)
				frontier.put(next, priority)
				came_from[next] = current
				
	return came_from, cost_so_far
	
def a_star_search(graph,start,goal):
	frontier = PriorityQueue()
	frontier.put((0,start))
	came_from={}
	cost_so_far={}
	# came_from[start]=None
	cost_so_far[start]=0
	
	while not frontier.empty():
		current= frontier.get()[1]
		if current in came_from:
			continue
			
		if current==goal:
			break
			
		for next in graph.neighbors(current):
			new_cost = cost_so_far[current] + graph.cost(current,next)
			if next not in cost_so_far or new_cost< cost_so_far[next]:
				cost_so_far[next]=new_cost
				#Change heuristic
				priority = new_cost + heuristic(goal,next)
				frontier.put((priority, next))
				came_from[next] = current
				
	return came_from, cost_so_far