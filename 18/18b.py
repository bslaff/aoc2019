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

	## strategy: first do dijkstra from each key to ALL other keys. Get min distance from each key to each other key. also from each start position to each key.
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

	start_positions = np.argwhere(arr_visited)

	for i in range(np.argwhere(arr_visited).shape[0]):

		start_pos = start_positions[i]

		k = str(i)

		keys_d[k] = dict()
		keys_d[k]['x'] = start_pos[1]
		keys_d[k]['y'] = start_pos[0]
		keys_d[k]['dependencies'] = set()

		arr[ keys_d[k]['y'], keys_d[k]['x'] ] = str(k)

	final_keys_d = dict()
	
	for c in keys_d.keys():
		x = keys_d[c]['x']
		y = keys_d[c]['y']
		# print(f"x {x}, y {y}")
		final_keys_d[c] = dijkstra(arr, x, y, deepcopy( keys_d ) )

	starts = ['0', '1', '2', '3']
	### Diagnostic, check the keys
	#for start in starts:
	# 	print(f"start {start}")
	# 	for key_name in final_keys_d[start].keys():
	# 		print(f"{key_name}: {final_keys_d[start][key_name]['dist']}, {final_keys_d[start][key_name]['dependencies']}")

	# 	print()
	# exit()
	### End diagnostic

	### Real solution: A*
	# See 18a for more notes.
	# now each "state" includes four positions (in order), but is not otherwise different

	## Minor optimization: convert all dependencies to lower case, sets
	for start in starts:
		for k_name in final_keys_d[start].keys():
			final_keys_d[start][k_name]["dependencies"] = set( [k.lower() for k in final_keys_d[start][k_name]["dependencies"]] )

	all_keys = set(final_keys_d.keys())

	(best_path, best_dist) = A_Star(('0','1','2','3', frozenset(['0','1','2','3'])), final_keys_d, all_keys)

	print(f"The best path was: {best_path}")
	print(f"The minimum number of required steps to collect all keys is: {best_dist}")

	# Runtime 10 sec.
	### End of real A* solution

	return 0

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
	fScore[start_state] = h(start_state, all_keys - start_state[-1], keys_d)

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
			print(f"YAY! All keys collected.")
			full_path = reconstruct_path(cameFrom, current_state)
			return (full_path, gScore[current_state])

		# print(f"About to remove {current_state} from openSet {openSet}")
		closedSet.add(current_state)
		openSet.remove(current_state)

		collected = current_state[-1]
		to_collect = all_keys - collected

		current_positions = [current_state[0], current_state[1], current_state[2], current_state[3]]
		neighbors = get_unblocked_neighbors(current_positions, keys_d, to_collect, collected, closedSet)

		# print(f"Evaluating state {current_state} with neighbors {neighbors}")
		# print(f"Evaluating state: {current_state}")
		# for n in neighbors:
		# 	print(f"Neighbor: {n}")
		# print(f"openSet: {openSet}")
		# exit()

		for neighbor_state in neighbors:
			# d(current,neighbor) is the weight of the edge from current to neighbor
			# tentative_gScore is the distance from start to the neighbor through current

			# tentative_gScore = gScore[current_state] + keys_d[current_state[0]][neighbor_state[0]]['dist']
			tentative_gScore = gScore[current_state] + get_state_dist(current_state, neighbor_state, keys_d)

			if neighbor_state not in gScore.keys():
				gScore[neighbor_state] = np.inf

			if tentative_gScore < gScore[neighbor_state]:
				# This path to neighbor is better than any previous one. Record it!
				cameFrom[neighbor_state] = current_state # only recording the key name path
				gScore[neighbor_state] = tentative_gScore

				to_collect_neighbor = to_collect - {neighbor_state[0], neighbor_state[1], neighbor_state[2], neighbor_state[3]}

				fScore[neighbor_state] = gScore[neighbor_state] + h(neighbor_state, to_collect_neighbor, keys_d)
				if neighbor_state not in openSet:
					openSet.add(neighbor_state)

	# Open set is empty but goal was never reached
	return False


def get_state_dist(current_state, neighbor_state, keys_d):

	for i in [0, 1, 2, 3]:
		if current_state[i]!=neighbor_state[i]:
			return keys_d[current_state[i]][neighbor_state[i]]['dist']

	# Yikes!
	return False


def get_unblocked_neighbors(current_positions, keys_d, to_collect, collected, closedSet):

	starts = ['0', '1', '2', '3']
	cp = current_positions

	neighbor_states = []

	for i in range(len(starts)):

		start = starts[i]

		unblocked = [k_name for k_name in to_collect if keys_d[start][k_name]["dependencies"].issubset( collected ) and not np.isinf(keys_d[start][k_name]["dist"])]

		# todo improve this
		if i==0:
			neighbor_candidates = [(ub, cp[1], cp[2], cp[3], frozenset(collected.union(ub))) for ub in unblocked]
		elif i==1:
			neighbor_candidates = [(cp[0], ub, cp[2], cp[3], frozenset(collected.union(ub))) for ub in unblocked]
		elif i==2:
			neighbor_candidates = [(cp[0], cp[1], ub, cp[3], frozenset(collected.union(ub))) for ub in unblocked]
		elif i==3:
			neighbor_candidates = [(cp[0], cp[1], cp[2], ub, frozenset(collected.union(ub))) for ub in unblocked]

		neighbor_states += [candidate for candidate in neighbor_candidates if not candidate in closedSet]

	return neighbor_states


def h(base_state, to_collect, keys_d):
	
	## sum of max individual distances within each quadrant
	## for more details see 18a
	total = 0
	for key_name in base_state[:4]:

		eligible = [target for target in to_collect if not np.isinf(keys_d[key_name][target]['dist'])]

		if len(eligible)==0:
			continue

		total += max( [keys_d[key_name][target]['dist'] for target in eligible] )

	return total

# based on Wikipedia A* pseudocode
def reconstruct_path(cameFrom, current_state):
	cs = current_state
	total_path = [(cs[0], cs[1], cs[2], cs[3])]
	while cs in cameFrom.keys():
		cs = cameFrom[cs]
		total_path.insert(0, (cs[0], cs[1], cs[2], cs[3]))
	return total_path


def all_keys_collected(current_state, all_keys):

	keys_collected = current_state[-1]

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
	doors = set([maybe_upper(v) for v in keys_d.keys()])
	doors_passed = set()

	dijkstra_rec(arr, x_start, y_start, arr_visited, arr_minDist, keys_d, keys, doors, doors_passed)

	for c in keys:
		keys_d[c]["dist"] = maybe_int( arr_minDist[ keys_d[c]['y'], keys_d[c]['x'] ] )
 
	return keys_d

def maybe_upper(v):

	try:
		x = v.upper()
		return x
	except:
		return v

def maybe_int(v):

	try:
		x = int(v)
		return x
	except:
		return v

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