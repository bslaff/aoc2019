import argparse
import numpy as np
from copy import copy, deepcopy
import itertools

def get_args():

	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str, help="Path to the input file")
	
	return parser.parse_args()

def run_main():

	args = get_args()

	f = open(args.infile, 'r')
	lines = f.readlines()
	f.close()

	lines = [list(line.strip()) for line in lines if len(line.strip())>0]
	arr = np.asarray(lines)

	# print_map(arr)
	# print(arr.shape)

	## strategy: first do dijkstra from each key to ALL other keys. Get min distance from each key to each other key. also from start position to each key.
	## while doing this, keep track of dependencies (doors) we run into on each path. 
	## Assumption: no cycles / multiple dependency paths, i.e. a dependency must be resolved (prove this?), and resolving it is sufficient.

	lower_set = set(list(range(97,123)))

	keys_d = dict()
	for y in range(arr.shape[0]):
		for x in range(arr.shape[1]):
			c = arr[y,x]
			if ord(c) in lower_set:
				keys_d[c] = dict()
				keys_d[c]['x']=x
				keys_d[c]['y']=y
				keys_d[c]['dependencies'] = set()

	arr_visited = np.zeros(shape=arr.shape)
	arr_visited[ arr=='@' ] = 1

	x_start = np.argwhere(arr_visited)[0][1]
	y_start = np.argwhere(arr_visited)[0][0]

	keys_d['start'] = dict()
	keys_d['start']['x'] = x_start
	keys_d['start']['y'] = y_start
	keys_d['start']['dependencies'] = set()

	# print(f"x_start {x_start}, y_start {y_start}")

	final_keys_d = dict()
	
	for c in keys_d.keys():
		x = keys_d[c]['x']
		y = keys_d[c]['y']
		# print(f"x {x}, y {y}")
		final_keys_d[c] = dijkstra(arr, x, y, deepcopy( keys_d ) )

	### Real solution: A*
	# The key to A* is determining the state space. In the simplest A* it's graph node only.
	# In our case, it's graph node AND keys collected.
	# In this conception, there are several concrete goal nodes (any with all keys collected)
	# g(n) distance traveled up to this point 
	# h(n) heuristic: max distance to SOME remaining key
	# this heuristic is admissible: always underestimates true cost
	# open set: unexplored states we can access
	# closed set: states we already accessed (crucially, includes keys collected)
	# should work!
	#
	# One remark: in fact doing this with the reduction to keys and distances allows inadmissable states
	# for example, if you have to go through a to get b, that isn't reflected in choosing to go from c to b.
	# but, in cases where you're forced like that, it may not affect the final step count anyway.

	## Minor optimization: convert all dependencies to lower case, sets
	for k_name in final_keys_d["start"].keys():
		final_keys_d["start"][k_name]["dependencies"] = set( [k.lower() for k in final_keys_d["start"][k_name]["dependencies"]] )

	all_keys = set(final_keys_d.keys())
	all_keys_nostart = all_keys - set(['start'])

	(best_path, best_dist) = A_Star(('start', frozenset(['start'])), final_keys_d, all_keys)

	print(f"The best path was: {best_path}")
	print(f"The minimum number of required steps to collect all keys is: {best_dist}")

	# After optimizations, runtime down to 45 sec.
	# The best path was: ['start', 'r', 't', 'k', 'b', 'e', 'm', 'c', 'a', 'p', 'f', 'o', 'h', 'v', 'j', 'y', 'w', 'g', 'q', 'u', 'i', 'x', 'd', 'l', 'n', 's', 'z']
	# The minimum number of required steps to collect all keys is: 2946

	### End of real A* solution

	return 0

def h(key_name, to_collect, keys_d):
	
	## greedy, door-unaware path to collecting all remaining keys
	## no. greedy might not be right.
	## mm. might need instead an A* optimal path to collecting all remaining keys, regardless of doors.
	## well then. this is double A*. but then what is the h for the inner a*? 
	## yikes
	## ok: how about, distance to the farthest single key
	## that definitely is a lower bound for the distance to cover. just maybe too low. 
	## yeah, I think that's it.
	## well let's start with that. simplest is best, go to a more complicated heuristic if we have to.
	if len(to_collect)==0:
		return 0

	return max( [keys_d[key_name][target]['dist'] for target in to_collect] )

# based on Wikipedia A* pseudocode
def reconstruct_path(cameFrom, current_state):
	total_path = [current_state[0]]
	while current_state in cameFrom.keys():
		current_state = cameFrom[current_state]
		total_path.insert(0, current_state[0])
	return total_path

# A* finds a path from start to goal.
# h is the heuristic function. h(n) estimates the cost to reach goal from node n.
def A_Star(start_state, keys_d, all_keys):
	# The set of discovered nodes that may need to be (re-)expanded.
	# Initially, only the start node is known.
	openSet = set([start_state])
	closedSet = set()

	# For node n, cameFrom[n] is the node immediately preceding it on the cheapest path from start to n currently known.
	cameFrom = dict()

	# For node n, gScore[n] is the cost of the cheapest path from start to n currently known.
	# gScore := map with default value of Infinity
	# gScore[start] := 0
	gScore = dict()
	# for key_name in all_keys:
	# 	gScore[key_name] = np.inf
	gScore[start_state] = 0

	# For node n, fScore[n] := gScore[n] + h(n).
	# fScore := map with default value of Infinity
	# fScore[start] := h(start)
	fScore = dict()
	# for key_name in all_keys:
	# 	fScore[key_name] = np.inf
	fScore[start_state] = h(start_state[0], all_keys - start_state[1], keys_d)

	while len(openSet)>0:
		#current := the node in openSet having the lowest fScore[] value
		least_score = np.inf
		least_node = None
		for state in openSet:
			if fScore[state] < least_score:
				least_score = fScore[state]
				least_state = state
		current_state = least_state

		if all_keys_collected(current_state, all_keys):
			full_path = reconstruct_path(cameFrom, current_state)
			return (full_path, gScore[current_state])

		# print(f"About to remove {current_state} from openSet {openSet}")
		closedSet.add(current_state)
		openSet.remove(current_state)

		collected = current_state[1]
		to_collect = all_keys - collected
		neighbors = get_unblocked_neighbors(keys_d, to_collect, collected, closedSet)

		# print(f"Evaluating state {current_state} with neighbors {neighbors}")

		for neighbor_state in neighbors:
			# d(current,neighbor) is the weight of the edge from current to neighbor
			# tentative_gScore is the distance from start to the neighbor through current
			tentative_gScore = gScore[current_state] + keys_d[current_state[0]][neighbor_state[0]]['dist']

			if neighbor_state not in gScore.keys():
				gScore[neighbor_state] = np.inf

			if tentative_gScore < gScore[neighbor_state]:
				# This path to neighbor is better than any previous one. Record it!
				cameFrom[neighbor_state] = current_state # only recording the key name path
				gScore[neighbor_state] = tentative_gScore
				fScore[neighbor_state] = gScore[neighbor_state] + h(neighbor_state[0], to_collect - {neighbor_state[0]}, keys_d)
				if neighbor_state not in openSet:
					openSet.add(neighbor_state)

	# Open set is empty but goal was never reached
	return False


def get_unblocked_neighbors(keys_d, to_collect, collected, closedSet):

	unblocked = [k_name for k_name in to_collect if keys_d["start"][k_name]["dependencies"].issubset( collected )]
	# unblocked = frozenset([k_name for k_name in to_collect if is_unblocked(k_name, keys_d, collected, known_unblocked_keys)])

	neighbor_candidates = [(ub, frozenset(collected.union(ub))) for ub in unblocked]
	# neighbor_candidates = [(ub, frozenset(collected.union(ub)), unblocked) for ub in unblocked]

	neighbor_states = [candidate for candidate in neighbor_candidates if not candidate in closedSet]

	return neighbor_states


def is_unblocked(k_name, keys_d, collected, known_unblocked_keys):

	if k_name in known_unblocked_keys:
		return True

	return keys_d["start"][k_name]["dependencies"].issubset( collected )



def all_keys_collected(current_state, all_keys):

	keys_collected = current_state[1]

	return keys_collected == all_keys

# make sure to send a COPY of keys_d in here if we don't want the main version modified
def dijkstra(arr, x_start, y_start, keys_d):
	# Keep track of dependencies:
	# Keep track of each door we pass as we go along. Store in node.
	# In the min step of dijkstra, if we replace the min dist for a node, also replace the dependency list.
	# That way each node has a record of the keys needed to get there from the middle.

	arr_visited = np.zeros(shape=arr.shape)
	arr_visited[y_start,x_start] = 1

	arr_minDist = np.ones(shape=arr.shape) * np.inf
	arr_minDist[y_start,x_start] = 0

	keys = set(keys_d.keys())
	doors = set([v.upper() for v in keys_d.keys()])
	doors_passed = set()

	dijkstra_rec(arr, x_start, y_start, arr_visited, arr_minDist, keys_d, keys, doors, doors_passed)

	for c in keys:
		keys_d[c]["dist"] = int( arr_minDist[ keys_d[c]['y'], keys_d[c]['x'] ] )
 
	return keys_d

def dijkstra_rec(arr, x, y, arr_visited, arr_minDist, keys_d, keys, doors, doors_passed):

	c = arr[y,x]
	if c in doors:
		doors_passed.add(c)

	dist_here = arr_minDist[y,x]
	dist_nbhrs_tmp = dist_here + 1

	neighbors = get_neighbors(arr, x, y)

	for n in neighbors:
		xx = n[0]
		yy = n[1]

		c = arr[yy,xx]

		if dist_nbhrs_tmp < arr_minDist[yy,xx]:

			arr_minDist[yy,xx] = dist_nbhrs_tmp

			c = arr[yy,xx]
			if c in keys:
				keys_d[c]["dependencies"] = deepcopy( doors_passed )
			if c=='@':
				keys_d['start']["dependencies"] = deepcopy( doors_passed )

	arr_visited[y,x]=1

	unvisited_nhbrs = get_unvisited_neighbors(neighbors, arr_visited, arr_minDist) # return in ascending order of distance, so we can iterate

	for next_nhbr in unvisited_nhbrs:

		next_x = next_nhbr[0][0]
		next_y = next_nhbr[0][1]

		dijkstra_rec(arr, next_x, next_y, arr_visited, arr_minDist, keys_d, keys, doors, deepcopy( doors_passed ) ) # arr_minDist will be modified sequentially

	return True

def get_neighbors(arr, x, y):

	prospects = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]

	neighbors = []

	for p in prospects:

		xx = p[0]
		yy = p[1]

		if xx<0 or xx>=arr.shape[1]:
			continue

		if yy<0 or yy>=arr.shape[0]:
			continue

		c = arr[yy,xx]

		if c!='#':
			neighbors.append(p)

	return neighbors

def get_unvisited_neighbors(neighbors, arr_visited, arr_minDist):

	aug = []

	for n in neighbors:

		x = n[0]
		y = n[1]

		if arr_visited[y,x]==1:
			continue # visted

		aug.append( [(x,y), arr_minDist[y,x] ] )

	aug = sorted(aug, key = lambda a: a[1])

	return aug

def print_map(arr):

	for i in range(arr.shape[0]):
		print("".join(arr[i,:]))

	return 0

def debug(s):
	print(s)
	return None

if __name__=="__main__":

	run_main()