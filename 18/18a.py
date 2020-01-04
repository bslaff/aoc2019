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
	#### Note: based on that assumption we could/should do DFS instead of Dijkstra. But will implement Dijkstra for practice, and just in case.
	## Once we have this, do a tree search:
	## From current position, note distance traveled on the path up to this point
	## Compute distance to each other key and tentative distance that way (with dependencies accounted for)
	## Recurse, computing a tree of paths towards the goal of collecting all keys (visiting all key positions)
	## Output the path with the smallest overall distance.
	## Will that brute force work memory-wise? maybe. Might need heuristic to kick out bad paths.

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

	# print("start position: start")
	# for c in sorted( final_keys_d['start'].keys() ):
	# 	print( f"{c}: {final_keys_d['start'][c]['dist']}, {final_keys_d['start'][c]['dependencies']}" )

	# print("start position: k")
	# for c in sorted( final_keys_d['k'].keys() ):
	# 	print( f"{c}: {final_keys_d['k'][c]['dist']}, {final_keys_d['k'][c]['dependencies']}" )

	# seems right
	# now we have the min distance from each node to each other node, and all dependencies
	# so this is now path search part 2

	# algorithm: start at START. for each possible (non-blocked) move, add distance from START and continue
	# another recursive guy
	# at each stage: cross off dependencies as they are satisfied. thus each path needs its own set of keys collected to expand.
	# each stage also needs its own copy of keys to get, strike each one off after visiting
	# final_keys_d is read-only, don't need to copy it

	# to_collect = set(final_keys_d.keys())
	# collected = set()

	# min_steps = collect_keys(final_keys_d, "start", to_collect, collected, 0)

	# print(f"The minimum number of required steps to collect all keys is: {min_steps}")

	# this almost works, but brute force dfs explodes combinatorally starting with test 4
	# we need to do this dynamically
	# first: distance to the end if we only need one more
	# next: distance to the end if we only need two more; use what we learned from one more
	# etc
	# final step: go from START to any of the keys (start should be excluded before this step)

	## Check results of first part, debug
	# start_node="g"
	# keys_ss = sorted(final_keys_d[start_node].keys())
	# for c in keys_ss:
	# 	print(f"{c}: {final_keys_d[start_node][c]['dist']}, {final_keys_d[start_node][c]['dependencies']}")
	# exit()
	## Looks good now

	### Unsuccessful: dynamic programming approach. Works for examples, but does not scale to real input.

	# all_keys = list(final_keys_d.keys())
	# all_keys_no_start = all_keys.copy()
	# all_keys_no_start.remove("start")
	# all_keys_no_start_set = set(all_keys_no_start)

	# print(f"all_keys_no_start {all_keys_no_start}")

	# master_d = dict()
	# p = len( all_keys_no_start )
	# r = p-1
	# while r>0:
	# 	print(f"generating for p, r = {p}, {r}")
	# 	collected_generator = itertools.combinations(all_keys_no_start, r)
	# 	while True:
	# 		try:
	# 			collected = next(collected_generator)
	# 			collected = set(collected)
	# 			to_collect = all_keys_no_start_set - collected
	# 			to_collect_frozen = frozenset(to_collect)

	# 			master_d[to_collect_frozen]=dict() # might need to limit the size of this guy
	# 			for key_name in to_collect:
	# 				# print(f"KEY_NAME {key_name}, TO_COLLECT {to_collect}, COLLECTED {collected}")
	# 				min_steps = collect_keys(final_keys_d, key_name, to_collect.copy(), collected.copy(), 0, master_d)
	# 				master_d[to_collect_frozen][key_name]=min_steps # min steps to collect remaining keys from node key_name

	# 		except StopIteration:
	# 			break
	# 	r-=1

	# # Now do the last step: from start, using master_d
	# min_steps = collect_keys(final_keys_d, "start", set(all_keys).copy(), set().copy(), 0, master_d)
	### End of unsuccessful dynamic programming approach. Neat idea though.

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

	all_keys = set(final_keys_d.keys())
	all_keys_nostart = all_keys - set(['start'])

	(best_path, best_dist) = A_Star(('start', frozenset(['start'])), final_keys_d, all_keys)

	print(f"The best path was: {best_path}")
	print(f"The minimum number of required steps to collect all keys is: {best_dist}")

	# Takes like 5-10 minutes to run. Output:
	# The best path was: ['start', 'r', 't', 'k', 'b', 'e', 'm', 'c', 'a', 'p', 'f', 'o', 'h', 'v', 'j', 'y', 'w', 'g', 'q', 'u', 'i', 'x', 'd', 'l', 'n', 's', 'z']
	# The minimum number of required steps to collect all keys is: 2946

	### End of real A* solution

	##### The following modification doesn't work and wasn't used in the end.
	### Need to modify A* for this.
	# A* keeps shortening the number of nodes we've traversed in order to get the least-distance path to the given node
	# That isn't what we want. We have to pick up every key!
	# But we should still be able to do some kind of best-first search. Like:
	#
	# Start at the start node. Consider all neighbors.
	# Each time after we extend, we check whether some path has collected all keys/nodes. If yes then we are done.
	# If not, we choose some path to extend.
	# That path should be the best according to g+h, as before.
	# Computationally hard to keep track of next best path to extend, especially as number of paths increases. hmm.
	# Only ever hang on to top 1000 paths? Messy, but might work
	# Is there a better way? probably, but need a working way first.
	##### End of modification that didn't work

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
				fScore[neighbor_state] = gScore[neighbor_state] + h(current_state[0], to_collect, keys_d)
				if neighbor_state not in openSet:
					openSet.add(neighbor_state)

	# Open set is empty but goal was never reached
	return False


def get_unblocked_neighbors(keys_d, to_collect, collected, closedSet):

	unblocked = set()

	for k_name in to_collect:

		deps = keys_d["start"][k_name]["dependencies"]

		is_unblocked = all( [k.lower() in collected for k in deps] )

		if is_unblocked:

			unblocked.add(k_name)

	neighbor_states = set()

	for ub in unblocked:

		temp_set = set(collected.copy())
		temp_set.add(ub)

		neighbor_candidate = (ub, frozenset(temp_set))

		if not neighbor_candidate in closedSet:

			neighbor_states.add(neighbor_candidate)

	return neighbor_states


def all_keys_collected(current_state, all_keys):

	keys_collected = current_state[1]

	return keys_collected == all_keys


### WRONG. 
# A* finds a path from start to goal.
# h is the heuristic function. h(n) estimates the cost to reach goal from node n.
# def A_Star_modified(start, keys_d, all_keys):
# 	# The set of discovered nodes that may need to be (re-)expanded.
# 	# Initially, only the start node is known.

# 	MAX_NPATHS = 1000

# 	# all_paths is a list of triples: path-list, path distance g, and f (= g plus h)
# 	PATH_IDX=0
# 	G_IDX=1
# 	F_IDX=2
# 	all_paths = [([start], 0, h(start, all_keys - set([start]), keys_d))]

# 	while True:

# 		# control path explosion
# 		# if block below is commented, result should be optimal
# 		while len(all_paths)>MAX_NPATHS:
# 			fscores = [p[F_IDX] for p in all_paths]
# 			i = np.argmax(fscores)
# 			del all_paths[i]

# 		fscores = [p[F_IDX] for p in all_paths]
# 		i = np.argmin(fscores)

# 		path_tup = copy( all_paths[i] )
# 		del all_paths[i]

# 		path = path_tup[PATH_IDX]
# 		path_set = set(path)
# 		g = path_tup[G_IDX]
# 		f = path_tup[F_IDX]

# 		to_collect = all_keys - path_set
# 		collected = path_set
# 		neighbors = get_unblocked_neighbors(keys_d, to_collect, collected)

# 		if len(neighbors)==0:
# 			return (path, g)

# 		current_state = path[-1]

# 		for neighbor in neighbors:
# 			new_g = g + keys_d[current_state][neighbor]['dist']
# 			new_f = new_g + h(neighbor, to_collect, keys_d)

# 			new_path_tup = (path+[neighbor], new_g, new_f )

# 			all_paths.append( new_path_tup )

	# Open set is empty but goal was never reached
	# return False


# def get_next_unblocked_target_keys(key_name, final_keys_d, to_collect, collected):

# 	unblocked = set()

# 	for k_name in to_collect:

# 		deps = final_keys_d["start"][k_name]["dependencies"]

# 		is_unblocked = all( [k.lower() in collected for k in deps] )

# 		if is_unblocked:

# 			unblocked.add(k_name)

# 	return unblocked

### Dynamic thingy that didn't work
# def collect_keys(final_keys_d, key_name, to_collect, collected, traveled, master_d):

# 	# print(f"key {key_name}, to_collect {to_collect}, collected {collected}")

# 	# dynamic guy. hopefully not to bad with memory
# 	to_collect_frozen = frozenset(to_collect)
# 	if to_collect_frozen in master_d.keys():
# 		if key_name in master_d[to_collect_frozen].keys():
# 			# print("USING THE DUDE")
# 			return master_d[to_collect_frozen][key_name]

# 	to_collect.remove(key_name)
# 	collected.add(key_name)

# 	if len(to_collect)==0:
# 		return traveled

# 	possible = get_next_unblocked_target_keys(key_name, final_keys_d, to_collect, collected)

# 	path_distances = []

# 	for next_key_name in possible:

# 		dist_to_key = final_keys_d[key_name][next_key_name]["dist"]

# 		path_dist = traveled + dist_to_key + collect_keys(final_keys_d, next_key_name, to_collect.copy(), collected.copy(), 0, master_d)

# 		path_distances.append(path_dist)

# 	if len(path_distances)==0:
# 		return np.inf

# 	optimal_dist = min(path_distances)

# 	return optimal_dist

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